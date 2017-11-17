import random
import Symbols
from Assembly import Stack, Chunk

Action = ['action_add', 'action_mul', 'action_equal', 'action_func_start', 'action_func_end',
          'action_func_para', 'action_func', 'action_declare']
Semantic = [] # to create quaternary

__Chunk = None # to create assembly

__Section_data = '.section .data\n'
__Section_text = '''
.section .text
.globl _start
_start:
\tcall main
\tmovl $1, %eax
\tint $0x80
'''

def produce_type(t1, t2):
    if t1 == 'int' and t2 == 'int':
        return 'int'
    else:
        print 'to_do'
        exit(0)

def produce_tmp(t1, t2):
    t = produce_type(t1, t2)
    head = chr(random.randint(ord('A'), ord('Z')))
    index = 0
    while True:
        index += 1
        tmp = str(index) + head
        if tmp not in [i[0] for i in Symbols.Func_symtab] and tmp not in [i[0] for i in Symbols.Global_symtab]:
            tmp = [tmp, t, None, 'v', None]
            Symbols.Func_symtab.append(tmp)
            return ('tmp_sym', (0, len(Symbols.Func_symtab)-1))

def get_entry(sym):
    if sym[0] in ['symbol', 'tmp_sym']:
        if type(sym[1]) != str:
            return sym
        name = sym[1]
        if Symbols.In_func:
            tmp = [i[0] for i in Symbols.Func_symtab]
            if name in tmp:
                return (sym[0], (0, tmp.index(name)))
            else:
                tmp = [i[0] for i in Symbols.Global_symtab]
                if name in tmp:
                    return (sym[0], (1, tmp.index(name)))
                else:
                    print name + ' not defined'
                    exit(-1)
        else:
            tmp = [i[0] for i in Symbols.Global_symtab]
            if name in tmp:
                return (sym[0], (0, tmp.index(name)))
            else:
                print name + ' not defined'
                exit(-1)
    else:
        return sym

def get_type(token):
    if token[0] in ['symbol', 'tmp_sym']:
        if Symbols.In_func and token[1][0] == 0:
            return Symbols.Func_symtab[token[1][1]][1]
        else:
            return Symbols.Global_symtab[token[1][1]][1]
    elif token[0] == 'constant':
        return token[1][1]
    else:
        print 'type wrong'
        exit(-1)

def produce_binop():
    b = Semantic.pop()
    op = Semantic.pop()
    a = Semantic.pop()
    b = get_entry(b)
    a = get_entry(a)
    tmp = produce_tmp(get_type(a), get_type(b))
    Semantic.append(tmp)
    return (op, a, b, tmp)

def action_declare():
    global __Section_data
    name = Semantic.pop()[1]
    t = Semantic[-1][1]
    if Symbols.In_func:
        if Symbols.Func_symtab != []:
            tmp = [i[0] for i in Symbols.Func_symtab]
            if name in tmp:
                print name + ' defined repeated'
                exit(-1)
        entry = [name, t, None, 'v', None]
        Symbols.Func_stack.put(entry)
        Symbols.Func_symtab.append(entry)
        index = len(Symbols.Func_symtab) - 1
    else:
        if Symbols.Global_symtab != []:
            tmp = [i[0] for i in Symbols.Global_symtab]
            if name in tmp:
                print name + ' defined repeated'
                exit(-1)
        entry = [name, t, None, 'v', None]
        Symbols.Global_symtab.append(entry)
        index = len(Symbols.Global_symtab) - 1
    Semantic.append(('symbol', (0, index)))


def action_func_start():
    global __Chunk
    assert Semantic[-2][1][0] == 0
    Symbols.Func_entry = Symbols.Global_symtab[Semantic[-2][1][1]]
    Symbols.Func_entry[3] = 'f'
    Symbols.Func_entry[4] = [0, -1, []]
    Symbols.In_func = True
    Symbols.Func_stack = Stack()
    __Chunk = Chunk()


def action_func_para():
    name = Semantic.pop()[1]
    t = Semantic.pop()[1]
    sym_entry = Symbols.Func_entry[4][2]
    sym_entry.append(t)
    Symbols.Func_entry[4][0] += 1
    if Symbols.Func_symtab != []:
        tmp = [i[0] for i in Symbols.Func_symtab]
        if name in tmp:
            print name + ' defined repeated'
            exit(-1)
    entry = [name, t, None, 'vf', None]
    Symbols.Func_stack.put(entry)
    Symbols.Func_symtab.append(entry)

def action_func_end():
    global __Section_text, __Chunk
    __Section_text += Symbols.Func_entry[0] + ':\n'
    __Section_text +=__Chunk.produce_asm()
    __Chunk = None
    Symbols.Func_entry = []
    Symbols.Func_symtab = []
    Symbols.Func_stack = None
    Symbols.In_func = False

def action_equal():
    b = Semantic.pop()
    op = Semantic.pop()
    a = Semantic.pop()
    b = get_entry(b)
    a = get_entry(a)
    return (op, b, None, a)

def parse_action(name):
    if name == 'action_declare':
        action_declare()
    elif name == 'action_func_start':
        action_func_start()
    elif name == 'action_func_para':
        action_func_para()
    elif name == 'action_func_end':
        action_func_end()
    elif name == 'action_add' or name == 'action_mul':
        __Chunk.put(produce_binop())
    elif name == 'action_equal':
        __Chunk.put(action_equal())

def get_asm():
    global __Section_data
    for entry in Symbols.Global_symtab:
        if entry[3] == 'v':
            __Section_data += entry[0] + ':\n\t.long 0\n'
    return __Section_data + __Section_text
