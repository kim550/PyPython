import pyast
import compiler

class Var: pass
var = Var()
var.ilevel = 0
var.itype = None

def expr(tokens):
    left = assigment(tokens)
    if left is None:
        left = gllevel(tokens)
    if left is None:
        return pyast.Pass()
    else:
        return left

def assigment(tokens):
    tks = tokens.copy()
    left = name(tokens)
    if not tokens or left is None:
        tokens[:] = tks
        return None
    t = tokens.pop(0)
    if t.type == compiler.TT_PUNCT and t.obj == '=':
        right = expr(tokens)
        left = pyast.Assigment(left, right)
        return left
    else:
        tokens[:] = tks
        return None

def gllevel(tokens):
    left = addlevel(tokens)
    if not tokens:
        return left
    t = tokens.pop(0)
    while t.type == compiler.TT_PUNCT and t.obj in '<=>=!==':
        op = {'>': pyast.Gt, '<': pyast.Lt, '>=': pyast.Ge, '<=': pyast.Le, '==': pyast.Eq, '!=': pyast.Ne}
        right = addlevel(tokens)
        left = op[t.obj](left, right)
        if not tokens:
            return left
        t = tokens.pop(0)
    tokens.insert(0, t)
    return left

def addlevel(tokens):
    left = mullevel(tokens)
    if not tokens:
        return left
    t = tokens.pop(0)
    while t.type == compiler.TT_PUNCT and t.obj in '+-':
        if t.obj == '+':
            right = mullevel(tokens)
            left = pyast.Add(left, right)
        elif t.obj == '-':
            right = mullevel(tokens)
            left = pyast.Sub(left, right)
        if not tokens:
            return left
        t = tokens.pop(0)
    tokens.insert(0, t)
    return left

def mullevel(tokens):
    left = primary(tokens)
    if not tokens:
        return left
    t = tokens.pop(0)
    while t.type == compiler.TT_PUNCT and t.obj in '*/%':
        if t.obj == '*':
            right = primary(tokens)
            left = pyast.Mul(left, right)
        elif t.obj == '/':
            right = primary(tokens)
            left = pyast.Div(left, right)
        elif t.obj == '%':
            right = primary(tokens)
            left = pyast.Mod(left, right)
        if not tokens:
            return left
        t = tokens.pop(0)
    tokens.insert(0, t)
    return left

def primary(tokens):
    t = tokens.pop(0)
    if t.type == compiler.TT_NUMBER:
        return pyast.Number(t.obj)
    elif t.type == compiler.TT_STRING:
        return pyast.String(t.obj)
    elif t.type == compiler.TT_PUNCT and t.obj in '+-':
        if t.obj == '+':
            return primary(tokens)
        else:
            n = primary(tokens)
            if type(n) == pyast.Number:
                n.n = -n.n
            else:
                n = pyast.Negative(n)
            return n
    elif t.type == compiler.TT_PUNCT and t.obj == '(':
        left = tuplelevel(tokens)
        if type(left) == list:
            return pyast.Tuple(left)
        else:
            return left
    elif t.type == compiler.TT_PUNCT and t.obj == '[':
        left = listlevel(tokens)
        return pyast.List(left)
    elif t.type == compiler.TT_IBEGIN:
        var.ilevel = t.obj
        return expr(tokens)
    elif t.type == compiler.TT_IEND:
        var.ilevel = t.obj
        var.itype = var.itype.prev
        return expr(tokens)
    else:
        tokens.insert(0, t)
        left = name(tokens)
        if not tokens:
            return left
        t = tokens.pop(0)
        if t.type == compiler.TT_PUNCT and t.obj == '(':
            right = args(tokens)
            return pyast.Call(left, right)
        else:
            tokens.insert(0, t)
            return left

def name(tokens):
    t = tokens.pop(0)
    if t.type == compiler.TT_NAME:
        return pyast.Name(t.obj)
    elif t.type == compiler.TT_KEYWORD:
        if t.obj == 'True':
            return pyast.Bool(True)
        elif t.obj == 'False':
            return pyast.Bool(False)
        elif t.obj == 'if':
            left = gllevel(tokens)
            t = tokens.pop(0)
            if t.type == compiler.TT_PUNCT and t.obj == ':':
                itype = var.itype
                var.itype = pyast.If(left, [])
                if itype is not None:
                    var.itype.prev = itype
                return var.itype

def args(tokens):
    left = None
    t = tokens.pop(0)
    if t.type == compiler.TT_PUNCT and t.obj == ')':
        return []
    tokens.insert(0, t)
    t = None
    r = []
    while t is None or t.type == compiler.TT_PUNCT and t.obj == ',':
        left = gllevel(tokens)
        r.append(left)
        t = tokens.pop(0)
        if t.type == compiler.TT_PUNCT and t.obj == ')':
            return r

def listlevel(tokens):
    left = None
    t = tokens.pop(0)
    if t.type == compiler.TT_PUNCT and t.obj == ']':
        return []
    tokens.insert(0, t)
    t = None
    r = []
    while t is None or t.type == compiler.TT_PUNCT and t.obj == ',':
        t = tokens.pop(0)
        if t.type == compiler.TT_PUNCT and t.obj == ']':
            return r
        tokens.insert(0, t)
        left = gllevel(tokens)
        r.append(left)
        t = tokens.pop(0)
        if t.type == compiler.TT_PUNCT and t.obj == ']':
            return r

def tuplelevel(tokens):
    left = None
    t = tokens.pop(0)
    if t.type == compiler.TT_PUNCT and t.obj == ')':
        return []
    tokens.insert(0, t)
    t = None
    r = []
    while t is None or t.type == compiler.TT_PUNCT and t.obj == ',':
        t = tokens.pop(0)
        if t.type == compiler.TT_PUNCT and t.obj == ')':
            return r
        tokens.insert(0, t)
        left = gllevel(tokens)
        r.append(left)
        t = tokens.pop(0)
        if t.type == compiler.TT_PUNCT and t.obj == ')':
            if len(r) == 1:
                return r[0]
            else:
                return r
