import sys
import os
import pathlib

from pprint import pprint


C_ARITHMETIC = 0
C_PUSH = 1
C_POP = 2
C_LABEL = 3
C_GOTO = 4
C_IF = 5
C_FUNCTION = 6
C_RETURN = 7
C_CALL = 8


class VMTranslator:

    def __init__(self, path):
        self.vm_files = self.get_vm_files(path)
        self.parsers = [Parser(vm_file) for vm_file in self.vm_files]
        self.asm_file = self.get_asm_name(path)
        self.coder = Coder(self.asm_file)

    def translate(self):
        # Translate each vm command until each parser exhausted
        for parser in self.parsers:
            parser.preprocess()
            while parser.hasMoreCommands():
                parser.advance()
                cmd_type = parser.commandType()
                if cmd_type == C_ARITHMETIC:
                    cmd = parser.arg1()
                    self.coder.writeArithmetic(cmd)
                elif cmd_type == C_PUSH:
                    segment = parser.arg1()
                    index = parser.arg2()
                    self.coder.writePush(segment, index)
                elif cmd_type == C_POP:
                    segment = parser.arg1()
                    index = parser.arg2()
                    self.coder.writePop(segment, index)
                elif cmd_type == C_LABEL:
                    label = parser.arg1()
                    self.coder.writeLabel(label)
                elif cmd_type == C_GOTO:
                    label = parser.arg1()
                    self.coder.writeGoto(label)
                elif cmd_type == C_IF:
                    label = parser.arg1()
                    self.coder.writeIf(label)
                elif cmd_type == C_FUNCTION:
                    name = parser.arg1()
                    num_locals = int(parser.arg2())
                    self.coder.writeFunction(name, num_locals)
                elif cmd_type == C_CALL:
                    name = parser.arg1()
                    num_args = int(parser.arg2())
                    self.coder.writeCall(name, num_args)
                elif cmd_type == C_RETURN:
                    self.coder.writeReturn()
                else:
                    raise RuntimeError("Invalid command type {}".format(cmd))

    @staticmethod
    def get_vm_files(path):
        # Collect paths to all .vm files to be translated
        vm_files = []
        if os.path.isfile(path):
            vm_files.append(path)
        else:
            files = os.listdir(path)
            for dir_file in files:
                if pathlib.Path(dir_file).suffix == '.vm':
                    vm_files.append(os.path.join(path, dir_file))
        return vm_files

    @staticmethod
    def get_asm_name(path):
        # Name of assembly file is parent directory of files
        if os.path.isfile(path):
            file_path = pathlib.Path(path).absolute()
        else:
            files = os.listdir(path)
            for dir_file in files:
                if pathlib.Path(dir_file).suffix == '.vm':
                    file_path = pathlib.Path(os.path.join(path, dir_file)).absolute()
                    break
            else:
                raise RuntimeError("No .vm files in directory {}".format(path))
        out_file_name = str(file_path.parent).split("\\")[-1] + ".asm"
        parent_path = file_path.parent.absolute()
        out_file_path = os.path.join(parent_path, out_file_name)
        return out_file_path
            


