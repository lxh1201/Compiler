import random
import Symbols
from Assembly import Stack, Chunk

Action = ['action_add', 'action_mul', 'action_equal', 'action_func_start', 'action_func_end',
          'action_func_para', 'action_func', 'action_declare', 'action_return', 'action_call_func',
          ]
Semantic = [] # to create quaternary

__Chunk = None # to create assembly

__Section_data = '.section .data\n'
__Section_text = '''
.section .text
.globl main
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

def get_token(sym):
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

def get_entry(token):
    assert token[0] in ['symbol', 'tmp_sym']
    if Symbols.In_func:
        if token[1][0] == 0:
            return Symbols.Func_symtab[token[1][1]]
        else:
            return Symbols.Global_symtab[token[1][1]]
    else:
        assert token[1][0] == 0
        return Symbols.Global_symtab[token[1][1]]

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
    b = get_token(b)
    a = get_token(a)
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
    global __Chunk, __Section_text
    assert Semantic[-2][1][0] == 0
    Symbols.Func_entry = Symbols.Global_symtab[Semantic[-2][1][1]]
    Symbols.Func_entry[3] = 'f'
    Symbols.Func_entry[4] = []
    Symbols.In_func = True
    Symbols.Is_ret = False
    Symbols.Func_stack = Stack()
    __Chunk = Chunk()


def action_func_para():
    name = Semantic.pop()[1]
    t = Semantic.pop()[1]
    sym_entry = Symbols.Func_entry[4]
    sym_entry.append(t)
    if Symbols.Func_symtab != []:
        tmp = [i[0] for i in Symbols.Func_symtab]
        if name in tmp:
            print name + ' defined repeated'
            exit(-1)
    entry = [name, t, None, 'vf', None]
    Symbols.Func_stack.put(entry)
    Symbols.Func_symtab.append(entry)

def action_func_end(is_ret=False):
    global __Section_text, __Chunk
    __Section_text += Symbols.Func_entry[0] + ':\n'
    off = -Symbols.Func_stack.get_offset()
    __Section_text += '\tpushl %ebp\n'
    __Section_text += '\tmovl %esp, %ebp\n'
    if off != 0:
        __Section_text += '\tsubl $%d, %%esp\n' % off
    if is_ret:
        a = Semantic
        Semantic.pop()
        tmp = Semantic.pop()
        if tmp[0] == 'return':
            if Symbols.Func_entry[1] == 'void':
                __Section_text += __Chunk.produce_asm()
                __Section_text += '\tleave\n\tret\n'
            else:
                print "return type doesn't match"
                exit(-1)
        else:
            assert Semantic.pop()[0] == 'return'
            tmp = get_token(tmp)
            if tmp[0] == 'constant':
                if Symbols.Func_entry[1] != tmp[1][1]:
                    print "return type doesn't match"
                    exit(-1)
            elif tmp[0] == 'symbol':
                entry = get_entry(tmp)
                if entry[1] != Symbols.Func_entry[1]:
                    print "return type doesn't match"
                    exit(-1)
                if entry[3] == 'f':
                    print "return a function pointer isn't supported yet"
                    exit(-1)
            __Chunk.put((('return', None), None, None, tmp))
            __Section_text += __Chunk.produce_asm()
            Symbols.Is_ret = True
    else:
        __Section_text += __Chunk.produce_asm()
        __Section_text += '\tleave\n\tret\n'
    __Chunk = None
    Symbols.Func_entry = []
    Symbols.Func_symtab = []
    Symbols.Func_stack = None
    Symbols.In_func = False

def action_equal():
    b = Semantic.pop()
    op = Semantic.pop()
    a = Semantic.pop()
    b = get_token(b)
    a = get_token(a)
    return (op, b, None, a)

def action_call_func():
    assert Semantic.pop()[1] == ')'
    tmp = Semantic.pop()
    args_stack = []
    while tmp[1] != '(':
        args_stack.append(get_token(tmp))
        tmp = Semantic.pop()
    entry = get_entry(get_token(Semantic.pop()))
    if len(entry[4]) != len(args_stack):
        print entry[0] + ": func args don't match"
        exit(-1)
    for a, b in zip(entry[4], args_stack):
        if a != get_entry(b)[1]:
            print entry[0] + ": func args don't match"
            exit(-1)
    for i in args_stack[::-1]:
        __Chunk.put((('delimiter', '='), i, None, ('symbol', (-1, -1))))
    Semantic.append(('symbol', (-1, entry[0], len(args_stack))))


def parse_action(name):
    if Symbols.Is_ret and name != 'action_func_end':
        return
    if name == 'action_declare':
        action_declare()
    elif name == 'action_func_start':
        action_func_start()
    elif name == 'action_func_para':
        action_func_para()
    elif name == 'action_func_end':
        if Symbols.Is_ret:
            Symbols.Is_ret = False
            return
        action_func_end()
    elif name == 'action_add' or name == 'action_mul':
        __Chunk.put(produce_binop())
    elif name == 'action_equal':
        __Chunk.put(action_equal())
    elif name == 'action_return':
        if Symbols.Is_ret:
            return
        action_func_end(True)
    elif name == 'action_call_func':
        action_call_func()

def get_asm():
    global __Section_data
    for entry in Symbols.Global_symtab:
        if entry[3] == 'v':
            __Section_data += entry[0] + ':\n\t.long 0\n'
    return __Section_data + __Section_text
