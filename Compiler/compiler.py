import sys
import os
import pathlib

from lexer import Lexer
from parser import Parser
from common import *


class Compiler:

    def __init__(self, input_path):
        self.jack_files = self.get_files(input_path)

    def compile(self):
        # Syntax directed translation
        # Parser will pull from lexer and drive the symbol table and VM encoder
        for jack_file in self.jack_files:
            stem_name = jack_file.stem
            output_file = os.path.join(jack_file.parent, stem_name + ".vm")
            lexer = Lexer(jack_file)
            parser = Parser(lexer, output_file)
            parser.compile()

    @staticmethod
    def get_files(input_path):
        # Collect all jack files
        if os.path.isfile(input_path):
            dir_paths = [input_path]
        elif os.path.isdir(input_path):
            dir_files = os.listdir(input_path)
            dir_paths = [os.path.join(input_path, file_path) for file_path in dir_files]
        else:
            raise RuntimeError("Invalid input path: {}".format(input_path))
        jack_files = []
        for file in dir_paths:
            file_path = pathlib.Path(file)
            file_ext = file_path.suffix
            if file_ext == '.jack':
                jack_files.append(file_path.absolute())
        return jack_files


if __name__ == '__main__':
    assert(len(sys.argv)==2)
    jack_file = sys.argv[1]
    compiler = Compiler(jack_file)
    compiler.compile()
