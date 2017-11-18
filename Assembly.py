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
        self.active_register = [-2, -2]
        self.register_name = ['%eax', '%edx']
        self.active_table = {}
        self.active_stack = []
        self.optz = [] # [[father_index], lchild_index, rchild_index, constant, symbol, tmp_symbol, op]
        self.tree_exist_table = {}
        self.optimized_quats = []
        self.text = ''
        self.ret = None

    def get_name(self, entry):
        assert entry[0] in ['tmp_sym', 'symbol']
        if entry[1][0] == 0:
            return Symbols.Func_symtab[entry[1][1]][0]
        else:
            return Symbols.Global_symtab[entry[1][1]][0]

    def put(self, quat):
        if quat[0][0] == 'return':
            self.ret = quat[3]
            return
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
            for tmp in self.optz:
                if entry in tmp[4] and (tmp[3] != None or tmp[5] != []):
                    tmp[4].remove(entry)
        if index >= 0:
            if entry[0] == 'constant':
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
        if a == b:
            for entry in self.optz:
                for i in range(len(entry[0])):
                    if entry[0][i] > a:
                        entry[0][i] -= 1
                for i in range(1, 3):
                    if entry[i] > a:
                        entry[i] -= 1
        else:
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
        if a == b:
            del self.optz[a]
        else:
            del self.optz[b]
            del self.optz[a]

    def get_token_fm_optz(self, index):
        entry = self.optz[index]
        if entry[3] != None:
            return ('constant', (entry[3], 'int'))
        elif entry[4] != []:
            return entry[4][0]
        elif entry[5] != []:
            return entry[5][0]
        else:
            print 'somethings wrong'
            exit(-1)

    def optimize(self):
        for entry in self.quats:
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
        for entry in self.optz:
            if self.ret != None and self.ret in entry[4] and entry[3] != None:
                self.ret = ('constant', (entry[3], 'int'))
            if entry[6] == None and entry[3] != None:
                for i in entry[4]:
                    self.optimized_quats.append((('delimiter', '='), ('constant', (entry[3], 'int')), None, i))
            elif entry[6] != None:
                assert entry[1] != -1 and entry[2] != -1
                a = self.get_token_fm_optz(entry[1])
                b = self.get_token_fm_optz(entry[2])
                if entry[4] != []:
                    for i in entry[4]:
                        self.optimized_quats.append((('delimiter', entry[6]), a, b, i))
                else:
                    if entry[0] != []:
                        self.optimized_quats.append((('delimiter', entry[6]), a, b, entry[5][0]))
            else:
                for i in range(len(entry[4]) - 1):
                    self.optimized_quats.append((('delimiter', '='), entry[4][i], None, entry[4][i+1]))
        self.quats = self.optimized_quats


    def cal_active(self, index, entry):
        if entry == None or entry[0] == 'constant':
            return
        if entry[0] == 'symbol' and entry[1][0] == -1:
            self.active_stack[-1][index] = -1
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

    def location(self, entry):
        assert entry != None
        if entry[0] == 'constant':
            return '$' + str(entry[1][0])
        elif entry[0] == 'symbol':
            if Symbols.In_func:
                if entry[1][0] == 0:
                    return str(Symbols.Func_symtab[entry[1][1]][4]) + '(%ebp)'
                else:
                    return Symbols.Global_symtab[entry[1][1]][0]
            else:
                return Symbols.Global_symtab[entry[1][1]][0]
        elif entry[0] == 'tmp_sym':
            assert Symbols.Func_symtab[entry[1][1]][4] == None
            Symbols.Func_stack.put(Symbols.Func_symtab[entry[1][1]])
            i= Symbols.Func_symtab[entry[1][1]][4]
            return '[%ebp' + str(i) + ']'

    def get_inactive_register(self):
        for i in range(len(self.active_register)):
            if self.active_register[i] < 0:
                return i
        return -1

    def asm_op(self, src, des, op='movl'):
        return op + ' ' + src + ', ' + des

    def choose_inactive_register(self):
        min_num = float('inf')
        min_index = -1
        for i in range(len(self.active_register)):
            if self.active_register[i] == 0:
                continue
            if self.active_register[i] < min_num:
                min_num = self.active_register[i]
                min_index = i
        if min_index != -1:
            return min_index
        else:
            return 0

    def produce_op_asm(self, entry, line):
        if entry[1] in self.register:
            index = self.register.index(entry[1])
            r_name = self.register_name[index]
            if self.active_register[index] >= 0:
                i = self.get_inactive_register()
                if i > 0:
                    self.text += '\t' + self.asm_op(r_name, self.register_name[i]) + '\n'
                    self.register[i] = self.register[index]
                    self.active_register[i] = self.active_register[index]
                else:
                    self.text += '\t' + self.asm_op(r_name, self.location(self.register[index])) + '\n'
            self.active_register[index] = self.active_stack[line][2]
        else:
            i = self.get_inactive_register()
            if i >= 0:
                r_name = self.register_name[i]
                self.text += '\t' + self.asm_op(self.location(entry[1]), self.register_name[i]) + '\n'
                self.register[i] = entry[3]
                self.active_register[i] = self.active_stack[line][2]
            else:
                to_clean = self.get_inactive_register()
                r_name = self.register_name[to_clean]
                self.text += '\t' + self.asm_op(self.register_name[to_clean], self.location(self.register[to_clean])) + '\n'
                self.text += '\t' + self.asm_op(self.location(entry[1]), self.register_name[to_clean]) + '\n'
                self.register[to_clean] = entry[3]
                self.active_register[to_clean] = self.active_stack[line][2]
        if entry[0][1] == '+':
            self.text += '\t' + self.asm_op(self.location(entry[2]), r_name, 'addl') + '\n'
        elif entry[0][1] == '-':
            self.text += '\t' + self.asm_op(self.location(entry[2]), r_name, 'subl') + '\n'
        else:
            print 'to_do'
            exit(0)

    def save_all(self):
        for i in range(len(self.register)):
            if self.active_register[i] >= 0:
                self.text += '\t' + self.asm_op(self.register_name[i], self.location(self.register[i])) + '\n'
        if self.ret != None:
            if self.ret != self.register[0]:
                if self.ret in self.register:
                    i = self.register.index(self.ret)
                    self.text += '\t' + self.asm_op(self.register_name[i], self.register_name[0]) + '\n'
                else:
                    self.text += '\t' + self.asm_op(self.location(self.ret), self.register_name[0]) + '\n'
            self.text += '\tleave\n\tret\n'

    def push_entry(self, entry):
        addr = self.location(entry)
        self.text += '\tpushl ' + addr + '\n'

    def produce_asm(self):
        self.optimize()
        self.length = len(self.quats)
        self.produce_active_infotab()
        for i in range(len(self.quats)):
            entry = self.quats[i]
            if entry[0][1] in '+-*/':
                self.produce_op_asm(entry, i)
            elif entry[0][1] == '=':
                if entry[3][0] == 'symbol' and entry[3][1][0] == -1:
                    self.push_entry(entry[1])
                elif entry[1][1][0] == -1:
                    self.text += '\tcall ' + entry[1][1][1] + '\n'
                    self.text += '\taddl' + ' $' + str(entry[1][1][2] * 4) + ', %ebp\n'
                    self.text += '\t' + self.asm_op('%eax', self.location(entry[3])) + '\n'
                else:
                    self.text += '\t' + self.asm_op(self.location(entry[1]), self.location(entry[3])) + '\n'
        self.save_all()
        return self.text


