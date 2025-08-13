# this class is responsible for generating the intermediate code

ICG_OUTPUT_PATH = "./output.txt"

INT_SIZE = 4 #4 Bytes

RETURN_VALUE_ADDRESS = 0
FUNCTION_RETURN_ADDRESS = 4
DEFAULT_RETURN_ADDRESS_LINE = 1 
OUTPUT_VAR = "output_var"

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
        self.rt_stack = []
        # --- Flags ---
        self.force_declare = False
        self.no_push = False
        self.function_scope = False
        self.current_type = None
        self.first_func = True
        self.array_param = False
        
        self.main_is_found = False
        # --- initialize addresses for functions ---
        self.program_block.new_command("ASSIGN", "#0", f"{RETURN_VALUE_ADDRESS}")
        self.program_block.skip_line() #DEFAULT_RETURN_ADDRESS_LINE

        self.output_return_address = self.env.temp_address()
        # --- Reserve line MAIN_JUMP_LINE for the jump to main ---
        # self.program_block.skip_line()


    def take_action(self, action, input_str=None):
        if action == "ASSIGN":
            top = self.sp()
            arg1 = self.semantic_stack[top]
            arg2 = self.semantic_stack[top - 1]
            self.program_block.new_command("ASSIGN", arg1, arg2)
            self.pop(2)
            self.semantic_stack.append(arg2)

        elif action == "OPERATE":
            top = self.sp()
            arg2 = self.semantic_stack[top]
            symb = self.semantic_stack[top - 1]
            arg1 = self.semantic_stack[top - 2]
            result_addr = str(self.env.temp_address())

            if symb == "+":
                command_type = "ADD"
            elif symb == "-":
                command_type = "SUB"
            elif symb == "*":
                command_type = "MULT"
            else:
                raise Exception(f"{symb} was not a operator")

            self.program_block.new_command(command_type, arg1, arg2, result_addr)
            self.pop(3)
            self.semantic_stack.append(result_addr)

        elif action == "COMPARE":
            top = self.sp()
            arg2 = self.semantic_stack[top]
            symb = self.semantic_stack[top - 1]
            arg1 = self.semantic_stack[top - 2]
            result_addr = str(self.env.temp_address())

            if symb == "==":
                command_type = "EQ"
            elif symb == "<":
                command_type = "LT"
            else:
                raise Exception(f"{symb} was not a relop")

            self.program_block.new_command(command_type, arg1, arg2, result_addr)
            self.pop(3)
            self.semantic_stack.append(result_addr)

        elif action == "NEG":
            arg = self.semantic_stack.pop()
            result_addr = str(self.env.temp_address())
            self.program_block.new_command("SUB", "#0", arg, result_addr)
            self.semantic_stack.append(result_addr)

        elif action == "PID":
            self.last_seen_id = input_str
            address = str(self.env.get_address(input_str, self.force_declare))

            if input_str in self.function_table:  # is a function
                function_description = self.function_table[input_str]
                self.call_stack.append((input_str, function_description))

            if not self.no_push or self.function_scope:
                self.semantic_stack.append(address)

        elif action == "LIST_ACC":
            top = self.sp()
            index_addr_str = self.semantic_stack[top]
            list_addr_str = self.semantic_stack[top - 1]
            tmp_addr = str(self.env.temp_address())
            self.program_block.new_command("MULT", index_addr_str, "#4", tmp_addr)
            result_addr = tmp_addr
            self.program_block.new_command("ADD", list_addr_str, tmp_addr, result_addr)
            self.pop(2)
            self.semantic_stack.append("@" + result_addr)

        elif action == "IMM":
            self.semantic_stack.append("#" + input_str)

        elif action == "SYMB":
            self.semantic_stack.append(input_str)

        elif action == "POP":
            self.pop()


        elif action == "SAVE_TYPE":
            self.current_type = input_str

        elif action == "VOID_CHECK":
            if input_str == "void":
                self.current_type = "void"

        elif action == "VOID_CHECK_THROW":
            if self.current_type == "void":
                pass

        elif action == "SET_FORCE_DECLARE":
            self.force_declare = True

        elif action == "UNSET_FORCE_DECLARE":
            self.force_declare = False

        elif action == "SET_NO_PUSH":
            self.no_push = True

        elif action == "UNSET_NO_PUSH":
            self.no_push = False

        elif action == "PNUM":
            self.semantic_stack.append(f"#{input_str}")

        elif action == "DECLARE_ARRAY":
            size_str = self.semantic_stack.pop()
            size = int(size_str[1:])
            start_of_array = str(self.env.temp_address())
            array_address = str(self.env.get_address(self.last_seen_id))
            self.program_block.new_command("ASSIGN", f"#{start_of_array}", array_address)
            if size > 1:
                self.env.last_address += (size - 1) * INT_SIZE

        elif action == "ARRAY_PARAM":
            self.array_param = True


        elif action == "OPEN_SCOPE":
            if self.function_scope:
                self.function_scope = False
            else:
                self.env.open_scope()

        elif action == "CLOSE_SCOPE":
            self.env.close_scope()
            self.function_scope = False


        elif action == "DECLARE_FUN":
            if self.first_func:
                self.main_jump_line = self.program_block.get_line_number()
                self.program_block.skip_line()
                self.first_func = False
                self.generate_output_func()
            self.current_function = self.last_seen_id
            func_start_line = self.program_block.get_line_number()

            if self.current_function == 'main' and not self.main_is_found:
                self.program_block.write_command_at(self.main_jump_line, "JP", func_start_line)
                self.main_is_found = True

            self.rt_stack.append(self.env.temp_address())
            self.function_table[self.current_function] = {
                'address': self.program_block.get_line_number(),
                'params': [],
                'return_address': self.rt_stack[-1]
            }
            func_var_addr = self.env.get_address(self.last_seen_id)
            self.program_block.new_command("ASSIGN", f"#{self.program_block.get_line_number()}", func_var_addr)

        elif action == "SET_FUNCTION_SCOPE":
            self.function_scope = True

        elif action == "POP_PARAM":
            param_addr = self.semantic_stack.pop()
            if self.current_function:
                self.function_table[self.current_function]['params'].append({
                    'name': self.last_seen_id,
                    'addr': param_addr,
                    'is_array': self.array_param
                })
                self.array_param = False

        elif action == "SET_RETURN_VALUE":
            return_val = self.semantic_stack.pop()
            self.program_block.new_command("ASSIGN", return_val, "0")

        elif action == "JUMP_BACK":
            rt = self.rt_stack[-1]
            self.program_block.new_command("JP", f"@{rt}")
            self.current_function = None
            self.function_scope = False

        elif action == "ELSE_JUMP":
            condition = self.semantic_stack.pop()
            jpf_addr = self.semantic_stack.pop()
            jp_addr = self.program_block.get_line_number()
            self.program_block.skip_line()
            self.semantic_stack.append(jp_addr)
            self.program_block.write_command_at(jpf_addr, "JPF", condition, self.program_block.get_line_number())

        elif action == "END_IF_JUMP":
            jp_addr = self.semantic_stack.pop()
            self.program_block.write_command_at(jp_addr, "JP", self.program_block.get_line_number())

        elif action == "CALL":
            func_name, func_description = self.call_stack.pop()
            func_params = func_description.get("params", [])
            param_index = len(func_params) - 1
            while param_index >= 0:
                param = func_params[param_index]
                param_addr = param["addr"]
                param_input = self.semantic_stack.pop()
                self.program_block.new_command("ASSIGN", param_input, param_addr)
                param_index -= 1

            func_addr = self.semantic_stack.pop()
            func_line = func_description["address"]
            return_addr = self.program_block.get_line_number() + 2
            self.program_block.new_command("ASSIGN", f"#{return_addr}", f"{func_description['return_address']}")
            self.program_block.new_command("JP", func_line)
            temp = str(self.env.temp_address())
            self.program_block.new_command("ASSIGN", f"{RETURN_VALUE_ADDRESS}", temp)
            self.semantic_stack.append(temp)

        elif action == "LABEL":
            self.semantic_stack.append(self.program_block.get_line_number())

        elif action == "SAVE":
            condition = self.semantic_stack.pop()
            self.semantic_stack.append(self.program_block.get_line_number())
            self.program_block.skip_line()
            self.semantic_stack.append(condition)

        elif action == "WHILE":
            condition = self.semantic_stack.pop()
            jpf_addr = self.semantic_stack.pop()
            label = self.semantic_stack.pop()
            self.program_block.new_command("JP", label)
            self.program_block.write_command_at(jpf_addr, "JPF", condition, self.program_block.get_line_number())

        elif action == "START_BREAK_SCOPE":
            self.break_stack.append([])

        elif action == "BREAK":
            if not self.break_stack:
                raise Exception("Break statement outside of a loop.")
            break_addr = self.program_block.get_line_number()
            self.break_stack[-1].append(break_addr)
            self.program_block.skip_line()

        elif action == "HANDLE_BREAKS":
            if not self.break_stack:
                return
            exit_point = self.program_block.get_line_number()
            for break_addr in self.break_stack.pop():
                self.program_block.write_command_at(break_addr, "JP", exit_point)

        elif action in ("START_RHS", "END_RHS"):
            pass

        elif action == "PROGRAM_END":
            last_command, arg1, _, _ = self.program_block.blocks[-1]
            main_rt = self.function_table["main"]["return_address"]
            if last_command == "JP" and arg1 == f"@{str(main_rt)}":
                self.program_block.blocks.pop()
            self.program_block.write_command_at(
                DEFAULT_RETURN_ADDRESS_LINE,
                "ASSIGN",
                f"#{self.program_block.get_line_number()}",
                FUNCTION_RETURN_ADDRESS
            )




    def sp(self):
        return len(self.semantic_stack) - 1

    def pop(self, number=1):
        for _ in range(number):
            if self.semantic_stack:
                self.semantic_stack.pop()

    def generate_output_func(self):
        rt = self.env.temp_address() 
        line = self.program_block.get_line_number()
        self.function_table["output"] = {
                'address': line,
                'params': [],
                'return_address':  rt
            }
        # The address of the function itself (pushed by #PID) is on the stack.
        # Assign the current line number to it, so jumps to the function work.
        func_var_addr = self.env.get_address("output", True)
        self.program_block.new_command("ASSIGN", f"#{line}", func_var_addr)
        self.env.open_scope()
        var_addr = self.env.new_reference(OUTPUT_VAR)
        self.function_table["output"]['params'].append({
                        'name': OUTPUT_VAR,
                        'addr': var_addr,
                        'is_array': False
                    })
        self.env.close_scope()
        self.program_block.new_command("PRINT", var_addr)
        self.program_block.new_command("JP", f"@{rt}")






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
                    a1 = a1 if a1 is not None else " "
                    a2 = a2 if a2 is not None else " "
                    a3 = a3 if a3 is not None else " "
                    f.write(f"{i}\t({ctype}, {a1}, {a2}, {a3} )\n")



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
                current_scope = self.scopes[-1]
                if var_name in current_scope:
                    return current_scope[var_name]
                else:
                    return self.new_reference(var_name)
            else:
                for scope in reversed(self.scopes):
                    if var_name in scope:
                        return scope[var_name]
                
                return self.new_reference(var_name)

        def temp_address(self):
            tmpaddr = self.last_address
            self._go_next_address()
            return tmpaddr
