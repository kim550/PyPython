import operator
import sys

LOAD_CONST = 0
BINARY_ADD = 1
PRINT_STACK_TOP = 2
LOAD_FAST = 3
LOAD_GLOBAL = 4
STORE_FAST = 5
STORE_GLOBAL = 6
JUMP = 7
POP_JUMP_IF_FALSE = 8
COMPARE_OP = 9
MAKE_FUNCTION = 10
CALL_FUNCTION = 11
RETURN_VALUE = 12
POPTOP = 13
BINARY_SUB = 14
BINARY_MUL = 15
BINARY_DIV = 16
BINARY_MOD = 17
MAKE_LIST = 18
MAKE_TUPLE = 19
UNARY_NEGATIVE = 20

builtins = {}

class VirtualMachine:
    def __init__(self):
        self.frames = []
        self.frame = None
    def run_code(self, codes, consts, names, global_names=None, local_names=None):
        frame = self.make_frame(codes, consts, names, global_names, local_names)
        self.run_frame(frame)
    def make_frame(self, codes, consts, names, global_names, local_names, call_args={}):
        if global_names is not None and local_names is not None:
            local_names = global_names
        elif self.frames:
            global_names = self.frame.global_names
            local_names = {}
        else:
            global_names = local_names = builtins.copy()
        local_names.update(call_args)
        frame = Frame(codes, consts, names, global_names, local_names, self.frame, self)
        return frame
    def push_frame(self, frame):
        self.frames.append(frame)
        self.frame = frame
    def pop_frame(self):
        frame = self.frames.pop()
        if self.frames:
            self.frame = self.frames[-1]
        else:
            self.frame = None
        return frame
    def run_frame(self, frame):
        self.push_frame(frame)
        frame.run()

class Frame:
    def __init__(self, codes, consts, names, global_names, local_names, prev_frame, vm):
        self.codes = codes
        self.consts = consts
        self.names = names
        self.global_names = global_names
        self.local_names = local_names
        self.prev_frame = prev_frame
        self.vm = vm
        self.pos = 0
        self.stack = []
        self.functions = [self.LOAD_CONST,
                          self.BINARY_ADD,
                          self.PRINT_STACK_TOP,
                          self.LOAD_FAST,
                          self.LOAD_GLOBAL,
                          self.STORE_FAST,
                          self.STORE_GLOBAL,
                          self.JUMP,
                          self.POP_JUMP_IF_FALSE,
                          self.COMPARE_OP,
                          self.MAKE_FUNCTION,
                          self.CALL_FUNCTION,
                          self.RETURN_VALUE,
                          self.POPTOP,
                          self.BINARY_SUB,
                          self.BINARY_MUL,
                          self.BINARY_DIV,
                          self.BINARY_MOD,
                          self.MAKE_LIST,
                          self.MAKE_TUPLE,
                          self.UNARY_NEGATIVE]
        self.last_exception = None
    def run(self):
        while self.pos < len(self.codes):
            code = self.codes[self.pos]
            data = self.codes[self.pos + 1]
            try:
                r = self.functions[code](data)
                if r == 'error':
                    self.print_error()
                    for frame in self.vm.frames:
                        frame.pos = len(frame.codes)
                    self.vm.frames = []
                    self.vm.frame = None
                    return
            except RecursionError as e:
                print('PyPython: %s: %s' % (e.__class__.__name__, e), file=sys.stderr)
                self.vm.frames = []
                self.vm.frame = None
                return
            self.pos += 2
    def raise_error(self, error):
        self.last_exception = error
        return 'error'
    def print_error(self):
        error = self.last_exception
        print('Traceback (most recent call last):', file=sys.stderr)
        print('  File "<unknown>", line ?, in <unknown>', file=sys.stderr)
        if error.__str__():
            print('%s: %s' % (error.__class__.__name__, error.__str__()), file=sys.stderr)
        else:
            print(error.__class__.__name__, file=sys.stderr)
    def LOAD_CONST(self, data):
        self.stack.append(self.consts[data])
    def BINARY_ADD(self, data):
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(b + a)
    def PRINT_STACK_TOP(self, data):
        if self.stack[-1] is not None:
            print(repr(self.stack[-1]))
    def LOAD_FAST(self, data):
        self.stack.append(self.local_names[self.names[data]])
    def LOAD_GLOBAL(self, data):
        if self.names[data] not in self.global_names.keys():
            return self.raise_error(NameError("name '%s' is not defined" % self.names[data]))
        self.stack.append(self.global_names[self.names[data]])
    def STORE_FAST(self, data):
        a = self.stack.pop()
        self.local_names[self.names[data]] = a
    def STORE_GLOBAL(self, data):
        a = self.stack.pop()
        self.global_names[self.names[data]] = a
    def JUMP(self, data):
        self.pos = data
    def POP_JUMP_IF_FALSE(self, data):
        a = self.stack.pop()
        if a == 0:
            self.pos = data
    def COMPARE_OP(self, data):
        operators = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt, operator.ge]
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(operators[data](b, a))
    def MAKE_FUNCTION(self, data):
        a = self.stack.pop()
        b = self.stack.pop()
        self.local_names[b] = Function(a)
    def CALL_FUNCTION(self, data):
        args = []
        for i in range(data):
            args.append(self.stack.pop())
        args.reverse()
        a = self.stack.pop()
        if type(a) == BuiltinFunction:
            a.call(args)
        elif len(a.codeobj.args) == data:
            callargs = {}
            for i in range(data):
                callargs[a.codeobj.args[i]] = args[i]
            a.call(callargs)
        else:
            raise Exception
    def RETURN_VALUE(self, data):
        if not self.vm.frames:
            print('PyPython CurentThread: frame list empty', file=sys.stderr)
            sys.exit()
        self.vm.pop_frame()
        a = self.stack.pop()
        self.vm.frame.stack.append(a)
    def POPTOP(self, data):
        self.stack.pop()
    def BINARY_SUB(self, data):
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(b - a)
    def BINARY_MUL(self, data):
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(b * a)
    def BINARY_DIV(self, data):
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(b / a)
    def BINARY_MOD(self, data):
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(b % a)
    def MAKE_LIST(self, data):
        l = []
        for i in range(data):
            l.append(self.stack.pop())
        l.reverse()
        self.stack.append(l)
    def MAKE_TUPLE(self, data):
        l = []
        for i in range(data):
            l.append(self.stack.pop())
        l.reverse()
        self.stack.append(tuple(l))
    def UNARY_NEGATIVE(self, data):
        self.stack.append(-self.stack.pop())

