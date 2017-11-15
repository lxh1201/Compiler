#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from Automachine import *
from Symbols import *
import ctypes

class Scanner:

    def __init__(self, t):
        self.index = 0
        self.text = t
        self.length = len(t)

    def read_alpha(self):
        i = self.index + 1
        num = 0
        name = self.text[self.index]
        while self.text[i] not in spaces:
            if self.text[i].isalpha() or self.text[i].isdigit() or self.text[i] in legal:
                name += self.text[i]
                num += 1
                i += 1
            elif self.text[i] in Delimiter_table or self.text[i] in spaces:
                break
            else:
                print 'name is illegal'
                exit(-1)
            if num >= 1024:
                print 'name is too long'
                exit(-1)
        self.index = i
        if name in Keywords_table:
            return ('keywords', name)
        else:
            return ('symbol', name)

    def read_digit(self):
        def mdd(num):
            dic = {}
            for i in range(10):
                dic[str(i)] = num
            return dic
        trans_table = [
            dict(mdd(2), **{'-':1}),
            mdd(2),
            dict(mdd(2), **{'.':3, 'e':5, '\x00':8}),
            mdd(4),
            dict(mdd(4), **{'e':5, '\x00':8}),
            dict(mdd(7), **{'+':6, '-':6}),
            mdd(7),
            dict(mdd(7), **{'\x00':8}),
            {'\x00':8}
        ]
        am = machine(trans_table, [8])
        digit = am.get(self.text[self.index:], spaces + Delimiter_table)
        if digit == '\x00':
            print 'numbers wrong'
            exit(-1)
        self.index += len(digit)
        if '.' in digit:
            print "float isn't supported yet"
            exit(0)
        elif 'e' in digit:
            print "e(10^n) isn't supported yet"
            exit(0)
        else:
            out = ctypes.c_int32(eval(digit)).value
            return ('constant', (out, 'int'))

    def read_bounds(self):
        self.index += 1
        return ('delimiter', self.text[self.index-1])

    def read_chr(self):
        i = self.index + 1
        tmp = i
        while self.text[i] != "'":
            if i == self.length - 1:
                print "lost '"
                exit(-1)
            i += 1
        self.index = i + 1
        s = self.text[tmp:i]
        return ('char', s)

    def read_str(self):
        i = self.index + 1
        tmp = i
        while self.text[i] != '"':
            if i == self.length - 1:
                print 'lost "'
                exit(-1)
            i += 1
        self.index = i + 1
        s = self.text[tmp:i]
        return ('string', s)

    def get_token(self):
        while self.index < self.length:
            if self.text[self.index].isalpha() or self.text[self.index] == '_':
                return self.read_alpha()
            elif self.text[self.index].isdigit():
                return self.read_digit()
            elif self.text[self.index] in Delimiter_table:
                return self.read_bounds()
            elif self.text[self.index] == "'":
                return self.read_chr()
            elif self.text[self.index] == '"':
                return self.read_str()
            elif self.text[self.index] in spaces:
                self.index += 1
            else:
                return None