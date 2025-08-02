# this class is responsible for generating the intermediate code

ICG_OUTPUT_PATH = "./output.txt"

INT_SIZE = 4 #4 Bytes

class ICG:
    def __init__(self):
        self.env = self.Environment()
        self.program_block = self.ProgramBlock()

        self.semantic_stack = [] 
            # we put strings in the stack. regular numbers (e.g. 100) means direct addressing
            # for immediate numbers we use #. for example #100.
            # we also can write indirect addressing by putting @ behind numbers. 

    def take_action(self, action, input_str = None):
        match action:
            case "ASSIGN": 
                # arg2 = arg1
                top = self.sp()
                arg1 = self.semantic_stack[top]
                arg2 = self.semantic_stack[top-1]
                self.program_block.new_command("ASSIGN", arg1, arg2)
                self.pop(2)

            case "OPERATE":
                top = self.sp()
                arg2 = self.semantic_stack[top]
                symb = self.semantic_stack[top-1]
                arg1 = self.semantic_stack[top-2]
                result_addr = str(self.env.temp_address())

                match symb:
                    case "+":
                        command_type = "ADD"
                    case "-":
                        command_type = "SUB"
                    case "*":
                        command_type = "MULT"
                    case _:
                        raise Exception(f"{symb} was not a operator")
                
                self.program_block.new_command(command_type, arg1, arg2, result_addr)
                self.pop(3)
                self.semantic_stack.append(result_addr)

            
            case "PID":
                address = str(self.env.get_address(input_str))
                self.semantic_stack.append(address)

            case "LIST_ACC":
                top = self.sp()
                index_addr_str = self.semantic_stack[top]
                list_addr_str = self.semantic_stack[top-1]
                tmp_addr = str(self.env.temp_address())
                self.program_block.new_command("MULT", index_addr_str, "#4", tmp_addr) # tmp <- index * 4
                result_addr = str(self.env.temp_address())
                self.program_block.new_command("ADD",  list_addr_str, tmp_addr, result_addr) # result <- list_addr + index * 4
                self.pop(2)
                self.semantic_stack.append(result_addr)
                
            case "IMM": # maybe this would result in error. then get a temp address and put number in the address and push the address
                immediate_str = "#" + input_str
                self.semantic_stack.append(immediate_str) 

            case "SYMB":
                self.semantic_stack.append(input_str)

            case "COMPARE":
                top = self.sp()
                arg2 = self.semantic_stack[top]
                symb = self.semantic_stack[top-1]
                arg1 = self.semantic_stack[top-2]
                result_addr = str(self.env.temp_address())

                match symb:
                    case "==":
                        command_type = "EQ"
                    case "<":
                        command_type = "LT"
                    case _:
                        raise Exception(f"{symb} was not a relop")

                self.program_block.new_command(command_type, arg1, arg2, result_addr)

                self.pop(3)
                self.semantic_stack.append(result_addr)

            case "NEG":
                top = self.sp()
                arg = self.semantic_stack[top]
                result_addr = str(self.env.temp_address())
                self.program_block.new_command("SUB", "#0", arg, result_addr) #negating
                self.pop()
                self.semantic_stack.append(result_addr)

    
    def sp(self):
        return len(self.semantic_stack) - 1
    def pop(self, number=1):
        for i in range(number):
            self.semantic_stack.pop()

    class ProgramBlock: 
        def __init__(self):
            self.blocks = []

        def new_command(self, command_type, arg1, arg2=None, arg3=None):
            command = (command_type, arg1, arg2, arg3)
            self.blocks.append(command)
        def write_command_at(self, line_number, command_type, arg1, arg2=None, arg3=None):
            command = (command_type, arg1, arg2, arg3)
            self.blocks[line_number] = command
        def skip_line(self, number=1):
            for i in range(number):
                self.blocks.append(None)
        def get_line_number(self):
            return len(self.blocks)
        def save(self):
            with open(ICG_OUTPUT_PATH, "w", encoding='utf-8') as icg_output_file:
                line_number = 0 
                for command in self.blocks:
                    command_type, arg1, arg2, arg3 = command 
                    if arg1 == None:
                        icg_output_file.write(f"{line_number}\t({command_type}, , , )")
                    elif arg2 == None:
                        icg_output_file.write(f"{line_number}\t({command_type}, {arg1}, , )")
                    elif arg3 == None:
                        icg_output_file.write(f"{line_number}\t({command_type}, {arg1}, {arg2}, )")
                    else:
                        icg_output_file.write(f"{line_number}\t({command_type}, {arg1}, {arg2}, {arg3})")
                    icg_output_file.write("\n")
                    line_number += 1
        


    class Environment: 
        # this class stores variable addresses and give new addresses
        def __init__(self):
            self.env = {}
            self.last_address = 100 

        def new_reference(self, var_name):
            self.env[var_name] = self.last_address
            self._go_next_address()
            return self.env[var_name]
        
        def temp_address(self):
            tmpaddr = self.last_address
            self._go_next_address()
            return tmpaddr
            
        def get_address(self, var_name):
            if var_name not in self.env:
                self.new_reference(var_name)
                # raise Exception(f"Variable {var_name} not found in environment")
            return self.env[var_name]

        def _go_next_address(self):
            self.last_address += INT_SIZE