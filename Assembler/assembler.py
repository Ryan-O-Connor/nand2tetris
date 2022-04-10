import os


A_COMMAND = 0
C_COMMAND = 1
L_COMMAND = 2


class Assembler:

    def __init__(self, asm_file):
        self.asm_file = asm_file
        self.hack_file = asm_file.split(".")[0] + ".hack"
        self.parser = Parser(self.asm_file)
        self.coder = Coder()
        self.ST = SymbolTable()
        self.next_RAM_address = 16

    def assemble(self):
        # Main assembly function
        self.parser.preprocess()
        self.first_pass()
        self.second_pass()

    def first_pass(self):
        # Construct symbol table for L_COMMAND's
        self.ROM_address = 0
        while self.parser.hasMoreCommands():
            self.parser.advance()
            if self.parser.commandType() == L_COMMAND:
                symbol = self.parser.symbol()
                self.ST.addEntry(symbol, self.ROM_address)
            else:
                self.ROM_address += 1
        self.parser.reset()

    def second_pass(self):
        # Generate code
        out_file = open(self.hack_file, "wt")
        while self.parser.hasMoreCommands():
            self.parser.advance()
            if self.parser.commandType() == A_COMMAND:
                # A instruction code generation
                abin = "0"
                symbol = self.parser.symbol()
                if symbol.isnumeric():
                    symbol_int = int(symbol)
                elif self.ST.contains(symbol):
                    symbol_int = self.ST.getAddress(symbol)
                else:
                    self.ST.addEntry(symbol, self.next_RAM_address)
                    self.next_RAM_address += 1
                    symbol_int = self.ST.getAddress(symbol)
                abin += bin(symbol_int)[2:].zfill(15)
                out_file.write(abin + "\n")
            elif self.parser.commandType() == C_COMMAND:
                # C instruction code generation
                cbin = "111"
                cbin += self.coder.comp(self.parser.comp())
                cbin += self.coder.dest(self.parser.dest())
                cbin += self.coder.jump(self.parser.jump())
                out_file.write(cbin + "\n")
        out_file.close()


class Parser:

    def __init__(self, asm_file):
        file_handle = open(asm_file, 'rt')
        self.file_lines = file_handle.readlines()
        self.num_lines = len(self.file_lines)
        self.line_index = -1

    def reset(self):
        self.line_index = -1

    def currentCommand(self):
        return self.file_lines[self.line_index]

    def hasMoreCommands(self):
        # Determine if any more nontrivial commands
        if self.line_index < self.num_lines - 1:
            return True
        else:
            return False

    def advance(self):
        # Advance parser to next line
        self.line_index += 1

    def commandType(self):
        # Determine type of command
        cmd = self.currentCommand()
        if cmd[0] == '@':
            return A_COMMAND
        elif cmd[0] == '(' and cmd[-1] == ')':
            return L_COMMAND
        else:
            return C_COMMAND

    def symbol(self):
        # Extract symbol in command
        cmd = self.currentCommand()
        if self.commandType() == A_COMMAND:
            return cmd[1:]
        elif self.commandType() == L_COMMAND:
            return cmd[1:-1]

    def dest(self):
        cmd = self.currentCommand()
        if "=" in cmd:
            return cmd.split("=")[0]
        else:
            return None

    def comp(self):
        cmd = self.currentCommand()
        if "=" in cmd:
            cmd = cmd.split("=")[-1]
        if ";" in cmd:
            cmd = cmd.split(";")[0]
        return cmd
    
    def jump(self):
        cmd = self.currentCommand()
        if ";" in cmd:
            return cmd.split(";")[-1]
        else:
            return None

    def preprocess(self):
        # Remove comments and whitespace
        new_lines = []
        for i, line in enumerate(self.file_lines):
            line = self.strip_comments(line)
            line = self.strip_whitespace(line)
            if len(line) != 0:
                new_lines.append(line)
        self.file_lines = new_lines
        self.num_lines = len(self.file_lines)

    @staticmethod
    def strip_comments(line):
        # Strip all trailing characters following //
        stripped = ''
        prev_ch = ''
        next_ch = ''
        for next_ch in line:
            if next_ch == '/':
                if prev_ch == '/':
                    break
                else:
                    stripped += prev_ch
            else:
                stripped += next_ch
            prev_ch = next_ch
        return stripped

    @staticmethod
    def strip_whitespace(line):
        return line.strip()

    
class Coder:

    def __init__(self):
        self.comp_codes = {"0": "101010", "1": "111111", "-1": "111010", 
                            "D": "001100", "A": "110000", "!D": "001101", "!A": "110001", 
                            "-D": "001111", "-A": "110011", "D+1": "011111", "A+1": "110111", 
                            "D-1": "001110", "A-1": "110010", "D+A": "000010", "D-A": "010011", 
                            "A-D": "000111", "D&A": "000000", "D|A": "010101"}

    def comp(self, code):
        # Computation binary code translation
        if "M" in code:
            code = code.replace("M", "A")
            bin_code = "1"
        else:
            bin_code = "0"
        bin_code += self.comp_codes[code]
        return bin_code

    @staticmethod
    def dest(code):
        # Destination binary code translation
        if code == "M":
            return "001"
        elif code == "D":
            return "010"
        elif code == "MD":
            return "011"
        elif code == "A":
            return "100"
        elif code == "AM":
            return "101"
        elif code == "AD":
            return "110"
        elif code == "AMD":
            return "111"
        else:
            return "000"
    
    @staticmethod
    def jump(code):
        # Jump binary code translation
        if code == "JGT":
            return "001"
        elif code == "JEQ":
            return "010"
        elif code == "JGE":
            return "011"
        elif code == "JLT":
            return "100"
        elif code == "JNE":
            return "101"
        elif code == "JLE":
            return "110"
        elif code == "JMP":
            return "111"
        else:
            return "000"


class SymbolTable:

    def __init__(self):
        self.ST = self.predefined_symbols()

    def addEntry(self, symbol, address):
        self.ST[symbol] = address

    def contains(self, symbol):
        return self.ST.get(symbol) is not None

    def getAddress(self, symbol):
        return self.ST[symbol]

    @staticmethod
    def predefined_symbols():
        # Setup new symbol table with predefined symbols
        ST = {'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4, 
            'SCREEN': 16384, 'KBD': 24567}
        for i in range(16):
            symbol = "R" + str(i)
            ST[symbol] = i
        return ST


if __name__ == '__main__':
    asm_file = 'Pong.asm'
    asm = Assembler(asm_file)
    asm.assemble()
