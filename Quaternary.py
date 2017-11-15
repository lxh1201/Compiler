import random
from Symbols import *
from Assembly import *

Action = ['action_add', 'action_mul', 'action_equal', 'action_func_start', 'action_func_end',
          'action_func_para', 'action_func', 'action_declare']
Semantic = []

__Chunk = None

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
        if tmp not in [i[0] for i in Func_symtab] and tmp not in [i[0] for i in Global_symtab]:
            tmp = [tmp, t, None, 'v', None, -1]
            Func_symtab.append(tmp)
            return ('tmp_sym', (0, len(Func_symtab)-1))

def get_entry(sym):
    if sym[0] in ['symbol', 'tmp_sym']:
        if type(sym[1]) != str:
            return sym
        name = sym[1]
        if In_func:
            tmp = [i[0] for i in Func_symtab]
            if name in tmp:
                return (sym[0], (0, tmp.index(name)))
            else:
                tmp = [i[0] for i in Global_symtab]
                if name in tmp:
                    return (sym[0], (1, tmp.index(name)))
                else:
                    print name + ' not defined'
                    exit(-1)
        else:
            tmp = [i[0] for i in Global_symtab]
            if name in tmp:
                return (sym[0], (0, tmp.index(name)))
            else:
                print name + ' not defined'
                exit(-1)
    else:
        return sym

def get_type(token):
    if token[0] in ['symbol', 'tmp_sym']:
        if In_func and token[1][0] == 0:
            return Func_symtab[token[1][1]][1]
        else:
            return Global_symtab[token[1][1]][1]
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
    name = Semantic.pop()[1]
    t = Semantic[-1][1]
    if In_func:
        if Func_symtab != []:
            tmp = [i[0] for i in Func_symtab]
            if name in tmp:
                print name + ' defined repeated'
                exit(-1)
        entry = [name, t, None, 'v', None, 0]
        Func_stakc.put(entry)
        Func_symtab.append(entry)
        index = len(Func_symtab) - 1
    else:
        if Global_symtab != []:
            tmp = [i[0] for i in Global_symtab]
            if name in tmp:
                print name + ' defined repeated'
                exit(-1)
        entry = [name, t, None, 'v', None, 0]
        Global_symtab.append(entry)
        index = len(Global_symtab) - 1
    Semantic.append(('symbol', (0, index)))


def action_func_start():
    global Func_entry, In_func, Func_stakc, __Chunk
    assert (Semantic[-2][1][0] == 0)
    Func_entry = Global_symtab[Semantic[-2][1][1]]
    Func_entry[3] = 'f'
    Func_entry[4] = [0, -1, []]
    In_func = True
    Func_stakc = Stack()
    __Chunk = Chunk()

def action_func_para():
    name = Semantic.pop()[1]
    t = Semantic.pop()[1]
    sym_entry = Func_entry[4][2]
    sym_entry.append(t)
    Func_entry[4][0] += 1
    if Func_symtab != []:
        tmp = [i[0] for i in Func_symtab]
        if name in tmp:
            print name + ' defined repeated'
            exit(-1)
    entry = [name, t, None, 'vf', None, ]
    Func_stakc.put(entry)
    Func_symtab.append(entry)

def action_func_end():
    #print Func_symtab
    #print Semantic
    __Chunk.produce_asm()
    pass

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

