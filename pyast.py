from pypython import *
import compiler

class Codeobj:
    def __init__(self, codes, consts, names):
        self.codes = codes
        self.consts = consts
        self.names = names

class Ast:
    def __init__(self):
        self.stmts = []

class Statement:
    def __init__(self, stmt):
        self.stmt = stmt
    def parse(self, codeobj):
        self.stmt.parse(codeobj)

class Add:
    p = 20
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def parse(self, codeobj):
        self.a.parse(codeobj)
        self.b.parse(codeobj)
        codeobj.codes.extend([BINARY_ADD, 0])
    def add(self, obj):
        if obj.p < self.p:
            self.b = obj
            return obj, self
        else:
            obj.add(self)
            return self, obj

class Sub:
    p = 20
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def parse(self, codeobj):
        self.a.parse(codeobj)
        self.b.parse(codeobj)
        codeobj.codes.extend([BINARY_SUB, 0])
    def add(self, obj):
        if obj.p < self.p:
            self.b = obj
            return obj, self
        else:
            obj.add(self)
            return self, obj

class Mul:
    p = 10
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def parse(self, codeobj):
        self.a.parse(codeobj)
        self.b.parse(codeobj)
        codeobj.codes.extend([BINARY_MUL, 0])
    def add(self, obj):
        if obj.p < self.p:
            self.b = obj
            return obj, self
        else:
            obj.add(self)
            return self, obj

class Div:
    p = 10
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def parse(self, codeobj):
        self.a.parse(codeobj)
        self.b.parse(codeobj)
        codeobj.codes.extend([BINARY_DIV, 0])
    def add(self, obj):
        if obj.p < self.p:
            self.b = obj
            return obj, self
        else:
            obj.add(self)
            return self, obj

class Mod:
    p = 10
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def parse(self, codeobj):
        self.a.parse(codeobj)
        self.b.parse(codeobj)
        codeobj.codes.extend([BINARY_MOD, 0])
    def add(self, obj):
        if obj.p < self.p:
            self.b = obj
            return obj, self
        else:
            obj.add(self)
            return self, obj

class Number:
    p = 0
    def __init__(self, n):
        self.n = n
    def parse(self, codeobj):
        codeobj.codes.extend([LOAD_CONST, add_obj(codeobj.consts, self.n)])
    def add(self, obj):
        return self, self

def make_ast(tokens):
    ast = Ast()
    i = 0
    now = None
    stmt = None
    while i < len(tokens):
        t = tokens[i]
        if t.type == compiler.TT_NUMBER:
            if now is None:
                now = stmt = Number(t.obj)
                print('1:now stmt:', now, stmt)
            else:
                now, stmt0 = now.add(Number(t.obj))
                print('2:now stmt:', now, stmt)
        elif t.type == compiler.TT_PUNCT:
            if now is not None:
                if t.obj in '+-*/%':
                    op = {'+': Add, '-': Sub, '*': Mul, '/': Div, '%': Mod}
                    if stmt.p == 0:
                        now = stmt = op[t.obj](now, None)
                        print('3:now stmt:', now, stmt)
                    else:
                        now, stmt = stmt.add(op[t.obj](now, None))
                        print('4:now stmt:', now, stmt)
        elif t.type == compiler.TT_NEWLINE:
            if now is not None:
                ast.stmts.append(Statement(stmt))
                stmt = None
                now = None
        i += 1
    if now:
        print(stmt)
        print(stmt.a)
        print(stmt.b)
        ast.stmts.append(Statement(stmt))
    return ast

def add_obj(consts, obj):
    if obj not in consts:
        consts.append(obj)
    return consts.index(obj)

def make_codes(ast):
    codes = [LOAD_CONST, 0]
    consts = [None]
    names = []
    codeobj = Codeobj(codes, consts, names)
    for stmt in ast.stmts:
        stmt.parse(codeobj)
    codes.extend([PRINT_STACK_TOP, 0])
    return codes, consts, names
