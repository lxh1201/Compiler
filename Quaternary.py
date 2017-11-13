import random
from Symbols import *
from Stack import *

Action = ['action_add', 'action_mul', 'action_equal', 'action_func_start', 'action_func_end',
          'action_func_para', 'action_func', 'action_declare']
Semantic = []

__global_table = []
__in_func = False
__func_table = []
__func_entry = []
__stack = None

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
        if tmp not in [i[0] for i in __func_table] and tmp not in [i[0] for i in __global_table]:
            tmp = [tmp, t, None, 'v', None]
            __stack.put(tmp)
            __func_table.append(tmp)
            return ('symbol', (0, len(__func_table)-1))

def get_entry(sym):
    if sym[0] == 'symbol':
        name = sym[1]
        if __in_func:
            tmp = [i[0] for i in __func_table]
            if name in tmp:
                return (sym[0], (0, tmp.index(name)))
            else:
                tmp = [i[0] for i in __global_table]
                if name in tmp:
                    return (sym[0], (1, tmp.index(name)))
                else:
                    exit(-1)
        else:
            tmp = [i[0] for i in __global_table]
            if name in tmp:
                return (sym[0], (0, tmp.index(name)))
            else:
                exit(-2)
    else:
        return sym

def get_type(token):
    if token[0] == 'symbol':
        if __in_func and token[1][0] == 0:
            return __func_table[token[1][1]][1]
        else:
            return __global_table[token[1][1]][1]
    elif token[0] == 'constant':
        return token[1][1]
    else:
        exit(-6)

def produce_binop():
    b = Semantic.pop()
    op = Semantic.pop()
    a = Semantic.pop()
    b = get_entry(b)
    a = get_entry(a)
    tmp = produce_tmp(get_type(a), get_type(b))
    Semantic.append(tmp)
    print (op, a, b, tmp)
    print __func_table

def action_declare():
    name = Semantic.pop()[1]
    t = Semantic[-1][1]
    if __in_func:
        if __func_table != []:
            tmp = [i[0] for i in __func_table]
            if name in tmp:
                exit(-3)
        entry = [name, t, None, 'v', None]
        __stack.put(entry)
        __func_table.append(entry)
        index = len(__func_table) - 1
    else:
        if __global_table != []:
            tmp = [i[0] for i in __global_table]
            if name in tmp:
                exit(-4)
        entry = [name, t, None, 'v', None]
        __global_table.append(entry)
        index = len(__global_table) - 1
    Semantic.append((t, (0, index)))


def action_func_start():
    global __func_entry, __in_func, __stack
    assert (Semantic[-2][1][0] == 0)
    __func_entry = __global_table[Semantic[-2][1][1]]
    __func_entry[3] = 'f'
    __func_entry[4] = [0, -1, []]
    __in_func = True
    __stack = Stack()

def action_func_para():
    name = Semantic.pop()[1]
    t = Semantic.pop()[1]
    sym_entry = __func_entry[4][2]
    sym_entry.append(t)
    __func_entry[4][0] += 1
    if __func_table != []:
        tmp = [i[0] for i in __func_table]
        if name in tmp:
            exit(-5)
    entry = [name, t, None, 'vf', None]
    __stack.put(entry)
    __func_table.append(entry)

def action_func_end():
    #print __func_table
    #print Semantic
    pass

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
        produce_binop()

