class Reader:

    def __init__(self, filepath):
        self.filepath = filepath
        self.max_line_number = self.count_lines(filepath)
        self.file = open(self.filepath, 'r')
        self.line = ""
        self.line_number = 0
        self.index = 0
        self.read_line()
            
    def get_current_line_number(self):
        return self.line_number

    def read_line(self):
        try:
            self.line = self.file.readline()
        except:
            print("tried to read non-existant line")
            self.line = ""
        self.line_number = min(self.line_number + 1, self.max_line_number) 
        self.index = 0
    


    def read_char(self):
        if self.line == '':
            self.index += 1
            self.file.close()
            return ''
        elif self.index >= len(self.line):
            self.read_line()
            return self.read_char()
        else:
            result = self.line[self.index]
            self.index += 1
            return result
        
    def unread_char(self):
        if self.index == 0:
            print(f"cannot unread char at start of line {self.line_number}")
            return None
        
        self.index -= 1
        return 0
    
    def count_lines(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                line_count = 0
                while True:
                    char = file.read(1)
                    if not char:
                        break
                    if char == '\n':
                        line_count += 1
                
                return line_count+1
        except FileNotFoundError:
            print("File not found.")
            return -1
        except Exception as e:
            print(f"An error occurred: {e}")
            return -1