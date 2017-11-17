Type_table = ['int', 'void', 'char', 'float']
Delimiter_table = ['=', '>', '<', '+', '-', '*', '/', '{', '}', ',', ';', '(', ')', '[', ']']
spaces = [' ', '\n', '\t', '\r']
legal = ['_', '-']

Symtab_stack = []

Global_symtab = []
In_func = False
Func_symtab = []
Func_entry = []
Func_stack = None
Is_ret = False


