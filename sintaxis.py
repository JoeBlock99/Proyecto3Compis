import lexico

class Productions:
    def __init__(self, f, compiler):
        self.compiler = compiler
        self.tokens = []
        self.noterminals = self.getNoTerminals(f)
        self.productions = []
        self.firsts = {}
        self.new_tokens = {}
        self.extra = 1

        self.program = '''

class AnalisiSintactico():
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.currentToken = None
        self.nextToken = self.tokens[self.pos]
        self.next()
        self.lastvalue = None

        self.main()

    def coincidir(self, terminal):
        if self.currentToken == terminal:
            self.next()
        else:
            self.reportar('Error de sintaxis')

    def next(self):
        if self.pos - 1 < 0:
            self.lastvalue = None
        else:
            self.lastvalue = self.tokens[self.pos - 1][1]

        if self.nextToken == None:
            self.currentToken = None
        else:
            self.currentToken = self.nextToken[0]
        self.pos += 1

        if self.pos >= len(self.tokens):
            self.nextToken = None
        else:
            self.nextToken = self.tokens[self.pos]
        

    def reportar(self, msg):
        print(msg)

    def main(self):
        '''
        self.current = ''

    def getNoTerminals(self, lista):
        temp = ''
        productions = []
        noT = []
        for a in lista:
            c = a[:-1]
            words = c.split()
            if len(words) > 0:
                temp += c
                if c[-1] == '.' or temp == 'PRODUCTIONS':
                    productions.append(temp)
                    temp = ''
        productions.pop(0)
        for p in productions:
            production = p.split('=', 1)
            ident = production[0].split('<', 1)[0].replace(' ', '')

            noT.append(ident)
        return noT

    def getToken(self, token, value):
        if value != 'PRODUCTIONS' and token != 'white':
            self.tokens.append((token, value))

    def build(self):
        currentMethod = []
        expression = []
        parameters = []

        for token in self.tokens:
            t, v = [*token]
            if t == 'end_of_prod':
                self.productions.append(currentMethod)

                for i in range(len(currentMethod)):
                    if currentMethod[i][1] == '=':
                        if len(currentMethod[:i]) == 2:
                            parameters.append(currentMethod[1:i])
                        else:
                            parameters.append([])
                        expression.append(currentMethod[i + 1:])
                        break
                currentMethod = []
            else:
                currentMethod.append(token)

        for i in range(len(self.noterminals)):
            print(self.noterminals[i], parameters[i])
            print(expression[i])

        self.program += 'self.' + self.noterminals[0] + '()'
        new_strings = {}
        for i, item in enumerate(expression):
            for index, exp in enumerate(item):
                if exp[0] == 'string':
                    if exp[1][1:-1] not in new_strings.keys():
                        name = f'nuevo{self.extra}'
                        new_strings[exp[1][1:-1]] = name
                        self.extra += 1

                    expression[i][index] = ('ident', new_strings[exp[1][1:-1]])
        print('\nDESPUES:', new_strings)

        self.new_tokens = dict((y, x) for x, y in new_strings.items())

        for i in range(len(expression) - 1, 0, -1):
            first = self.calculateFirst(expression[i])
            noterminal = self.noterminals[i]
            self.firsts[noterminal] = first

        print(self.firsts)
        self.create_program(expression, parameters)

    def create_program(self, expression, parameters):
        for i in range(len(self.noterminals)):
            my_tokens = []
            print(self.noterminals[i], parameters[i])
            print(expression[i])

            for j in expression[i]:
                t = lexico.Token(j[0], j[1])
                my_tokens.append(t)

            analisislexico = lexico.DFA(my_tokens, self.firsts)


            prm_string = ''
            if len(parameters[i]) > 0:
                prm_string = ', '.join([p[1][1:-1] for p in parameters[i]])
                prm_string = ', ' + prm_string

            self.program += '\n\n    def ' + self.noterminals[i] + '(self' + prm_string + '):\n        ' + '\n        '.join(analisislexico.root[0])

        print(self.program)

        f = open(f'parser{self.compiler}.py', 'w', encoding='utf-8')
        f.write(self.program)
        f.close()

    def calculateFirst(self, production):
        first = []

        hasParenthesis = False
        hasSquare = False
        took = False

        for prod in production:
            token, value = [*prod]
            if token == 'end_parenthesis':
                hasParenthesis = False
                break
            elif token == 'end_optional':
                hasSquare = False

            if hasParenthesis:
                if took:
                    if token == 'union':
                        took = False
                else:
                    if token == 'ident' and value in self.noterminals:
                        took = True
                        first += self.firsts[value]
                    elif token == 'ident' and value not in self.noterminals:
                        took = True
                        first.append(value)
                    elif token == 'string':
                        took = True
                        first.append(value.replace('"', ''))
            elif hasSquare:
                if token == 'ident' and value in self.noterminals:
                    first += self.firsts[value]
                elif token == 'ident' and value not in self.noterminals:
                    first.append(value)
                elif token == 'string':
                    first.append(value.replace('"', ''))
            elif token == 'ident' and value in self.noterminals:
                first += self.firsts[value]
                break
            elif token == 'ident' and value not in self.noterminals:
                first.append(value)
                break
            elif token == 'string':
                first.append(value.replace('"', ''))
                break

            if token == 'start_parenthesis':
                hasParenthesis = True
            elif token == 'start_optional':
                hasSquare = True

        return first
        
