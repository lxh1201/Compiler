import random
from Symbols import *

Action = ['action_add', 'action_mul', 'action_equal', 'action_func_start', 'action_func_end',
          'action_func_para', 'action_func', 'action_declare']
Semantic = []

__sym_table_stack = []
__sym_table = []

def produce_tmp():
    tmp = chr(random.randint(ord('A'), ord('Z')))
    index = 0
    while True:
        index += 1
        if tmp + str(index) not in Name_table:
            Name_table.append(tmp + str(index))
            __sym_table.append([tmp + str(index), -1, -1, -1])
            return ['symbol', len(Name_table)-1]

def produce_binop():
    b = Semantic.pop()
    op = Semantic.pop()
    a = Semantic.pop()
    tmp = produce_tmp()
    Semantic.append(tmp)
    return [op, a, b, tmp]

def get_index(table, name, appended, index=0):
    if table != []:
        tmp = [i[index] for i in table]
        if name in tmp:
            return tmp.index(name)
    table.append(appended)
    return len(table) - 1

def declare():
    pass

def fill_func_table():
    pass

def parse_func_para():
    pass


def parse_action(name):
    if name == 'action_add' or name == 'action_mul':
        print produce_binop()
    elif name == 'action_declare':
        declare()
    elif name == 'action_func':
        fill_func_table()
    elif name == 'action_func_para':
        parse_func_para()
