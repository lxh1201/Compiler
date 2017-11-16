import Symbols
import ctypes

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
        if type(sym_entry) != list:
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
        # eax ecx
        self.register = [None, None]
        self.active_table = {}
        self.active_stack = []
        self.optz = [] # [[father_index], lchild_index, rchild_index, constant, symbol, tmp_symbol, op]
        self.tree_exist_table = {}
        self.optimized_quats = []

    def get_name(self, entry):
        assert entry[0] in ['tmp_sym', 'symbol']
        if entry[1][0] == 0:
            return Symbols.Func_symtab[entry[1][1]][0]
        else:
            return Symbols.Global_symtab[entry[1][1]][0]

    def put(self, quat):
        self.quats.append(quat)

    def get_optz_index(self, entry):
        if entry[0] == 'constant':
            tmp = [i[3] for i in self.optz]
            if entry[1][0] in tmp:
                return tmp.index(entry[1][0])
            else:
                return self.optz_append(-1, entry)
        elif entry[0] == 'tmp_sym':
            tmp = [i[5] for i in self.optz]
            for i in range(len(tmp)):
                if entry in tmp[i]:
                    return i
            return self.optz_append(-1, entry)
        elif entry[0] == 'symbol':
            tmp = [i[4] for i in self.optz]
            for i in range(len(tmp)):
                if entry in tmp[i]:
                    return i
            return self.optz_append(-1, entry)
        else:
            print 'somethings wrong'
            exit(-1)

    def optz_append(self, index, entry, clear=False, father=-1, lchild=-1, rchild=-1, op=None):
        if clear and entry[0] == 'symbol':
            tmp = [i[4] for i in self.optz]
            if entry in tmp and (self.optz[tmp.index(entry)][3] != None or self.optz[tmp.index(entry)][5] != []):
                self.optz[tmp.index(entry)][4].remove(entry)
        if index >= 0:
            if entry[0] == 'constant':
                print entry
                self.optz[index][3] = entry[1][0]
            elif entry[0] == 'tmp_sym':
                self.optz[index][5].append(entry)
            elif entry[0] == 'symbol':
                self.optz[index][4].append(entry)
            else:
                print 'somethings wrong'
                exit(-1)
            return index
        else:
            if entry[0] == 'constant':
                if father == -1:
                    self.optz.append([[], lchild, rchild, entry[1][0], [], [], op])
                else:
                    self.optz.append([[father], lchild, rchild, entry[1][0], [], [], op])
            elif entry[0] == 'tmp_sym':
                if father == -1:
                    self.optz.append([[], lchild, rchild, None, [], [entry], op])
                else:
                    self.optz.append([[father], lchild, rchild, None, [], [entry], op])
            elif entry[0] == 'symbol':
                if father == -1:
                    self.optz.append([[], lchild, rchild, None, [entry], [], op])
                else:
                    self.optz.append([[father], lchild, rchild, None, [entry], [], op])
            else:
                print 'somethings wrong'
                exit(-1)
            return len(self.optz) - 1

    def get_same_father_index(self, entry1, entry2, op):
        a = set(entry1[0])
        b = set(entry2[0])
        c = a & b
        if c == []:
            return -1
        else:
            for i in c:
                if self.optz[i][6] == op:
                    return i
            return -1

    def move_index(self, a, b):
        c = a
        d = b
        a = min(c, d)
        b = max(c, d)
        for entry in self.optz:
            for i in range(len(entry[0])):
                if entry[0][i] > b:
                    entry[0][i] -= 2
                elif entry[0][i] > a:
                    entry[0][i] -= 1
            for i in range(1, 3):
                if entry[i] > b:
                    entry[i] -= 2
                elif entry[i] > a:
                    entry[i] -= 1
        for i in self.optz[a][4]:
            self.optimized_quats.append((('delimiter', '='), ('constant', (self.optz[a][3], 'int')), None, i))
        for i in self.optz[b][4]:
            self.optimized_quats.append((('delimiter', '='), ('constant', (self.optz[b][3], 'int')), None, i))
        del self.optz[b]
        del self.optz[a]

    def optimize(self):
        for entry in self.quats:
            #print entry
            if entry[0][0] == 'delimiter' and entry[0][1] == '=':
                index = self.get_optz_index(entry[1])
                self.optz_append(index, entry[3], True)
            elif entry[1][0] == 'constant' and entry[2][0] == 'constant':
                s = eval(str(entry[1][1][0]) + entry[0][1] + str(entry[2][1][0]))
                s = ctypes.c_int32(s).value
                new_entry = ('constant', (s, 'int'))
                index = self.get_optz_index(new_entry)
                self.optz_append(index, entry[3], True)
            else:
                a = self.get_optz_index(entry[1])
                b = self.get_optz_index(entry[2])
                if self.optz[a][3] != None and self.optz[b][3] != None:
                    tmp = self.get_same_father_index(self.optz[a], self.optz[b], None)
                    appended = False
                    while tmp != -1:
                        if self.optz[tmp][6] == entry[0][1]:
                            self.optz_append(tmp, entry[3], True)
                            appended = True
                        c = eval(str(self.optz[a][3]) + self.optz[tmp][6] + str(self.optz[b][3]))
                        c = ctypes.c_int32(c).value
                        self.optz[tmp][3] = c
                        self.optz[tmp][1] = -1
                        self.optz[tmp][2] = -1
                        self.optz[tmp][6] = None
                        tmp = self.get_same_father_index(self.optz[a], self.optz[b], None)
                    if not appended:
                        c = self.optz_append(-1, entry[3], True, -1, -1, -1, None)
                        self.optz[c][3] = eval(str(self.optz[a][3]) + entry[0][1] + str(self.optz[b][3]))
                    self.move_index(a, b)
                else:
                    tmp = self.get_same_father_index(self.optz[a], self.optz[b], entry[0][1])
                    if tmp >= 0:
                        self.optz_append(tmp, entry[3], True)
                    else:
                        c = self.optz_append(-1, entry[3], True, -1, a, b, entry[0][1])
                        self.optz[a][0].append(c)
                        self.optz[b][0].append(c)
        for i in self.optz:
            #print i
            pass


    def cal_active(self, index, entry):
        if entry == None or entry[0] == 'constant':
            return
        name = self.get_name(entry)
        if name not in self.active_table.keys():
            if entry[1][0] == 0:
                self.active_stack[-1][index] = -1
            else:
                self.active_stack[-1][index] = 0
            if index == 2:
                self.active_table[name] = -1
            else:
                self.active_table[name] = self.length
        else:
            self.active_stack[-1][index] = self.active_table[name]
            if index == 2:
                self.active_table[name] = -1
            else:
                self.active_table[name] = self.length

    def produce_active_infotab(self):
        for quat in self.quats[::-1]:
            if quat[0][0] != 'delimiter':
                print 'to_do'
                exit(0)
            if quat[0][1] not in '+-*/=':
                print 'to_do'
                exit(0)
            self.active_stack.append([-2, -2, -2])
            for i in range(3):
                self.cal_active(i, quat[i+1])
            self.length -= 1
        self.active_stack = self.active_stack[::-1]


    def produce_asm(self):
        self.optimize()
        self.length = len(self.quats)
        self.produce_active_infotab()
        print Symbols.Func_stack.get_offset()


