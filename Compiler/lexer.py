import sys

from common import *

# This lexer/scanner/tokenizer uses deterministic finite automata to generate lexemes
# based on the following 8 lexeme regular expressions for the jack language:

# 1) identifier = ([A..Z]|[a..z]|_)([A..Z]|[a..z]|[0..9]|_)*
# 2) keyword = special identifier found in dictionary
# 3) symbol = special symbol found in dictionary
# 4) integer constant = (0..9)(0..9)*, but not more than 32676
# 5) string constant = " (^"\n) "
# 6) single-line comment = //(^\n)
# 7) multi-line comment = /* (^*|*+^/)* */
# 8) whitespace characters = \n|\t| |\r

# See "Engineering a Compiler" by Cooper and Torczon, Ch.2 for details and notation
# This DFA is simulated as a table driven scanner

# You could just use the re library to match these, but this
# is more fun


# DFA states for recognizing jack lexemes
S_0 = 0         # Start state
S_1 = 1         # Identifier terminal state
S_2 = 2         # Integer constant terminal state
S_3 = 3         
S_4 = 4         # String constant terminate state
S_5 = 5         # Symbol terminal state except for /
S_6 = 6         # / terminal state
S_7 = 7
S_8 = 8         # Single line comment termimal state
S_9 = 9
S_10 = 10
S_11 = 11       # Multi line comment terminal state
S_12 = 12       # Space character terminal state
S_ERROR = 13


# DFA character categories
C_ALPHA = 0
C_NUMBER = 1
C_QUOTE = 2
C_NEWLINE = 3
C_UNDERSCORE = 4
C_OTHER_SYMBOL = 5
C_STAR = 6
C_FSLASH = 7
C_OTHER = 8
C_SPACE = 9


# DFA transition table
# Character categories not in table will map to error state
DELTA = {S_0: {C_ALPHA: S_1, C_NUMBER: S_2, C_QUOTE: S_3, C_NEWLINE: S_12, C_OTHER_SYMBOL: S_5, C_UNDERSCORE: S_1, C_STAR: S_5, C_FSLASH: S_6, C_SPACE: S_12},
        S_1: {C_ALPHA: S_1, C_NUMBER: S_1, C_UNDERSCORE: S_1},
        S_2: {C_NUMBER: S_2},
        S_3: {C_ALPHA: S_3, C_NUMBER: S_3, C_QUOTE: S_4, C_OTHER_SYMBOL: S_3, C_UNDERSCORE: S_3, C_STAR: S_3, C_FSLASH: S_3, C_OTHER: S_3, C_SPACE: S_3},
        S_4: {},
        S_5: {},
        S_6: {C_FSLASH: S_7, C_STAR: S_9},
        S_7: {C_ALPHA: S_7, C_NUMBER: S_7, C_QUOTE: S_7, C_NEWLINE: S_8, C_OTHER_SYMBOL: S_7, C_UNDERSCORE: S_7, C_STAR: S_7, C_FSLASH: S_7, C_OTHER: S_7, C_SPACE: S_7},
        S_8: {},
        S_9: {C_ALPHA: S_9, C_NUMBER: S_9, C_QUOTE: S_9, C_NEWLINE: S_9, C_OTHER_SYMBOL: S_9, C_UNDERSCORE: S_9, C_STAR: S_10, C_FSLASH: S_9, C_OTHER: S_9, C_SPACE: S_9},
        S_10: {C_ALPHA: S_9, C_NUMBER: S_9, C_QUOTE: S_9, C_NEWLINE: S_9, C_OTHER_SYMBOL: S_9, C_UNDERSCORE: S_9, C_STAR: S_10, C_FSLASH: S_11, C_OTHER: S_9, C_SPACE: S_9},
        S_11: {},
        S_12: {}}


# DFA accepted state map
S_A = {S_1: L_IDENTIFIER, S_2: L_INT, S_4: L_STR, S_5: L_SYMBOL, S_6: L_SYMBOL, S_8: L_COMMENT, S_11: L_COMMENT, S_12: L_SPACE}


class Lexer:

    def __init__(self, jack_file):
        self.jack_file = jack_file
        self.file_handle = open(jack_file, "rt")
        self.DFA = JackLexemeDFA()
        self.character_stack = []
        self.token_queue = []
        self.token = None
        self.EOF = False

    def __del__(self):
        self.file_handle.close()

    def hasMoreTokens(self):
        return not self.EOF

    def peek(self, again=False):
        # Advance token stream to peek ahead, but don't consume token
        if self.token_queue and not again:
            # Don't peek more tokens, just the next one
            self.token = self.token_queue[0]
        else:
            # Continue to peek further tokens ahead
            self.advance(again=True)
            self.token_queue.append(self.token)

    def advance(self, again=False):
        # Advance to next significant lexeme in file stream
        if again or not self.token_queue:
            # No peeked tokens in the queue or continue advancing again anyway
            while self.hasMoreTokens():
                self.DFA.reset()
                while not self.EOF:
                    c = self.getCh()
                    if not c:
                        self.EOF = True
                        c = '\n'
                    error_state = self.DFA.update(c)
                    if error_state:
                        if not c.isspace():
                            self.ungetCh(c)
                        break
                token_type = self.DFA.getType()
                if token_type != L_COMMENT and token_type != L_SPACE:
                    break
            self.token = Token(word=self.DFA.getLexeme(), token_type=self.DFA.getType())
        else:
            # Already peeked token in the queue
            self.token = self.token_queue.pop(0)

    def ungetCh(self, c):
        self.character_stack.append(c)

    def getCh(self):
        if self.character_stack:
            next_ch = self.character_stack.pop()
        else:
            next_ch = self.file_handle.read(1)
        return next_ch

    def getToken(self):
        return self.token

    def tokenWord(self):
        return self.token.word

    def tokenType(self):
        return self.token.token_type


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
        return self.lexeme

    def getType(self):
        # If terminal state, return lexeme and type
        lexeme_type = S_A.get(self.state)
        if lexeme_type is None:
            raise SyntaxError("DFA terminated in non-terminal state \"{}\" on lexeme \"{}\"".format(self.state, self.lexeme))
        if lexeme_type == L_IDENTIFIER:
            if self.lexeme in JackKeywords:
                lexeme_type = L_KEYWORD
        return lexeme_type

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


class LexTest:

    @staticmethod
    def test_lex():
        assert(len(sys.argv)==2)
        jack_file = sys.argv[1]
        lexer = Lexer(jack_file)
        while lexer.hasMoreTokens():
            lexer.advance()
            print("{}: {}".format(LexemeTypeMap[lexer.tokenType()], lexer.tokenWord()))


if __name__ == '__main__':
    LexTest.test_lex()
