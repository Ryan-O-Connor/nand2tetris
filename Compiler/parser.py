import sys

from common import *


class Parser:

    def __init__(self, lexer, output_file):
        self.lexer = lexer
        self.token_stack = []
        self.ast = XMLParseTree(output_file)

    def parse(self):
        # Each file consists of a single class to be parsed
        self.parseClass()

    def parseTerminal(self, expected_type, expected_value=None):
        # Consume the expected terminal from the lexer
        self.lexer.advance()
        assert(self.lexer.tokenType() == expected_type)
        if expected_value is not None:
            assert(self.lexer.tokenWord() == expected_value)
        self.ast.addTerminalNode(self.lexer.getToken())

    def parseClass(self):
        # class := 'class' className '{' classVarDec* subroutineDec* '}'
        self.ast.addNonterminalNode("class")
        self.parseTerminal(L_KEYWORD, "class")
        self.parseTerminal(L_IDENTIFIER)
        self.parseTerminal(L_SYMBOL, "{")
        while True:
            self.lexer.peek()
            if self.lexer.tokenWord() in ("static", "field"):
                self.parseClassVarDec()
            else:
                break
        while True:
            self.lexer.peek()
            if self.lexer.tokenWord() in ("constructor", "function", "method"):
                self.parseSubroutine()
            else:
                break
        self.parseTerminal(L_SYMBOL, "}")
        self.ast.endFocus()

    def parseAnyVarDec(self):
        # anyVarDec := type varName (',' varName)* ';'
        self.parseType()
        self.parseTerminal(L_IDENTIFIER)
        while True:
            self.lexer.peek()
            if self.lexer.tokenWord() != ',':
                break
            self.parseTerminal(L_SYMBOL, ',')
            self.parseTerminal(L_IDENTIFIER)
        self.parseTerminal(L_SYMBOL, ';')

    def parseClassVarDec(self):
        # classVarDec := ('static' | 'field') type varName (',' varName)* ';'
        self.ast.addNonterminalNode("classVarDec")
        self.parseTerminal(L_KEYWORD)
        self.parseAnyVarDec()
        self.ast.endFocus()

    def parseVarDec(self):
        # varDec := 'var' type varName (',' varName)* ';'
        self.ast.addNonterminalNode("varDec")
        self.parseTerminal(L_KEYWORD)
        self.parseAnyVarDec()
        self.ast.endFocus()
        
    def parseType(self):
        # type := 'int' | 'char' | 'boolean' | className
        # Any identifier is assumed to be a class name
        self.lexer.peek()
        if self.lexer.tokenWord() in ("int", "char", "boolean"):
            self.parseTerminal(L_KEYWORD)
        elif self.lexer.tokenType() == L_IDENTIFIER:
            self.parseTerminal(L_IDENTIFIER)
        else:
            raise SyntaxError("Expected type, but got {}".format(self.lexer.tokenWord()))

    def parseSubroutine(self):
        # subroutineDec := ('constructor' | 'function' | 'method' ) ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        self.ast.addNonterminalNode("subroutineDec")
        self.parseTerminal(L_KEYWORD)
        self.lexer.peek()
        if self.lexer.tokenWord() == "void":
            self.parseTerminal(L_KEYWORD)
        else:
            self.parseTerminal(L_IDENTIFIER)
        self.parseTerminal(L_IDENTIFIER)
        self.parseTerminal(L_SYMBOL, "(")
        self.parseParameterList()
        self.parseTerminal(L_SYMBOL, ")")
        # subroutineBody := '{' varDec* statements '}'
        self.ast.addNonterminalNode("subroutineBody")
        self.parseTerminal(L_SYMBOL, "{")
        while True:
            self.lexer.peek()
            if self.lexer.tokenWord() != "var":
                break
            self.parseVarDec()
        self.parseStatements()
        self.parseTerminal(L_SYMBOL, "}")
        self.ast.endFocus() # End subroutineBody
        self.ast.endFocus() # End subroutineDec
        
    def parseParameterList(self):
        # parametersList := ((type varName) (',' type varName)*)?
        self.ast.addNonterminalNode("parameterList")
        self.lexer.peek()
        if self.lexer.tokenWord() != ")":
            self.parseType()
            self.parseTerminal(L_IDENTIFIER)
            while True:
                self.lexer.peek()
                if self.lexer.tokenWord() != ",":
                    break
                self.parseTerminal(L_SYMBOL, ",")
                self.parseType()
                self.parseTerminal(L_IDENTIFIER)
        self.ast.endFocus()

    def parseStatements(self):
        # statements = (letStatement | ifStatement | whileStatement | doStatement | returnStatement)*
        self.ast.addNonterminalNode("statements")
        while True:
            self.lexer.peek()
            next_word = self.lexer.tokenWord()
            if next_word == "let":
                self.parseLet()
            elif next_word == "if":
                self.parseIf()
            elif next_word == "while":
                self.parseWhile()
            elif next_word == "do":
                self.parseDo()
            elif next_word == "return":
                self.parseReturn()
            else:
                break
        self.ast.endFocus()

    def parseDo(self):
        # doStatement := 'do' subroutineCall ';'
        self.ast.addNonterminalNode("doStatement")
        self.parseTerminal(L_KEYWORD, "do")
        self.parseCall()
        self.parseTerminal(L_SYMBOL, ";")
        self.ast.endFocus()

    def parseLet(self):
        # letStatement := 'let' varName ('[' expression ']')? '=' expression ';'
        self.ast.addNonterminalNode("letStatement")
        self.parseTerminal(L_KEYWORD, "let")
        self.parseTerminal(L_IDENTIFIER)
        self.lexer.peek()
        if self.lexer.tokenWord() == '[':
            self.parseTerminal(L_SYMBOL, "[")
            self.parseExpression()
            self.parseTerminal(L_SYMBOL, "]")
        self.parseTerminal(L_SYMBOL, "=")
        self.parseExpression()
        self.parseTerminal(L_SYMBOL, ";")
        self.ast.endFocus()

    def parseWhile(self):
        # whileStatement := 'while' '(' expression ')' '{' statements '}'
        self.ast.addNonterminalNode("whileStatement")
        self.parseTerminal(L_KEYWORD, "while")
        self.parseTerminal(L_SYMBOL, "(")
        self.parseExpression()
        self.parseTerminal(L_SYMBOL, ")")
        self.parseTerminal(L_SYMBOL, "{")
        self.parseStatements()
        self.parseTerminal(L_SYMBOL, "}")
        self.ast.endFocus()

    def parseReturn(self):
        # returnStatement := 'return' expression? ';'
        self.ast.addNonterminalNode("returnStatement")
        self.parseTerminal(L_KEYWORD, "return")
        self.lexer.peek()
        if self.lexer.tokenWord() != ";":
            self.parseExpression()
        self.parseTerminal(L_SYMBOL, ";")
        self.ast.endFocus()

    def parseIf(self):
        # ifStatement := 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        self.ast.addNonterminalNode("ifStatement")
        self.parseTerminal(L_KEYWORD, "if")
        self.parseTerminal(L_SYMBOL, "(")
        self.parseExpression()
        self.parseTerminal(L_SYMBOL, ")")
        self.parseTerminal(L_SYMBOL, "{")
        self.parseStatements()
        self.parseTerminal(L_SYMBOL, "}")
        self.lexer.peek()
        if self.lexer.tokenWord() == "else":
            self.parseTerminal(L_KEYWORD, "else")
            self.parseTerminal(L_SYMBOL, "{")
            self.parseStatements()
            self.parseTerminal(L_SYMBOL, "}")
        self.ast.endFocus()

    def parseCall(self):
        # call := subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'
        self.parseTerminal(L_IDENTIFIER)
        self.lexer.peek()
        if self.lexer.tokenWord() == "(":
            self.parseTerminal(L_SYMBOL, "(")
            self.parseExpressionList()
            self.parseTerminal(L_SYMBOL, ")")
        else:    
            self.parseTerminal(L_SYMBOL, ".")
            self.parseTerminal(L_IDENTIFIER)
            self.parseTerminal(L_SYMBOL, "(")
            self.parseExpressionList()
            self.parseTerminal(L_SYMBOL, ")")

    def parseExpression(self):
        self.ast.addNonterminalNode("expression")
        self.parseTerm()
        self.ast.endFocus()

    def parseTerm(self):
        self.ast.addNonterminalNode("term")
        self.parseTerminal(L_IDENTIFIER)
        self.ast.endFocus()

    def parseExpressionList(self):
        self.ast.addNonterminalNode("expressionList")
        self.lexer.peek()
        if self.lexer.tokenType() == L_SYMBOL:
            self.parseExpression()
        self.ast.endFocus()


