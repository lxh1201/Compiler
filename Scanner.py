#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from Automachine import *
from Symbols import *
import os

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
                return -1
            if num >= 1024:
                print 'name is too long'
                exit(0)
        self.index = i
        if name in Keywords_table:
            return ('keywords', Keywords_table.index(name))
        if name in Name_table:
            return ('symbol', Name_table.index(name))
        Name_table.append(name)
        return ('symbol', len(Name_table)-1)

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
        self.index += len(digit)
        if digit in Constant_table:
            return ('constant', Constant_table.index(digit))
        Constant_table.append(digit)
        return ('constant', len(Constant_table)-1)

    def read_bounds(self):
        self.index += 1
        return ('delimiter', Delimiter_table.index(self.text[self.index-1]))

    def read_chr(self):
        i = self.index + 1
        tmp = i
        while self.text[i] != "'":
            if i == self.length - 1:
                exit(-1)
            i += 1
        self.index = i + 1
        s = self.text[tmp:i]
        if s in Char_table:
            return ('char', Char_table.index(s))
        Char_table.append(s)
        return ('char', len(Char_table)-1)

    def read_str(self):
        i = self.index + 1
        tmp = i
        while self.text[i] != '"':
            if i == self.length - 1:
                exit(-1)
            i += 1
        self.index = i + 1
        s = self.text[tmp:i]
        if s in String_table:
            return ('string', String_table.index(s))
        String_table.append(s)
        return ('string', len(String_table)-1)

    def get_token(self):
        while self.index < self.length:
            if self.text[self.index].isalpha() or self.text[self.index] == '_':
                return self.read_alpha()
            elif self.text[self.index].isdigit() or self.text[self.index] == '-':
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