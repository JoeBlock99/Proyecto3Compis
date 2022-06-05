import functools
epsilon = 'ε'

class Token():
    def __init__(self, attr, value):
        self.Atributo = attr
        self.Valor = value


class SyntaxTree():
    def __init__(self, regular_expression, firsts):
        
        self.firsts = firsts
        self.tabs = 0
        self.last_operation = None
        self.simbolos = []
        
        self.nodos = []
        self.root = None
        self.id = 0

        self.follow_pos = {}
        regular_expression = self.concatenation(regular_expression)

        self.evaluate(regular_expression)

    def calculate_first(self, ident):
        if ident in self.firsts.keys():
            return self.firsts[ident]
        else:
            return [ident]

    def get_first(self, left, right, operator):
        if operator == 'concat':
            if left.Atributo == 'ident':
                return self.calculate_first(left.Valor)
            elif right.Atributo == 'ident':
                return self.calculate_first(right.Valor)
            else:
                return []
        elif operator == 'union':
            return self.calculate_first(left.Valor) + self.calculate_first(right.Valor)

    def concatenation(self, expresion):
        new = []
        operators = ['{', '|','(', '[', '}', ']', ')']
        cont = 0

        for cont in range(len(expresion)):
            if cont + 1 >= len(expresion):
                new.append(expresion[-1])
                break

            new.append(expresion[cont])

            if expresion[cont].Valor == '}' and expresion[cont + 1].Valor in '({[]}':
                new.append(Token('concat', '.'))
            elif expresion[cont].Valor not in operators and expresion[cont+1].Valor not in operators:
                new.append(Token('concat', '.'))
            elif expresion[cont].Valor not in operators and expresion[cont+1].Valor in '([':
                new.append(Token('concat', '.'))
            elif expresion[cont].Valor == ')' and expresion[cont+1].Valor not in operators:
                new.append(Token('concat', '.'))
        return new

    def peek(self, stack):
        return stack[-1] if stack else None

    def is_symbol(self, s):
        tokens = ['ident', 'attr', 'semantic_action', 'string', 'white']
        if s.Atributo in tokens:
            return True
        return False

    def get_id(self):
        self.id += 1
        return self.id

    def apply_operator(self, operators, values):
        operator = operators.pop()

        if len(values) == 1 and operator.Atributo == 'end_kleene':
            right = ([], [])
        else:
            right = values.pop()

        if len(values) == 0:
            left = ([], [])
        else:
            left = values.pop()
        
        if operator.Atributo == 'union': return self.operator_or(left, right)
        elif operator.Atributo == 'concat': return self.operator_concat(left, right)
        elif operator.Atributo == 'start_kleene': return self.operator_kleene(left, right)
        elif operator.Atributo == 'end_kleene': return self.operator_kleene_close(left, right)
        elif operator.Atributo == 'start_optional': return self.operator_square(left, right)
        elif operator.Atributo == 'end_optional': return self.operator_square_close(left, right)

    def operator_square(self, left, right):
        first = root = []

        if isinstance(left, tuple):
            root = left[0]
        else:
            self.tabs -= 1
            if left.Atributo == 'semantic_action':
                root = ['\t' * self.tabs + left.Valor[2:-2]]
            elif left.Atributo == 'ident' and left.Valor in self.firsts.keys():
                root = ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[left.Valor]) + ':']
                root += ['\t' * self.tabs + '\tself.' + left.Valor + '()']
                self.tabs += 1
            elif left.Atributo == 'ident' and left.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + left.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + left.Valor + '")']

        if isinstance(right, tuple):
            self.tabs -= 1
            root += ['\t' * self.tabs + 'if self.currentToken in ' + repr(right[1]) + ':'] + ['\t' + i for i in right[0]]
        else:
            root += ['\t' * self.tabs + 'if self.currentToken in ["' + right.Valor + '"]:'] + ['\t' * self.tabs + '\tself.coincidir("' + right.Valor + '")']
        return (root, first)

    def operator_square_close(self, left, right):
        first = []
        self.tabs -= 1

        if isinstance(right, tuple):
            root = left[0] + right[0]
        else:
            root = left[0]
            if right.Atributo == 'semantic_action':
                root += ['\t' * self.tabs + right.Valor[2:-2]]
            elif right.Atributo == 'ident' and right.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[right.Valor])]
                root += ['\t' * self.tabs +  '\tself.' + right.Valor + '()']
            elif right.Atributo == 'ident' and right.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + right.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + right.Valor + '")']

        return (root, first)

    def operator_kleene(self, left, right):
        first = []
        root = []

        if isinstance(left, tuple):
            root = left[0]
        else:
            self.tabs -= 1
            if left.Atributo == 'semantic_action':
                root = ['\t' * self.tabs + left.Valor[2:-2]]
            elif left.Atributo == 'ident' and left.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[left.Valor]) + ':']
                root = ['\t' * self.tabs + '\tself.' + left.Valor + '()']
                self.tabs += 1
            elif left.Atributo == 'ident' and left.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + left.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + left.Valor + '")']
            self.tabs += 1

        if isinstance(right, tuple):
            self.tabs -= 2
            root += ['\t' * self.tabs + 'while self.currentToken in ' + repr(right[1]) + ':'] + ['\t' + i for i in right[0]]
            self.tabs += 1
        else:
            root += ['\t' * self.tabs + 'while self.currentToken in ["' + right.Valor + '"]:'] + ['\t' * self.tabs + '\tself.coincidir("' + right.Valor + '")']
        return (root, first)

    def operator_kleene_close(self, left, right):
        first = []
        self.tabs -= 1

        if isinstance(right, tuple):
            root = left[0] + right[0]
        else:
            root = left[0]
            if right.Atributo == 'semantic_action':
                root += ['\t' * self.tabs + right.Valor[2:-2]]
            elif right.Atributo == 'ident' and right.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[right.Valor])]
                root += ['\t' * self.tabs +  '\tself.' + right.Valor + '()']
            elif right.Atributo == 'ident' and right.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + right.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + right.Valor + '")']

        return (root, first)

    def operator_or(self, left, right):
        operator = 'union'
        
        if isinstance(left, tuple) and isinstance(right, tuple):
            self.tabs -= 1
            root = left[0] + ['else:'] + right[0]
            self.tabs -= 1
            return (root, left[1] + right[1])

        elif not isinstance(left, tuple) and not isinstance(right, tuple):
            root = []
            first = self.get_first(left, right, operator)

            if left.Atributo == 'ident' and left.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[left.Valor])]
                root += ['\t' * self.tabs +  '\tself.' + right.Valor + '()']
            elif left.Atributo == 'ident' and left.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + left.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + left.Valor + '")']

            if right.Atributo == 'ident' and right.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'elif self.currentToken in ' + repr(self.firsts[right.Valor])]
                root += ['\t' * self.tabs +  '\tself.' + right.Valor + '()']
            elif right.Atributo == 'ident' and right.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'elif self.currentToken == "' + right.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + right.Valor + '")']
                        
            self.tabs -= 1
            return (root, first)

        elif isinstance(left, tuple) and not isinstance(right, tuple):
            root = left[0] + ['else:']
            first = left[1]

            if right.Atributo == 'ident' and right.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[right.Valor])]
                root += ['\t' * self.tabs +  '\tself.' + right.Valor + '()']
                first += self.firsts[right.Valor]
            elif right.Atributo == 'ident' and right.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + right.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + right.Valor + '")']
                first += [right.Valor]

            self.tabs -= 1
            return (root, first)

        elif not isinstance(left, tuple) and isinstance(right, tuple):
            root = []
            first = right[1]
            self.tabs -= 1

            if left.Atributo == 'ident' and left.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[left.Valor])]
                root += ['\t' * self.tabs +  '\tself.' + right.Valor + '()']
                first += self.firsts[left.Valor]
            elif left.Atributo == 'ident' and left.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + left.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + left.Valor + '")']
                first += [left.Valor]

            root += ['else:'] + ['\t' + r for r in right[0]]

            self.tabs -= 1
            return (root, first)

    def operator_concat(self, left, right):
        operator = 'concat'
        first = []
        if isinstance(left, tuple) and isinstance(right, tuple):
            root = left[0] + right[0]
            first = left[1]
            return (root, first)

        elif not isinstance(left, tuple) and not isinstance(right, tuple):
            root = []

            first = self.get_first(left, right, operator)
            if left.Atributo == 'semantic_action':
                root += ['\t' * self.tabs + left.Valor[2:-2]]
            elif left.Atributo == 'ident' and left.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[left.Valor]) + ':']
                root += ['\t' * self.tabs + '\tself.' + left.Valor + '()']
                self.tabs += 1
            elif left.Atributo == 'ident' and left.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + left.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + left.Valor + '")']
                self.tabs += 1
           
            if right.Atributo == 'semantic_action':
                root += ['\t' * self.tabs + right.Valor[2:-2]]
            elif right.Atributo == 'ident' and right.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'self.' + right.Valor + '()']
            elif right.Atributo == 'ident' and right.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + right.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + right.Valor + '")']
                self.tabs += 1
            elif right.Atributo == 'attr':
                x = root[-1][:-2].rfind('\t')
                root[-1] = root[-1][:-2][:x + 1] + right.Valor[1:-1] + ' = ' + root[-1][:-2][x + 1:] + '(' + right.Valor[1:-1] + ')'

            return (root, first)

        elif isinstance(left, tuple) and not isinstance(right, tuple):
            root = left[0]
            first = left[1]

            if right.Atributo == 'semantic_action':
                root += ['\t' * self.tabs + right.Valor[2:-2]]
            elif right.Atributo == 'ident' and right.Valor in self.firsts.keys():
                root += ['\t' * self.tabs + 'self.' + right.Valor + '()']
            elif right.Atributo == 'ident' and right.Valor not in self.firsts.keys():
                root += ['\t' * self.tabs + 'if self.currentToken == "' + right.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + right.Valor + '")']
                self.tabs += 1
            elif right.Atributo == 'attr':
                x = root[-1][:-2].rfind('\t')
                root[-1] = root[-1][:-2][:x + 1] + right.Valor[1:-1] + ' = ' + root[-1][:-2][x + 1:] + '(' + right.Valor[1:-1] + ')'

            return (root, first)
        
        elif not isinstance(left, tuple) and isinstance(right, tuple):
            root = right[0]

            if left.Atributo == 'semantic_action':
                root = ['\t' * self.tabs + left.Valor[2:-2]] + root
                first = right[1]
            elif left.Atributo == 'ident' and left.Valor in self.firsts.keys():
                root = ['\t' * self.tabs + 'if self.currentToken in ' + repr(self.firsts[left.Valor]) + ':']
                root += ['\t' * self.tabs + '\tself.' + left.Valor + '()'] + right[0]
                self.tabs += 1
                first = self.calculate_first(left.Valor)
            elif left.Atributo == 'ident' and left.Valor not in self.firsts.keys():
                root = ['\t' * self.tabs + 'if self.currentToken == "' + left.Valor + '":']
                root += ['\t' * self.tabs + '\tself.coincidir("' + left.Valor + '")'] + right[0]
                first = [left.Valor]
                self.tabs += 1
            return (root, first)

    def greater_precedence(self, op1, op2):
        precedences = {
            'union' : 2,
            'concat' : 3,
            'start_kleene' : 1,
            'end_kleene': 0,
            'start_optional' : 1,
            'end_optional': 0
        }
        return precedences[op1] >= precedences[op2]
    
    def evaluate(self, expression):
        values = []
        operators = []
        for token in expression:
            if self.is_symbol(token):
                values.append(token)

            elif token.Atributo == 'start_parenthesis':
                operators.append(token)

            elif token.Atributo == 'end_parenthesis':
                top = self.peek(operators)

                while top is not None and top.Atributo != 'start_parenthesis':
                    raiz = self.apply_operator(operators, values)
                    values.append(raiz)
                    top = self.peek(operators)
                operators.pop()
                self.tabs -= 1

            else:
                top = self.peek(operators)

                while top is not None and top.Atributo not in ['start_parenthesis', 'end_parenthesis'] and self.greater_precedence(top.Atributo, token.Atributo):
                    raiz = self.apply_operator(operators, values)
                    values.append(raiz)
                    top = self.peek(operators)
                operators.append(token)

        while self.peek(operators) is not None:
            raiz = self.apply_operator(operators, values)
            values.append(raiz)

        self.root = values.pop()