class XMLParseTree:

    def __init__(self, output_file):
        self.root = None
        self.focus = None
        self.file_handle = open(output_file, "wt")
        self.indent_level = 0

    def __del__(self):
        self.file_handle.close()

    def write(self, text):
        self.file_handle.write(text + "\n")

    def writeTerminalTag(self, token):
        indentation = self.indent_level * 2 * " "
        open_tag = "<" + token.getTypeName() + ">"
        close_tag = "</" + token.getTypeName() + ">"
        self.write(indentation + open_tag + " " + token.getWord() + " " + close_tag)

    def writeNonterminalOpenTag(self, nonterminal_node):
        indentation = self.indent_level * 2 * " "
        open_tag = "<" + nonterminal_node.syntax_cat + ">"
        self.write(indentation + open_tag)
        self.indent_level += 1

    def writeNonterminalCloseTag(self, nonterminal_node):
        self.indent_level -= 1
        indentation = self.indent_level * 2 * " "
        close_tag = "</" + nonterminal_node.syntax_cat + ">"
        self.write(indentation + close_tag)

    def addNonterminalNode(self, syntaxCat):
        node = NonterminalNode(syntaxCat, parent=self.focus)
        if self.root is None:
            self.root = node
        self.focus = node
        self.writeNonterminalOpenTag(self.focus)

    def addTerminalNode(self, token):
        self.writeTerminalTag(token)

    def endFocus(self):
        self.writeNonterminalCloseTag(self.focus)
        self.focus = self.focus.parent


class NonterminalNode:

    def __init__(self, syntax_cat, parent):
        self.syntax_cat = syntax_cat
        self.parent = parent


class ParseTest:

    @staticmethod
    def test_parse():
        assert(len(sys.argv)==2)
        jack_file = sys.argv[1]
        lexer = Lexer(jack_file)
        parser = Parser(lexer, "out.xml")
        parser.parse()


if __name__ == '__main__':
    from lexer import Lexer
    ParseTest.test_parse()