class CodeObj:
    def __init__(self, code, consts, names, args, vm):
        self.code = code
        self.consts = consts
        self.names = names
        self.args = args
        self.vm = vm

class Function:
    def __init__(self, codeobj):
        self.codeobj = codeobj
        self.vm = self.codeobj.vm
    def call(self, callargs):
        frame = self.vm.make_frame(self.codeobj.code, self.codeobj.consts, self.codeobj.names, None, None, callargs)
        self.vm.run_frame(frame)

class BuiltinFunction:
    def __init__(self, vm, name, func):
        self.vm = vm
        self.name = name
        self.func = func
        builtins[name] = self
    def call(self, callargs):
        a = self.func(*callargs)
        if self.vm.frame:
            self.vm.frame.stack.append(a)

def builtin(vm, name):
    def wrap(func):
        return BuiltinFunction(vm, name, func)
    return wrap

vm = VirtualMachine()

@builtin(vm, 'print')
def builtin_print(*args):
    first = True
    for arg in args:
        if not first:
            sys.stdout.write(' ')
        sys.stdout.write(str(arg))
        first = False
    sys.stdout.write('\n')

@builtin(vm, 'input')
def builtin_input(prompt=''):
    if prompt:
        sys.stdout.write(prompt)
        sys.stdout.flush()
    return sys.stdin.readline()[:-1]

@builtin(vm, 'locals')
def builtin_locals():
    return vm.frame.local_names

@builtin(vm, 'globals')
def builtin_globals():
    return vm.frame.global_names

@builtin(vm, 'exec')
def builtin_exec(code, globals_=None, locals_=None):
    if globals_ is None:
        globals_ = vm.frame.global_names
    if locals_ is None:
        locals_ = vm.frame.local_names
    co = compiler.compile(code)
    execute(*co, globals_, locals_)
    if vm.frames:
        vm.pop_frame()

@builtin(vm, 'eval')
def builtin_eval(code, globals_=None, locals_=None):
    if globals_ is None:
        globals_ = vm.frame.global_names
    if locals_ is None:
        locals_ = vm.frame.local_names
    co = compiler.compile(code)
    r = execute(*co, globals_, locals_)
    if vm.frames:
        vm.pop_frame()
        return r

