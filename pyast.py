from pypython import *
import compiler
import expr

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
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, a={self.a}, b={self.b}>'
    def parse(self, codeobj):
        self.a.parse(codeobj)
        self.b.parse(codeobj)
        codeobj.codes.extend([BINARY_ADD, 0])

class Sub:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, a={self.a}, b={self.b}>'
    def parse(self, codeobj):
        self.a.parse(codeobj)
        self.b.parse(codeobj)
        codeobj.codes.extend([BINARY_SUB, 0])

class Mul:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, a={self.a}, b={self.b}>'
    def parse(self, codeobj):
        self.a.parse(codeobj)
        self.b.parse(codeobj)
        codeobj.codes.extend([BINARY_MUL, 0])

class Div:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, a={self.a}, b={self.b}>'
    def parse(self, codeobj):
        self.a.parse(codeobj)
        self.b.parse(codeobj)
        codeobj.codes.extend([BINARY_DIV, 0])

class Mod:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, a={self.a}, b={self.b}>'
    def parse(self, codeobj):
        self.a.parse(codeobj)
        self.b.parse(codeobj)
        codeobj.codes.extend([BINARY_MOD, 0])

class Gt:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, a={self.a}, b={self.b}>'
    def parse(self, codeobj):
        self.a.parse(codeobj)
        self.b.parse(codeobj)
        codeobj.codes.extend([COMPARE_OP, 4])

class Lt:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, a={self.a}, b={self.b}>'
    def parse(self, codeobj):
        self.a.parse(codeobj)
        self.b.parse(codeobj)
        codeobj.codes.extend([COMPARE_OP, 0])

class Ge:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, a={self.a}, b={self.b}>'
    def parse(self, codeobj):
        self.a.parse(codeobj)
        self.b.parse(codeobj)
        codeobj.codes.extend([COMPARE_OP, 5])

class Le:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, a={self.a}, b={self.b}>'
    def parse(self, codeobj):
        self.a.parse(codeobj)
        self.b.parse(codeobj)
        codeobj.codes.extend([COMPARE_OP, 1])


class Eq:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, a={self.a}, b={self.b}>'
    def parse(self, codeobj):
        self.a.parse(codeobj)
        self.b.parse(codeobj)
        codeobj.codes.extend([COMPARE_OP, 2])

class Ne:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, a={self.a}, b={self.b}>'
    def parse(self, codeobj):
        self.a.parse(codeobj)
        self.b.parse(codeobj)
        codeobj.codes.extend([COMPARE_OP, 3])

class Negative:
    def __init__(self, n):
        self.n = n
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, n={self.n}>'
    def parse(self, codeobj):
        self.n.parse(codeobj)
        codeobj.codes.extend([UNARY_NEGATIVE, 0])

class Number:
    def __init__(self, n):
        self.n = n
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, n={self.n}>'
    def parse(self, codeobj):
        codeobj.codes.extend([LOAD_CONST, add_obj(codeobj.consts, self.n)])

class String:
    def __init__(self, s):
        self.s = s
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, s={repr(self.s)}>'
    def parse(self, codeobj):
        codeobj.codes.extend([LOAD_CONST, add_obj(codeobj.consts, self.s)])

class Bool:
    def __init__(self, b):
        self.b = b
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, b={repr(self.b)}>'
    def parse(self, codeobj):
        codeobj.codes.extend([LOAD_CONST, add_obj(codeobj.consts, self.b)])

class List:
    def __init__(self, l):
        self.l = l
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, l={repr(self.l)}>'
    def parse(self, codeobj):
        for obj in self.l:
            obj.parse(codeobj)
        codeobj.codes.extend([MAKE_LIST, len(self.l)])

class Tuple:
    def __init__(self, t):
        self.t = t
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, t={repr(self.t)}>'
    def parse(self, codeobj):
        for obj in self.t:
            obj.parse(codeobj)
        codeobj.codes.extend([MAKE_TUPLE, len(self.t)])

class Name:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, name={self.name}>'
    def parse(self, codeobj):
        codeobj.codes.extend([LOAD_GLOBAL, add_obj(codeobj.names, self.name)])

class Call:
    def __init__(self, name, args):
        self.name = name
        self.args = args
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, name={self.name}, args={self.args}>'
    def parse(self, codeobj):
        self.name.parse(codeobj)
        for arg in self.args:
            arg.parse(codeobj)
        codeobj.codes.extend([CALL_FUNCTION, len(self.args)])

class Assigment:
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, name={self.name}, value={self.value}>'
    def parse(self, codeobj):
        self.value.parse(codeobj)
        codeobj.codes.extend([STORE_GLOBAL, add_obj(codeobj.names, self.name.name)])

class If:
    def __init__(self, condition, stmts):
        self.condition = condition
        self.stmts = stmts
        self.prev = None
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object, condition={self.condition}, stmts={self.stmts}, prev={self.prev}>'
    def parse(self, codeobj):
        self.condition.parse(codeobj)
        last = len(codeobj.codes) + 1
        codeobj.codes.extend([POP_JUMP_IF_FALSE, 0])
        for stmt in self.stmts:
            stmt.parse(codeobj)
        pos = len(codeobj.codes)
        codeobj.codes[last] = pos

class Pass:
    def __repr__(self):
        return f'<{__name__}.{self.__class__.__name__} object>'
    def parse(self, codeobj):
        pass

def make_ast(tokens):
    expr.var.ilevel = 0
    expr.var.itype = None
    ast = Ast()
    tks = []
    for t in tokens:
        tks.append(t)
        if t.type == compiler.TT_NEWLINE:
            if expr.var.itype is None:
                ast.stmts.append(Statement(expr.expr(tks[:-1])))
            else:
                expr.var.itype.stmts.append(Statement(expr.expr(tks[:-1])))
            tks = []
    if tks:
        if expr.var.itype is None:
            ast.stmts.append(Statement(expr.expr(tks[:-1])))
        else:
            expr.var.itype.stmts.append(Statement(expr.expr(tks[:-1])))
    return ast

def add_obj(consts, obj):
    if obj not in consts:
        consts.append(obj)
    return consts.index(obj)

def make_codes(ast):
    codes = []
    consts = [None]
    names = []
    codeobj = Codeobj(codes, consts, names)
    for stmt in ast.stmts:
        stmt.parse(codeobj)
    return codes, consts, names
