import Symbols

Grammar = {
    'Program': [
        ['type', 'symbol', 'action_declare', 'Nextpro', 'Program'],
        '\x00'
    ],
    'Nextpro': [
        ['Func'],
        ['Dec']
    ],
    'Func': [
        ['(', 'action_func_start', 'Vars', ')', '{', 'Text', 'action_func_end', '}']
    ],
    'Vars': [
        ['type', 'symbol', 'action_func_para', 'Nextvar'],
        '\x00'
    ],
    'Nextvar': [
        [',', 'type', 'symbol', 'action_func_para', 'Nextvar'],
        '\x00'
    ],
    'Dec': [
        ['Equal_Biao', 'action_equal', 'Nextdec'],
        [';']
    ],
    'Nextdec': [
        [',', 'symbol', 'action_declare', 'Dec'],
        [';']
    ],
    'Text': [
        ['type', 'symbol', 'action_declare', 'Dec', 'Text'],
        ['Equal', 'Text'],
        '\x00'
    ],
    'Equal': [
        ['symbol', 'Equal_Biao', 'action_equal', 'NextEqual', ';']
    ],
    'NextEqual': [
        [',', 'symbol', 'Equal_Biao', 'action_equal', 'NextEqual'],
        '\x00'
    ],
    'Equal_Biao': [
        ['=', 'Biao'],
    ],
    'Biao': [
        ['T', 'E1']
    ],
    'E1': [
        ['w0', 'T', 'action_add', 'E1'],
        '\x00'
    ],
    'T': [
        ['F', 'T1']
    ],
    'T1': [
        ['w1', 'F', 'action_mul', 'T1'],
        '\x00'
    ],
    'F': [
        ['I'],
        ['(', 'Biao', ')']
    ],
    'I': [
        ['symbol'],
        ['constant']
    ]
}

Start = 'Program'
End = Symbols.Delimiter_table + ['symbol', 'constant', 'type', 'w0', 'w1']