# this class is responsible for generating the intermediate code

ICG_OUTPUT_PATH = "./output.txt"

INT_SIZE = 4 #4 Bytes

RETURN_VALUE_ADDRESS = 0
FUNCTION_RETURN_ADDRESS = 4
DEFAULT_RETURN_ADDRESS_LINE = 1 

class ICG:
    def __init__(self):
        self.env = self.Environment()
        self.program_block = self.ProgramBlock()

        self.semantic_stack = []
        # we put strings in the stack. regular numbers (e.g. 100) means direct addressing
        # for immediate numbers we use #. for example #100.
        # we also can write indirect addressing by putting @ behind numbers.

        # --- New attributes for advanced features ---
        self.function_table = {}
        self.break_stack = [] # A stack to manage break statements for nested loops
        self.last_seen_id = None # To remember the name of the last ID encountered
        self.current_function = None # To hold the name of the function being defined
        self.call_stack = [] # A stack to save functions to call (haven't call yet, in the middle of its args)  
        # --- Flags ---
        self.force_declare = False
        self.no_push = False
        self.function_scope = False
        self.current_type = None
        self.is_output_call = False
        self.first_func = True
        self.array_param = False
        
        self.main_is_found = False
        # --- initialize addresses for functions ---
        self.program_block.new_command("ASSIGN", "#0", f"{RETURN_VALUE_ADDRESS}")
        self.program_block.skip_line() #DEFAULT_RETURN_ADDRESS_LINE


        # --- Reserve line MAIN_JUMP_LINE for the jump to main ---
        # self.program_block.skip_line()

        self.generate_output_func()


    def take_action(self, action, input_str = None):
        #=====================================================#
        #                Core Expression Actions              #
        #=====================================================#
        print(f"ACTION: {action:<20} STACK (before): {str(self.semantic_stack):<30} SCOPES: {self.env.scopes}\n{'#'*99}")
        match action:
            case "ASSIGN":
                top = self.sp()
                arg1 = self.semantic_stack[top]
                arg2 = self.semantic_stack[top-1]
                self.program_block.new_command("ASSIGN", arg1, arg2)
                self.pop(2)
                self.semantic_stack.append(arg2)

            case "OPERATE":
                top = self.sp()
                arg2 = self.semantic_stack[top]
                symb = self.semantic_stack[top-1]
                arg1 = self.semantic_stack[top-2]
                result_addr = str(self.env.temp_address())

                match symb:
                    case "+": command_type = "ADD"
                    case "-": command_type = "SUB"
                    case "*": command_type = "MULT"
                    case _: raise Exception(f"{symb} was not a operator")

                self.program_block.new_command(command_type, arg1, arg2, result_addr)
                self.pop(3)
                self.semantic_stack.append(result_addr)

            case "COMPARE":
                top = self.sp()
                arg2 = self.semantic_stack[top]
                symb = self.semantic_stack[top-1]
                arg1 = self.semantic_stack[top-2]
                result_addr = str(self.env.temp_address())

                match symb:
                    case "==": command_type = "EQ"
                    case "<": command_type = "LT"
                    case _: raise Exception(f"{symb} was not a relop")

                self.program_block.new_command(command_type, arg1, arg2, result_addr)
                self.pop(3)
                self.semantic_stack.append(result_addr)

            case "NEG":
                arg = self.semantic_stack.pop()
                result_addr = str(self.env.temp_address())
                self.program_block.new_command("SUB", "#0", arg, result_addr)
                self.semantic_stack.append(result_addr)

            case "PID":
                # Check if the identifier is our special 'output' function.
                if input_str == 'output':
                    self.is_output_call = True
                    # Do not get an address or push anything to the stack for 'output'.
                    # Just set the flag and stop.
                    return

                # If it's not 'output', proceed with the normal PID logic.
                self.last_seen_id = input_str
                address = str(self.env.get_address(input_str, self.force_declare))

                if input_str in self.function_table: # is a function
                    function_description = self.function_table[input_str]
                    self.call_stack.append(function_description) # append this function to call it after arguments are ready

                if not self.no_push or self.function_scope:
                    self.semantic_stack.append(address)
            
            case "LIST_ACC":
                top = self.sp()
                index_addr_str = self.semantic_stack[top]
                list_addr_str = self.semantic_stack[top-1]
                tmp_addr = str(self.env.temp_address())
                self.program_block.new_command("MULT", index_addr_str, "#4", tmp_addr) # tmp <- index * 4
                result_addr = tmp_addr
                self.program_block.new_command("ADD",  list_addr_str, tmp_addr, result_addr) # result <- list_addr + index * 4
                self.pop(2)
                self.semantic_stack.append("@" + result_addr)

            case "IMM":
                self.semantic_stack.append("#" + input_str)

            case "SYMB":
                self.semantic_stack.append(input_str)

            case "POP":
                # Check if this POP is for our special 'output' call.
                if self.is_output_call:
                    # The argument's address/value is on the stack. Pop it.
                    address_to_print = self.semantic_stack.pop()
                    # Generate the PRINT command.
                    self.program_block.new_command("PRINT", address_to_print)
                    # Reset the flag for the next statement.
                    self.is_output_call = False
                else:
                    # If it's not an output call, perform a normal pop for
                    # any other expression whose value isn't used.
                    self.pop()

            #=====================================================#
            #           Declaration and Type Actions              #
            #=====================================================#
            case "SAVE_TYPE":
                self.current_type = input_str

            case "VOID_CHECK":
                if input_str == "void":
                    self.current_type = "void"

            case "VOID_CHECK_THROW":
                if self.current_type == "void":
                    # In a real compiler, this would remove the symbol and raise a semantic error.
                    # print(f"Error: Variable '{self.last_seen_id}' cannot be of type void.")
                    pass

            case "SET_FORCE_DECLARE":
                self.force_declare = True

            case "UNSET_FORCE_DECLARE":
                self.force_declare = False

            case "SET_NO_PUSH":
                self.no_push = True
            
            case "UNSET_NO_PUSH":
                self.no_push = False
            
            case "PNUM":
                self.semantic_stack.append(f"#{input_str}")

            case "DECLARE_ARRAY":
                size_str = self.semantic_stack.pop()
                size = int(size_str[1:])
                start_of_array = str(self.env.temp_address())
                array_address = str(self.env.get_address(self.last_seen_id))                                    
                self.program_block.new_command("ASSIGN", f"#{start_of_array}", array_address)
                if size > 1:
                    self.env.last_address += (size - 1) * INT_SIZE

            case "ARRAY_PARAM":
                self.array_param = True

            #=====================================================#
            #              Scope Management Actions               #
            #=====================================================#
            case "OPEN_SCOPE":
                if self.function_scope:
                    self.function_scope = False
                else:
                    self.env.open_scope()

            case "CLOSE_SCOPE":
                self.env.close_scope()
                self.function_scope = False

            #=====================================================#
            #            Function Definition & Calls              #
            #=====================================================#
            case "DECLARE_FUN":
                if self.first_func:
                    self.main_jump_line = self.program_block.get_line_number()
                    self.program_block.skip_line()
                    self.first_func = False
                self.current_function = self.last_seen_id
                func_start_line = self.program_block.get_line_number()

                if self.current_function == 'main' and not self.main_is_found:
                    self.program_block.write_command_at(self.main_jump_line, "JP", func_start_line)
                    self.main_is_found = True

                # Store function info.
                self.function_table[self.current_function] = {
                    'address': self.program_block.get_line_number(),
                    'params': []
                }
                # The address of the function itself (pushed by #PID) is on the stack.
                # Assign the current line number to it, so jumps to the function work.
                func_var_addr = self.env.get_address(self.last_seen_id)
                self.program_block.new_command("ASSIGN", f"#{self.program_block.get_line_number()}", func_var_addr)

            case "SET_FUNCTION_SCOPE":
                self.function_scope = True

            case "POP_PARAM":
                # In a simple model, parameters are treated like local variables.
                # Their addresses are already allocated. We just record them.
                param_addr = self.semantic_stack.pop()
                if self.current_function:
                    self.function_table[self.current_function]['params'].append({
                        'name': self.last_seen_id,
                        'addr': param_addr,
                        'is_array': self.array_param
                    })
                    self.array_param = False

            case "SET_RETURN_VALUE":
                # Assigns the result of an expression to a conventional return value address (e.g., address 0).
                return_val = self.semantic_stack.pop()
                self.program_block.new_command("ASSIGN", return_val, "0")

            case "JUMP_BACK":
                # Jumps to the return address, which we assume is stored at a conventional address (e.g., 4).
                self.program_block.new_command("JP", f"@{FUNCTION_RETURN_ADDRESS}")
                self.current_function = None
                self.function_scope = False

            case "ELSE_JUMP":
                # This action is called after the "then" block.
                # It back-patches the JPF from the start of the if, and creates a new
                # placeholder for the unconditional JP to jump over the "else" block.
                condition = self.semantic_stack.pop()
                jpf_addr = self.semantic_stack.pop()

                # Create placeholder for the unconditional jump over the else block.
                jp_addr = self.program_block.get_line_number()
                self.program_block.skip_line()
                self.semantic_stack.append(jp_addr)

                # Now that we know where the else block starts (the line after the new JP),
                # we can back-patch the initial JPF.
                self.program_block.write_command_at(jpf_addr, "JPF", condition, self.program_block.get_line_number())

            case "END_IF_JUMP":
                # This action is called after the "else" block.
                # It back-patches the unconditional JP that sits between the "then" and "else" blocks.
                jp_addr = self.semantic_stack.pop()
                self.program_block.write_command_at(jp_addr, "JP", self.program_block.get_line_number())

            # Note: A #CALL action would be needed here to handle the actual function call.
            # Assuming it would be placed after the arguments in the grammar.
            case "CALL":
                if self.is_output_call:
                    return
                func_description = self.call_stack.pop()
                func_params = func_description.get("params", [])

                param_index = len(func_params) - 1
                while param_index >= 0:
                    param = func_params[param_index]
                    param_addr = param["addr"]
                    param_input = self.semantic_stack.pop()
                    self.program_block.new_command("ASSIGN", param_input, param_addr) # TODO: what if its list
                    param_index -= 1


                # This is a simplified call sequence.
                func_addr = self.semantic_stack.pop() # Address of the function to call.
                func_line = func_description["address"]
                return_addr = self.program_block.get_line_number() + 2 # Address to return to.
                
                # 1. Save the return address to our conventional location (address 4).
                self.program_block.new_command("ASSIGN", f"#{return_addr}", f"{FUNCTION_RETURN_ADDRESS}")
                # 2. Jump to the function's code.
                self.program_block.new_command("JP",func_line)
                # 3. After the call returns, move the return value (from address 0) to a new temporary.
                temp = str(self.env.temp_address())
                self.program_block.new_command("ASSIGN", f"{RETURN_VALUE_ADDRESS}", temp)
                self.semantic_stack.append(temp)


            #=====================================================#
            #              Control Flow Actions                   #
            #=====================================================#
            case "LABEL":
                self.semantic_stack.append(self.program_block.get_line_number())

            case "SAVE":
                condition = self.semantic_stack.pop()
                self.semantic_stack.append(self.program_block.get_line_number())
                self.program_block.skip_line()
                self.semantic_stack.append(condition)

            case "WHILE":
                condition = self.semantic_stack.pop()
                jpf_addr = self.semantic_stack.pop()
                label = self.semantic_stack.pop()
                self.program_block.new_command("JP", label)
                self.program_block.write_command_at(jpf_addr, "JPF", condition, self.program_block.get_line_number())

            case "START_BREAK_SCOPE":
                self.break_stack.append([])

            case "BREAK":
                if not self.break_stack:
                    raise Exception("Break statement outside of a loop.")
                # Save the location of the break's jump instruction for later patching.
                break_addr = self.program_block.get_line_number()
                self.break_stack[-1].append(break_addr)
                self.program_block.skip_line()

            case "HANDLE_BREAKS":
                if not self.break_stack: return
                # Get the exit point address (the line after the loop).
                exit_point = self.program_block.get_line_number()
                # Patch all break jumps for the most recent loop.
                for break_addr in self.break_stack.pop():
                    self.program_block.write_command_at(break_addr, "JP", exit_point)
            
            case "START_RHS" | "END_RHS":
                # These are typically used for more advanced semantic analysis (e.g., type checking).
                # For code generation purposes here, they are not needed.
                pass
            case "PROGRAM_END":
                last_command, arg1,_,_ = self.program_block.blocks[-1]
                if last_command == "JP" and arg1 == "@4":
                    self.program_block.blocks.pop()
                self.program_block.write_command_at(DEFAULT_RETURN_ADDRESS_LINE, "ASSIGN", f"#{self.program_block.get_line_number()}", FUNCTION_RETURN_ADDRESS)



    def sp(self):
        return len(self.semantic_stack) - 1

    def pop(self, number=1):
        for _ in range(number):
            if self.semantic_stack:
                self.semantic_stack.pop()

    def generate_output_func(self):
        pass

    #=====================================================#
    #                ProgramBlock Class                   #
    #=====================================================#
    class ProgramBlock:
        def __init__(self):
            self.blocks = []

        def new_command(self, command_type, arg1, arg2=None, arg3=None):
            self.blocks.append((command_type, arg1, arg2, arg3))

        def write_command_at(self, line_number, command_type, arg1, arg2=None, arg3=None):
            self.blocks[line_number] = (command_type, arg1, arg2, arg3)

        def skip_line(self, number=1):
            for _ in range(number): self.blocks.append(None)

        def get_line_number(self):
            return len(self.blocks)

        def save(self):
            with open(ICG_OUTPUT_PATH, "w", encoding='utf-8') as f:
                for i, command in enumerate(self.blocks):
                    if command is None: continue
                    ctype, a1, a2, a3 = command
                    a1 = a1 if a1 is not None else ""
                    a2 = a2 if a2 is not None else ""
                    a3 = a3 if a3 is not None else ""
                    f.write(f"{i}\t({ctype}, {a1}, {a2}, {a3})\n")


    #=====================================================#
    #                 Environment Class                   #
    #=====================================================#
    class Environment:
        def __init__(self):
            self.scopes = [{}]  # A stack of scope dictionaries
            self.address_stack = [] # To save/restore memory counters across scopes
            self.start_address = 100
            self.last_address = self.start_address

        def open_scope(self):
            self.scopes.append({})
            # self.address_stack.append(self.last_address)

        def close_scope(self):
            if len(self.scopes) > 1:
                self.scopes.pop()
                # self.last_address = self.address_stack.pop()

        def _go_next_address(self):
            self.last_address += INT_SIZE

        def new_reference(self, var_name):
            # Creates a new variable in the current (innermost) scope.
            addr = self.last_address
            self.scopes[-1][var_name] = addr
            self._go_next_address()
            return addr

        def get_address(self, var_name, force_declare=False):
            if force_declare:
                # --- Declaration Logic ---
                # We are declaring a new variable. Only check the current scope for redeclaration.
                current_scope = self.scopes[-1]
                if var_name in current_scope:
                    # This is a semantic error: "Variable 'x' redeclared in the same scope."
                    # For now, we'll just return its address.
                    return current_scope[var_name]
                else:
                    # It's a new variable in this scope. Create it.
                    return self.new_reference(var_name)
            else:
                # --- Lookup Logic ---
                # We are using an existing variable. Search from the innermost scope outwards.
                for scope in reversed(self.scopes):
                    if var_name in scope:
                        return scope[var_name]
                
                # This is a semantic error: "Undeclared variable 'x'."
                # To prevent a crash, we'll create it, but a real compiler would raise an error.
                return self.new_reference(var_name)

        def temp_address(self):
            tmpaddr = self.last_address
            self._go_next_address()
            return tmpaddr
