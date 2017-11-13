class machine:

    # T = [{('a', 1), ('b', 2)}, {}]

    def __init__(self, transform_table, end_state):
        self.T = transform_table
        self.E = end_state

    def check(self, text):
        state = 0
        for i in text:
            state = self.T[state][i]
            if not state:
                return False
        if state in self.E:
            return True
        else:
            return False

    def get(self, text, end):
        state = 0
        i = 0
        first = 0
        while text[i] not in end:
            try:
                state = self.T[state][text[i]]
            except KeyError:
                return '\x00'
            i += 1
            if text[i] in '+-' and first == 0:
                try:
                    state = self.T[state][text[i]]
                except KeyError:
                    return '\x00'
                i += 1
                first = 1
        try:
            state = self.T[state]['\x00']
        except KeyError:
            return '\x00'
        else:
            if state in self.E:
                return text[:i]
            else:
                return '\x00'
