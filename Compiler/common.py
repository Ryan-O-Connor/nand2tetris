

# Token data type
class Token:

    def __init__(self, word, token_type):
        self.word = word
        self.token_type = token_type

    def getWord(self):
        if self.token_type == L_STR:
            return self.word[1:-1]
        return self.word

    def getType(self):
        return self.token_type

    def getTypeName(self):
        return LexemeTypeMap[self.token_type]

    


# Jack keyword and symbol sets
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

LexemeTypeMap = {L_IDENTIFIER: "identifier", L_KEYWORD: "keyword", L_SYMBOL: "symbol", L_INT: "integer", L_STR: "string", L_COMMENT: "comment", L_SPACE: "space"}
