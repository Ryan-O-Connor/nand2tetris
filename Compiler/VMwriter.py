


class VMWriter:

    def __init__(self, output_file):
        self.output_file = output_file
        self.file_handle = open(output_file, "wt")

    def __del__(self):
        self.file_handle.close()

    def write(self, text):
        self.file_handle.write(text + "\n")

    def writePush(self, segment, index):
        self.write("push" + segment + str(index))

    def writePop(self, segment, index):
        pass

    def writeArithmetic(self, command):
        pass

    def writeLabel(self, label):
        pass

    def writeGoto(self, label):
        pass

    def writeIf(self, label):
        pass

    def writeCall(self, name, n_args):
        pass

    def writeFunction(self, name, n_locals):
        self.write("Function" + " " + name + " " + str(n_locals))
        for i in range(n_locals):
            self.writePush("local", i)

    def writeReturn(self):
        pass

