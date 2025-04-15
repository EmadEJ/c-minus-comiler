class Reader:

    def __init__(self, filepath):
        self.filepath = filepath
        self.file = open(self.filepath, 'r')
        self.line = ""
        self.line_number = 0
        self.index = 0
        self.read_line()

    def get_current_line_number(self):
        return self.line_number

    def read_line(self):
        self.line = self.file.readline()
        self.index = 0
        self.line_number += 1

    def read_char(self):
        if self.line == '':
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