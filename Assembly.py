from Symbols import *

class Stack:
    def __init__(self):
        self.args_ptr = 8
        self.vars_ptr = 0

    def cal_len(self, t, a):
        if t == 'char':
            return 4
        elif t in ['int', 'float']:
            return 4
        else:
            return 4

    def put(self, sym_entry):
        if type(sym_entry) != list or len(sym_entry) != 5:
            exit(-1)
        if sym_entry[4] != None:
            exit(-1)
        length = self.cal_len(sym_entry[1], sym_entry[2])
        if sym_entry[3] == 'vn' or sym_entry[3] == 'vf':
            self.args_ptr += length
            sym_entry[4] = self.args_ptr
        elif sym_entry[3] == 'v':
            self.vars_ptr -= length
            sym_entry[4] = self.vars_ptr
        else:
            exit(-1)

    def get_offset(self):
        return self.vars_ptr

class Chunk:
    def __init__(self):
        self.quats = []
        # eax ebx ecx edx
        self.Register = [None, None, None, None]


    def put(self, quat):
        self.quats.append(quat)

    def optimize(self):
        pass

    def produce_asm(self):
        self.optimize()


