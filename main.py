from Scanner import Scanner
import Grammar
from LL_1 import LL_1
from Quaternary import get_asm

filename = './tmp.c'

f_input = open(filename, 'r')
trans = f_input.read()

s = Scanner(trans)
l = LL_1(Grammar.Grammar, Grammar.Start, Grammar.End)

tmp = s.get_token()

while tmp != None:
    l.read_token(tmp)
    tmp = s.get_token()

print get_asm()