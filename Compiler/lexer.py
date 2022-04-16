
import sys
from compiler_constants import *


class Compiler:

    def __init__(self, jack_file):
        self.jack_file = jack_file
        self.lexer = Lexer(jack_file)

    def compile(self):
        while self.lexer.hasMoreTokens():
            self.lexer.advance()
            token = self.lexer.token()
            token_type = self.lexer.tokenType()
            if token_type != L_COMMENT and token_type != L_SPACE:
                print("Token {} of type {}".format(token, LexemeTypeMap[token_type]))


class Lexer:

    def __init__(self, jack_file):
        self.jack_file = jack_file
        self.file_handle = open(jack_file, "rt")
        self.DFA = JackLexemeDFA()
        self.stack = []
        self.lexeme = None
        self.lexeme_type = None
        self.EOF = False

    def __del__(self):
        self.file_handle.close()

    def hasMoreTokens(self):
        return not self.EOF

    def advance(self):
        # Advance to next significant lexeme in file stream
        self.DFA.reset()
        while not self.EOF:
            c = self.nextChar()
            if not c:
                self.EOF = True
                c = '\n'
            error_state = self.DFA.update(c)
            if error_state:
                if not c.isspace():
                    self.pushback(c)
                break
        lexeme, lexeme_type = self.DFA.getLexeme()
        self.lexeme = lexeme
        self.lexeme_type = lexeme_type

    def pushback(self, c):
        self.stack.append(c)

    def nextChar(self):
        # Check buffer and return most recent character
        if self.stack:
            next_ch = self.stack.pop()
        else:
            next_ch = self.file_handle.read(1)
        return next_ch

    def tokenType(self):
        return self.lexeme_type

    def token(self):
        return self.lexeme


class JackLexemeDFA:

    def __init__(self):
        self.reset()
        
    def reset(self):
        self.state = S_0
        self.lexeme = ''

    def update(self, c):
        # Update lexeme and determine if error state
        char_cat = self.charCat(c)
        new_state = self.transition(self.state, char_cat)
        if new_state == S_ERROR:
            return True
        self.state = new_state
        self.lexeme += c
        return False

    def getLexeme(self):
        # If terminal state, return lexeme and type
        lexeme_type = S_A.get(self.state)
        if lexeme_type is None:
            raise SyntaxError("DFA terminated in non-terminal state \"{}\" on lexeme \"{}\"".format(self.state, self.lexeme))
        if lexeme_type == L_IDENTIFIER:
            if self.lexeme in JackKeywords:
                lexeme_type = L_KEYWORD
        return (self.lexeme, lexeme_type)

    @staticmethod
    def charCat(c):
        # Determine character category
        if c.isalpha():
            return C_ALPHA
        elif c.isnumeric():
            return C_NUMBER
        elif c in JackSymbols:
            if c == "*":
                return C_STAR
            elif c == "/":
                return C_FSLASH
            return C_OTHER_SYMBOL
        elif c == "\n":
            return C_NEWLINE
        elif c == "\"":
            return C_QUOTE
        elif c == "_":
            return C_UNDERSCORE
        elif c.isspace():
            return C_SPACE
        return C_OTHER

    @staticmethod
    def transition(state, char_cat):
        # State transition function
        new_state = DELTA[state].get(char_cat)
        if new_state is None:
            return S_ERROR
        return new_state


if __name__ == '__main__':
    assert(len(sys.argv)==2)
    jack_file = sys.argv[1]
    compiler = Compiler(jack_file)
    compiler.compile()
