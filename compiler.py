import keyword

import pyast

TT_EOF = 0
TT_NUMBER = 1
TT_NAME = 2
TT_PUNCT = 3
TT_STRING = 4
TT_NEWLINE = 5
TT_KEYWORD = 6
TT_IBEGIN = 7
TT_IEND = 8

MAX_INDENT_LEVEL = 100

class TokenStream:
    def __init__(self, code):
        self.code = code
        self.indent = None
        self.ilevel = 0
        self.newline = False
    def get(self):
        t = None
        n = 0
        if not self.code:
            return Token(TT_EOF, None)
        char = self.code[0]
        if self.newline:
            ilevel = self.ilevel
            if self.indent is not None:
                if char == self.indent[0]:
                    indent = ''
                    x = 0
                    while self.code[x] in ' \t':
                        indent += self.code[x]
                        x += 1
                        if x >= len(self.code):
                            break
                    times = 1
                    while times < MAX_INDENT_LEVEL:
                        if self.indent * times == indent:
                            break
                        times += 1
                    self.ilevel = times
            if ilevel + 1 == self.ilevel:
                self.newline = False
                return Token(TT_IBEGIN, self.ilevel)
            elif ilevel - 1 == self.ilevel:
                self.newline = False
                return Token(TT_IEND, self.ilevel)
            elif ilevel > self.ilevel:
                self.ilevel = ilevel - 1
                return Token(TT_IEND, self.ilevel)
            elif ilevel == self.ilevel:
                self.newline = False
        while char == ' ':
            self.code = self.code[1:]
            if not self.code:
                return Token(TT_EOF, None)
            char = self.code[0]
        if char in ',:()[]{}':
            t = Token(TT_PUNCT, char)
            n = 1
        elif char in '<>=+-*/%~^|':
            if len(self.code) >= 2 and self.code[1] == '=':
                t = Token(TT_PUNCT, self.code[:2])
                n = 2
            else:
                t = Token(TT_PUNCT, char)
                n = 1
        elif char in '0123456789.':
            x = 1
            num = char
            while True:
                try:
                    float(num)
                except ValueError:
                    num = num[:-1]
                    break
                if x >= len(self.code) or self.code[x] in '\n ':
                    num = num
                    break
                x += 1
                num = self.code[:x]
            if num.isdigit():
                t = Token(TT_NUMBER, int(num))
            else:
                t = Token(TT_NUMBER, float(num))
            n = len(num)
        elif char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_':
            name = ''
            x = 1
            while char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_1234567890':
                name += char
                if x >= len(self.code):
                    break
                char = self.code[x]
                x += 1
            if keyword.iskeyword(name):
                t = Token(TT_KEYWORD, name)
            else:
                t = Token(TT_NAME, name)
            n = len(name)
        elif char in '\'"':
            ord_ = char
            s = ''
            x = 1
            char = ''
            while char != ord_:
                s += char
                if x >= len(self.code):
                    break
                char = self.code[x]
                x += 1
            t = Token(TT_STRING, s)
            n = len(s) + 2
        elif char in '\n;':
            if char == '\n':
                self.newline = True
                if self.indent is None and len(self.code) >= 2:
                    if self.code[1].isspace():
                        indent = ''
                        x = 1
                        while self.code[x] in ' \t':
                            indent += self.code[x]
                            x += 1
                            if x >= len(self.code):
                                break
                        if x < len(self.code) and self.code[x] != '\n':
                            self.indent = indent
            t = Token(TT_NEWLINE, None)
            n = 1
        self.code = self.code[n:]
        return t

class Token:
    def __init__(self, type_, obj):
        self.type = type_
        self.obj = obj
    def __repr__(self):
        return '<Token type=%r obj=%r>' % (self.type, self.obj)

def get_tokens(code):
    ts = TokenStream(code)
    t = ts.get()
    tokens = []
    while t.type != TT_EOF:
        tokens.append(t)
        t = ts.get()
    return tokens

def compile(code):
    tokens = get_tokens(code)
    ast = pyast.make_ast(tokens)
    res = pyast.make_codes(ast)
    return res

if __name__ == '__main__':
    while True:
        code = input('.> ')
        tokens = get_tokens(code)
        ast = pyast.make_ast(tokens)
        for stmt in ast.stmts:
            print(stmt.stmt)
