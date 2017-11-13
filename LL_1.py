import Symbols
import copy

from Quaternary import *

class LL_1:

    def __init__(self, grammar, start_symbol, end_symbol):
        self.grammar = grammar
        self.start = start_symbol
        self.end = end_symbol
        self.analysis_table = {}
        self.stack = ['#', self.start]

    def parse(self, sen):
        tmp = copy.copy(sen)
        for i in tmp:
            if i in Action:
                tmp.remove(i)
        return tmp

    def first(self, H):
        ret = []
        for sen in self.grammar[H]:
            sen = self.parse(sen)
            for i in range(len(sen)):
                if sen[i] in self.end:
                    ret.append(sen[i])
                    break
                elif sen[i] in self.grammar.keys():
                    tmp = self.first(sen[i])
                    if tmp == None:
                        return None
                    if '\x00' not in tmp:
                        ret += tmp
                        break
                    else:
                        tmp.remove('\x00')
                        ret += tmp
                        if i == len(sen) - 1:
                            ret.append('\x00')
                elif sen[i] == '\x00':
                    ret.append('\x00')
                    break
                else:
                    return None
        return ret

    def follow(self, H):
        ret = []
        if H == self.start:
            ret += ['#']
        for first in self.grammar.keys():
            for sen in self.grammar[first]:
                if H not in sen:
                    continue
                sen = self.parse(sen)
                i = sen.index(H) + 1
                if i == len(sen) and H != first:
                        ret += self.follow(first)
                while i < len(sen):
                    if sen[i] in self.grammar.keys():
                        tmp = self.first(sen[i])
                    elif sen[i] in self.end:
                        tmp = [sen[i]]
                    else:
                        return None
                    if tmp == None:
                        return None
                    if '\x00' not in tmp:
                        ret += tmp
                        break
                    else:
                        tmp.remove('\x00')
                        ret += tmp
                        if i == len(sen) - 1 and H != first:
                            ret += self.follow(first)
                    i += 1
        return ret

    def select(self, head, sentense):
        ret = []
        sen = self.parse(sentense)
        for i in range(len(sentense)):
            if sentense[i] in self.end:
                return [sentense[i]]
            elif sentense[i] in self.grammar.keys():
                tmp = self.first(sentense[i])
                if tmp == None:
                    return None
                if '\x00' not in tmp:
                    ret += tmp
                    return ret
                else:
                    tmp.remove('\x00')
                    ret += tmp
                    if i == len(sentense) - 1:
                        ret += self.follow(head)
            elif sentense[i] == '\x00':
                return self.follow(head)
            else:
                return None
        return ret

    def transfer(self, token):
        if token[0] == 'keywords':
            return 'type'
        elif token[0] == 'delimiter':
            if  token[1] in '+-':
                return 'w0'
            elif  token[1] in '*/':
                return 'w1'
            else:
                return token[1]
        else:
            return token[0]

    def read_token(self, token):
        name = self.transfer(token)
        top = self.stack.pop()
        while True:
            if top in Action:
                parse_action(top)
                top = self.stack.pop()
            elif top in self.grammar.keys():
                if top not in self.analysis_table.keys():
                    self.analysis_table[top] = {}
                    for tmp in self.grammar[top]:
                        tmp2 = self.select(top, tmp)
                        for tmp3 in tmp2:
                            self.analysis_table[top][tmp3] = tmp
                if name not in self.analysis_table[top]:
                    return False
                self.stack += list(self.analysis_table[top][name])[::-1]
                top = self.stack.pop()
            elif top == '\x00':
                top = self.stack.pop()
            elif name == top:
                Semantic.append(token)
                return True
            else:
                return False
