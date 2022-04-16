# DFA states for recognizing jack lexemes
S_0 = 0
S_1 = 1
S_2 = 2
S_3 = 3
S_4 = 4
S_5 = 5
S_6 = 6
S_7 = 7
S_8 = 8
S_9 = 9
S_10 = 10
S_11 = 11
S_12 = 12
S_ERROR = 13


# Character categories
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


# Keywords and Symbols
JackKeywords = {'class', 'constructor', 'function', 'method', 'field', 'static', \
        'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', \
        'this', 'let', 'do', 'if', 'else', 'while', 'return'}

JackSymbols = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', \
        '&', '|', '<', '>', '=', '~'}


# Lexeme types
L_IDENTIFIER = 0
L_KEYWORD = 1
L_SYMBOL = 2
L_INT = 3
L_STR = 4
L_COMMENT = 5
L_SPACE = 6

LexemeTypeMap = {L_IDENTIFIER: "Identifier", L_KEYWORD: "Keyword", L_SYMBOL: "Symbol", L_INT: "Integer", L_STR: "String", L_COMMENT: "Comment", L_SPACE: "Space"}


# Transition table
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

# Accepted state map
S_A = {S_1: L_IDENTIFIER, S_2: L_INT, S_4: L_STR, S_5: L_SYMBOL, S_6: L_SYMBOL, S_8: L_COMMENT, S_11: L_COMMENT, S_12: L_SPACE}