@builtin(vm, 'abs')
def builtin_abs(x):
    x = int(x)
    if x < 0:
        return -x
    else:
        return x

@builtin(vm, 'id')
def builtin_abs(obj):
    return id(obj)

def execute(codes, consts, names, global_names=None, local_names=None, vm=vm):
    vm.run_code(codes, consts, names, global_names, local_names)
    if vm.frame and vm.frame.stack:
        return vm.frame.stack[-1]

def test2():
    # while True:
    #     print(2)
    codes = [LOAD_CONST,        0,
             PRINT_STACK_TOP,   0,
             LOAD_CONST,        0,
             JUMP,              0]
    consts = [2]
    names = []
    execute(codes, consts, names)

def test3():
    # n = 0
    # while n < 10:
    #     n += 1
    #     print(n)
    codes = [LOAD_CONST,        0,
             STORE_FAST,        0,
             LOAD_FAST,         0,
             LOAD_CONST,        1,
             COMPARE_OP,        0,
             POP_JUMP_IF_FALSE, 26,
             LOAD_FAST,         0,
             LOAD_CONST,        2,
             BINARY_ADD,        0,
             STORE_FAST,        0,
             LOAD_FAST,         0,
             PRINT_STACK_TOP,   0,
             JUMP,              4,
             LOAD_CONST,        0]
    consts = [0, 10, 1]
    names = ['n']
    execute(codes, consts, names)

def test4():
    # def f():
    #     print(2)
    #     return 'a'
    # print(f())
    codes_f = [LOAD_CONST,      1,
               PRINT_STACK_TOP, 0,
               LOAD_CONST,      0,
               RETURN_VALUE,    0]
    consts_f = ['a', 2]
    names_f = []
    codeobj_f = CodeObj(codes_f, consts_f, names_f, (), vm)
    codes = [LOAD_CONST,        1,
             LOAD_CONST,        0,
             MAKE_FUNCTION,     0,
             LOAD_FAST,         0,
             CALL_FUNCTION,     0,
             PRINT_STACK_TOP,   0]
    consts = [codeobj_f, 'f']
    names = ['f']
    execute(codes, consts, names)

def test5():
    # def f():
    #     print(2)
    #     f()
    # # Bad example.
    # f()
    codes_f = [LOAD_CONST,      1,
               PRINT_STACK_TOP, 0,
               LOAD_GLOBAL,     0,
               CALL_FUNCTION,   0,
               LOAD_CONST,      0,
               RETURN_VALUE,    0]
    consts_f = [None, 2]
    names_f = ['f']
    codeobj_f = CodeObj(codes_f, consts_f, names_f, (), vm)
    codes = [LOAD_CONST,        1,
             LOAD_CONST,        0,
             MAKE_FUNCTION,     0,
             LOAD_FAST,         0,
             CALL_FUNCTION,     0,
             PRINT_STACK_TOP,   0]
    consts = [codeobj_f, 'f']
    names = ['f']
    execute(codes, consts, names)

def test6():
    # def f(m, n):
    #     print(m)
    #     print(n)
    # f(5, 6)
    codes_f = [LOAD_FAST,       0,
               PRINT_STACK_TOP, 0,
               LOAD_FAST,       1,
               PRINT_STACK_TOP, 0,
               LOAD_CONST,      0,
               RETURN_VALUE,    0]
    consts_f = [None]
    names_f = ['m', 'n']
    codeobj_f = CodeObj(codes_f, consts_f, names_f, ('m', 'n'), vm)
    codes = [LOAD_CONST,        1,
             LOAD_CONST,        0,
             MAKE_FUNCTION,     0,
             LOAD_FAST,         0,
             LOAD_CONST,        2,
             LOAD_CONST,        3,
             CALL_FUNCTION,     2,
             POPTOP,            0]
    consts = [codeobj_f, 'f', 5, 6]
    names = ['f']
    execute(codes, consts, names)

if __name__ == '__main__':
    import compiler
    if len(sys.argv) == 1:
        while True:
            code = input('.> ')
            if code:
                c = None
                if code.strip()[-1] == ':':
                    while c is None or c.strip():
                        c = input('.. ')
                        code = code + '\n' + c
                r = execute(*compiler.compile(code))
                if r is not None:
                    print(repr(r))
    else:
        filename = sys.argv[1]
        with open(filename, encoding='utf-8') as f:
            codes = f.read()
        execute(*compiler.compile(codes, False))