class Parser:

    def __init__(self, vm_file):
        file_handle = open(vm_file, 'rt')
        self.file_lines = file_handle.readlines()
        self.num_lines = len(self.file_lines)
        self.line_index = -1
        file_handle.close()

    def reset(self):
        self.line_index = -1

    def currentCommand(self):
        return self.file_lines[self.line_index]

    def tokenizeCommand(self):
        return self.currentCommand().split()

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
        cmd = self.tokenizeCommand()
        cmd_type = cmd[0]
        if cmd_type in ("add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"):
            return C_ARITHMETIC
        elif cmd_type == "push":
            return C_PUSH
        elif cmd_type == "pop":
            return C_POP
        elif cmd_type == "label":
            return C_LABEL
        elif cmd_type == "goto":
            return C_GOTO
        elif cmd_type == "if-goto":
            return C_IF
        elif cmd_type == "function":
            return C_FUNCTION
        elif cmd_type == "call":
            return C_CALL
        elif cmd_type == "return":
            return C_RETURN
        raise SyntaxError("Unidentified command {}".format(cmd_type))

    def arg1(self):
        cmd = self.tokenizeCommand()
        if self.commandType() == C_ARITHMETIC:
            return cmd[0]
        return cmd[1]

    def arg2(self):
        cmd = self.tokenizeCommand()
        return cmd[2]

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

    def __init__(self, output_file):
        self.output_file = output_file
        self.file_handle = open(output_file, 'wt')
        self.binary_ops = ("add", "sub", "and", "or")
        self.comparison_ops = ("eq", "gt", "lt")
        self.unary_ops = ("neg", "not")
        self.current_function = None
        self.label_id = 0
        self.setup()

    def __del__(self):
        self.file_handle.close()

    def setup(self):
        # Bootstrap code
        self.writeValue2Address("SP", 256)
        self.writeAinst("Sys.init")
        self.write("0;JMP")
        # self.writeValue2Address("SP", 317)
        # self.writeValue2Address("LCL", 317)
        # self.writeValue2Address("ARG", 310)
        # self.writeValue2Address("THIS", 3000)
        # self.writeValue2Address("THAT", 4000)
        # self.writeValue2Address("310", 1234)
        # self.writeValue2Address("311", 37)
        # self.writeValue2Address("312", 1000)
        # self.writeValue2Address("313", 305)
        # self.writeValue2Address("314", 300)
        # self.writeValue2Address("315", 3010)
        # self.writeValue2Address("316", 4010)
        # set RAM[0] 317,
        # set RAM[1] 317,
        # set RAM[2] 310,
        # set RAM[3] 3000,
        # set RAM[4] 4000,
        # set RAM[310] 1234,
        # set RAM[311] 37,
        # set RAM[312] 1000,
        # set RAM[313] 305,
        # set RAM[314] 300,
        # set RAM[315] 3010,
        # set RAM[316] 4010,
    
    def write(self, string):
        # Write command to file
        self.file_handle.write(string + "\n")

    # Basic coding functions

    def writeAinst(self, symbol):
        # Write A instruction
        self.write("@" + symbol)

    def writeLinst(self, symbol):
        # Write L instruction
        self.write("(" + symbol + ")")

    def incrementSP(self):
        # Increments the stack pointer
        self.writeAinst("SP")
        self.write("M=M+1")

    def decrementSP(self):
        # Decrements the stack pointer
        self.writeAinst("SP")
        self.write("M=M-1")

    def writeLoadAddress2D(self, address):
        self.writeAinst(address)
        self.write("D=A")

    def writeValue2Address(self, address, value):
        # Write value to address
        self.writeAinst(str(value))
        self.write("D=A")
        self.writeAinst(str(address))
        self.write("M=D")

    def writeD2Pointer(self, pointer):
        # Write value in D register to pointer address
        self.writeLoadPointerAddress(pointer, "A")
        self.write("M=D")

    def writeLoadPointerAddress(self, pointer, register):
        # Loads the value (address pointed to) of the pointer into register
        self.writeAinst(pointer)
        self.write(register + "=M")

    def writeLoadPointerAddressValue(self, pointer, register):
        # Loads the value of the address pointed to by the pointer into register
        self.writeAinst(pointer)
        self.write("A=M")
        self.write(register + "=M")
        
    def writeValue2Pointer(self, pointer, value):
        # Write value to address pointed to by pointer
        self.writeAinst(str(value))
        self.write("D=A")
        self.writeLoadPointerAddress(pointer, "A")
        self.write("M=D")

    def writeR13OffsetAddress(self, segment, index):
        # Write offset constant into R13 register
        self.writeValue2Address("R13", str(index))
        # Load base address of segment into D register
        if segment == "local":
            self.writeLoadPointerAddress("LCL", "D")
        elif segment == "argument":
            self.writeLoadPointerAddress("ARG", "D")
        elif segment == "this":
            self.writeLoadPointerAddress("THIS", "D")
        elif segment == "that":
            self.writeLoadPointerAddress("THAT", "D")
        elif segment == "temp":
            self.writeLoadAddress2D("R5")
        elif segment == "static":
            self.writeLoadAddress2D("16")
        elif segment == "pointer":
            self.writeLoadAddress2D("R3")
        # Add base address to R13 (it is now target address)
        self.writeAinst("R13")
        self.write("M=D+M")     

    # High level coding methods

    def writeBinaryOp(self, cmd):
        # Load y into D register and address of x into A register
        self.decrementSP()
        self.writeLoadPointerAddressValue("SP", "D")
        self.decrementSP()
        self.writeLoadPointerAddress("SP", "A")
        # x = M and y = D
        if cmd == "add":
            self.write("M=M+D")
        elif cmd == "sub":
            self.write("M=M-D")
        elif cmd == "and":
            self.write("M=D&M")
        elif cmd == "or":
            self.write("M=D|M")
        self.incrementSP()

    def writeComparisonOp(self, cmd):
        # Set D = M - D = x - y
        self.decrementSP()
        self.writeLoadPointerAddressValue("SP", "D")
        self.decrementSP()
        self.writeLoadPointerAddress("SP", "A")
        self.write("D=M-D")
        # Write if/then statement using gotos
        true_label = "true_" + str(self.label_id)
        false_label = "false_" + str(self.label_id)
        end_label = "end_" + str(self.label_id)
        self.writeAinst(true_label)
        if cmd == "eq":
            self.write("D;JEQ")
        elif cmd == "gt":
            self.write("D;JGT")
        elif cmd == "lt":
            self.write("D;JLT")
        self.writeAinst(false_label)
        self.write("0;JMP")
        # If true, set SP value to -1
        self.writeLinst(true_label)
        self.writeLoadPointerAddress("SP", "A")
        self.write("M=-1")
        self.writeAinst(end_label)
        self.write("0;JMP")
        # If false, set SP value to 0
        self.writeLinst(false_label)
        self.writeLoadPointerAddress("SP", "A")
        self.write("M=0")
        # End label
        self.writeLinst(end_label)
        # Wrapup
        self.label_id += 1
        self.incrementSP()

    def writeUnaryOp(self, cmd):
        # Load address of y into A register
        self.decrementSP()
        self.writeLoadPointerAddress("SP", "A")
        # y = M
        if cmd == "neg":
            self.write("M=-M")
        elif cmd == "not":
            self.write("M=!M")
        self.incrementSP()

    def writeArithmetic(self, cmd):
        if cmd in self.binary_ops:
            self.writeBinaryOp(cmd)
        elif cmd in self.comparison_ops:
            self.writeComparisonOp(cmd)
        elif cmd in self.unary_ops:
            self.writeUnaryOp(cmd)   

    def writePush(self, segment, index):
        # Push the value in the segment index onto the stack
        if segment == "constant":
            self.writeValue2Pointer("SP", index)
        else:
            # Set target address in R13 register
            self.writeR13OffsetAddress(segment, index)
            # Load value of target address into D register
            self.writeLoadPointerAddressValue("R13", "D")
            # Assign D register to SP's target address
            self.writeD2Pointer("SP")
        self.incrementSP()

    def writePop(self, segment, index):
        # Pop top element of stack into given segment index
        # Set target address in R13 register
        self.writeR13OffsetAddress(segment, index)
        # Pop the top value of stack into D register
        self.decrementSP()
        self.writeLoadPointerAddressValue("SP", "D")
        # Assign D register to R13's target address
        self.writeD2Pointer("R13")

    def writeLabel(self, label):
        # Write label
        self.writeLinst(self.current_function + "$" + label)

    def writeGoto(self, label):
        # Go to label
        self.writeAinst(self.current_function + "$" + label)
        self.write("0;JMP")

    def writeIf(self, label):
        # If top value of stack =/= 0, jump to label
        self.decrementSP()
        self.writeLoadPointerAddressValue("SP", "D")
        self.writeAinst(self.current_function + "$" + label)
        self.write("D;JNE")

    def writeFunction(self, function_name, num_locals):
        # Declare a function
        print("Compiling function {}".format(function_name))
        self.current_function = function_name
        self.writeLinst(function_name) # Names are already unique from compilation
        for _ in range(num_locals):
            self.writePush("constant", 0)

    def writePushRegister(self, register):
        self.writeAinst(register)
        self.write("D=M")
        self.writeD2Pointer("SP")
        self.incrementSP()

    def writeCall(self, function_name, num_args):
        # Call function
        # Create unique return address and push onto stack
        return_address = self.current_function + "$" + function_name + "_" + str(self.label_id)
        self.label_id += 1
        self.writeAinst(return_address)
        self.write("D=A")
        self.writeD2Pointer("SP")
        self.incrementSP()
        # Push register state onto stack
        self.writePushRegister("LCL")
        self.writePushRegister("ARG")
        self.writePushRegister("THIS")
        self.writePushRegister("THAT")
        # Reposition ARG = SP - n - 5 and LCL = SP
        self.writeAinst("SP")
        self.write("D=M")
        self.writeAinst(str(num_args))
        self.write("D=D-A")
        self.writeAinst("5")
        self.write("D=D-A")
        self.writeAinst("ARG")
        self.write("M=D")
        self.writeAinst("SP")
        self.write("D=M")
        self.writeAinst("LCL")
        self.write("M=D")
        # Jump to function
        self.writeAinst(function_name)
        self.write("0;JMP")
        self.writeLinst(return_address)

    def writeR14OffsetCallVariables(self, offset, target):
        self.writeAinst("R14")
        self.write("D=M")   # D = *R14 = FRAME
        self.writeAinst(str(offset))
        self.write("A=D-A") # A = FRAME - offset
        self.write("D=M")   # D = *(FRAME - 5) = return address
        self.writeAinst(target)
        self.write("M=D")

    def writeReturn(self):
        # Virtual register R13 is already used for pop operations
        # Save LCL to virtual register 14 (FRAME)
        self.writeAinst("LCL")
        self.write("D=M")
        self.writeAinst("R14")
        self.write("M=D")
        # Save return address to virtual register 15 (RET)
        self.writeR14OffsetCallVariables(5, "R15")
        # Overwrite first argument with return value
        self.decrementSP()
        self.writeLoadPointerAddressValue("SP", "D")
        self.writeD2Pointer("ARG")
        # Set SP at one level above return value
        self.writeLoadPointerAddress("ARG", "D")
        self.writeAinst("SP")
        self.write("M=D+1")
        # Restore caller's THAT, THIS, ARG, and LCL pointers
        self.writeR14OffsetCallVariables(1, "THAT")
        self.writeR14OffsetCallVariables(2, "THIS")
        self.writeR14OffsetCallVariables(3, "ARG")
        self.writeR14OffsetCallVariables(4, "LCL")
        # Goto return address
        self.writeAinst("R15")
        self.write("A=M")
        self.write("0;JMP")


if __name__ == '__main__':
    assert(len(sys.argv)==2)
    vm_file = sys.argv[1]
    translator = VMTranslator(vm_file)
    translator.translate()
