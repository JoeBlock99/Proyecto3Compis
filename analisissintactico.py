import re
import proy3

pipe = chr(8746) # ∪
concat = chr(8745) # ∩
star = chr(916) # Δ
left = chr(706) # ˂
right = chr(707) # ˃
question = chr(439) # Ʒ
hashtag = chr(8747) # ∫


class AnalisisLexico():
    def __init__(self, config):
        self.compiler = None
        self.characters = {}
        self.keywords = {}
        self.tokens = {}
        self.productions = []
        self.ignores = []
        self.noterminals = []

        self.parse(config)

    def precedence(self, op):
        if op == '+' or op == '-':
            return 1
        return 0
    
    def applyOp(self, a, b, op):
        if op == '+': return self.union(a, b)
        if op == '-': return self.difference(a, b)

    def union(self, a, b):
        res = a + pipe + b
        res = pipe.join(list(dict.fromkeys(res.split(pipe))))
        return res
    
    def difference(self, a, b):
        return pipe.join(list(set(a.split(pipe)) - set(b.split(pipe))))

    def evaluate(self, tokens):
        values = []
        ops = []
        i = 0
        
        last = 0
        for i in range(len(tokens) - 2):
            if tokens[i:i+3] == ' - ' or tokens[i:i+3] == ' + ':
                ops.insert(0, tokens[i+1])
                values.insert(0, tokens[last + 1:i - 1])
                last = i + 3
        values.insert(0, tokens[last + 1:-1])

        while len(ops) != 0:
            val1 = values.pop()
            val2 = values.pop()
            op = ops.pop()
                    
            values.append(self.applyOp(val1, val2, op))
        return values[-1]

    def parse(self, config):
        compiler = None
        characters = []
        keywords = []
        tokens = []
        productions = []
        ignores = []
        
        isCompiler = False
        isCharacters = False
        isKeywords = False
        isTokens = False
        isProductions = False

        temp = ''
        for c in config_file:
            words = c.split()
            if len(words) > 0:
                if words[0].lower() == 'compiler':
                    isCompiler = True
                    isCharacters = False
                    isKeywords = False
                    isTokens = False
                    isProductions = False
                elif words[0].lower() == 'characters':
                    isCompiler = False
                    isCharacters = True
                    isKeywords = False
                    isTokens = False
                    isProductions = False
                elif words[0].lower() == 'keywords':
                    isCompiler = False
                    isCharacters = False
                    isKeywords = True
                    isTokens = False
                    isProductions = False
                elif words[0].lower() == 'tokens':
                    isCompiler = False
                    isCharacters = False
                    isKeywords = False
                    isTokens = True
                    isProductions = False
                elif words[0].lower() == 'productions':
                    isCompiler = False
                    isCharacters = False
                    isKeywords = False
                    isTokens = False
                    isProductions = True
                elif words[0] == 'IGNORE':
                    ignores.append(words[1])
                    isCompiler = False
                    isCharacters = False
                    isKeywords = False
                    isTokens = False
                    isProductions = False
                elif words[0].lower() == 'end':
                    break

                if isCompiler:
                    compiler = words[1]
                    isCompiler = False
                elif isCharacters:
                    characters.append(c)
                elif isKeywords:
                    keywords.append(c)
                elif isTokens:
                    temp += c
                    if c[-1] == '.' or temp == 'TOKENS':
                        tokens.append(temp)
                        temp = ''
                elif isProductions:
                    temp += c
                    if c[-1] == '.' or temp == 'PRODUCTIONS':
                        productions.append(temp)
                        temp = ''

        if len(characters) > 0:
            characters.pop(0)
        
        if len(keywords) > 0:
            keywords.pop(0)

        if len(tokens) > 0:
            tokens.pop(0)

        if len(productions) > 0:
            productions.pop(0)

        print('---------------------- CHARACTERS ------------------------------------------------------')
        for p in characters:
            print(p)
        print('---------------------- TOKENS----------------------------------------------------------')
        for p in tokens:
            print(p)
        print('----------------------- PRODUCTIONS -----------------------------------------------')
        for p in productions:
            print(' >', p)
        
        self.compiler = compiler
        self.buildCharacters(characters)

        for i in ignores:
            ignore = self.characters[i]
            ignore = ignore.replace(left, '')
            ignore = ignore.replace(right, '')
            self.ignores += ignore.split(pipe)

        self.buildKeywords(keywords)
        self.buildTokens(tokens)
        self.buildProductions(productions)
        
    def rango_chars(self, a, b):
        for c in range(ord(a), ord(b) + 1):
            yield chr(c)
    
    def buildCharacters(self, characters):
        numbers = list(range(9, 11)) + list(range(13, 14)) + list(range(32, 127))
        any_array = '˂' + pipe.join(chr(i) for i in numbers) + '˃'

        pattern = '(CHR\([0-9]*\))'
        for i in range(len(characters)):
            matches = re.findall(pattern, characters[i])
            newCharacter = characters[i]
            for m in matches:
                newCharacter = newCharacter.replace(m, "'" + eval(m.lower()) + "'" if eval(m.lower()) == '"' else '"' + eval(m.lower()) + '"')

            characters[i] = newCharacter

        self.characters['ANY'] = any_array

        for char in characters:
            character = char.split('=', 1)

            isApostrophe = False 
            isQuote = False 
            last = 0
            new = ''

            aEvaluar = character[1]

            final = ''
            for i in range(len(aEvaluar)):
                text = ''
                if aEvaluar[i] == '"' and not isQuote and not isApostrophe:
                    isQuote = True
                    last = i + 1

                elif aEvaluar[i] == '"' and isQuote:
                    isQuote = False
                    isApostrophe = False
                    new = aEvaluar[last:i]

                    for i in range(len(new)):
                        if i < len(new) - 1:
                            text += new[i] + pipe
                        else:
                            text += new[i]

                    final += '˂' + text + '˃'

                elif aEvaluar[i] == "'" and not isApostrophe and not isQuote:
                    isApostrophe = True
                    last = i + 1

                elif aEvaluar[i] == "'" and isApostrophe:
                    isQuote = False
                    isApostrophe = False
                    new = aEvaluar[last:i]

                    for i in range(len(new)):
                        if i < len(new) - 1:
                            text += new[i] + pipe
                        else:
                            text += new[i]

                    final += '˂' + text + '˃'

                elif aEvaluar[i] == '+' and not isApostrophe and not isQuote:
                    final += ' + '
                
                elif aEvaluar[i] == '-' and not isApostrophe and not isQuote:
                    final += ' - '

                elif not isApostrophe and not isQuote and aEvaluar[i] != ' ':
                    final += aEvaluar[i]
            self.characters[character[0].replace(' ', '')] = final[:-1]

        for key, value in self.characters.items():
            result = ''

            if '..' in value:
                index = value.find('..')
                a = value[1:index-1]
                b = value[index+3:-1]
                resultadoA = chr(int(a[4:-1])) if a.find('CHR(') == 0 else a.replace("'", "")
                resultadoB = chr(int(b[4:-1])) if b.find('CHR(') == 0 else b.replace("'", "")

                for j in self.rango_chars(a, b):
                    if j != b:
                        result += j + pipe
                    else:
                        result += j
                self.characters[key] = '˂' + result + '˃'
        
        llaves = list(self.characters.keys())
        valores = list(self.characters.values())
        for i in range(len(llaves) - 1):
            for j in range(i + 1, len(llaves)):
                if llaves[i] in self.characters[llaves[j]]:
                    self.characters[llaves[j]] = self.characters[llaves[j]].replace(llaves[i], self.characters[llaves[i]])

        for key, value in self.characters.items():
            result = self.evaluate(value)
            self.characters[key] = '˂' + result + '˃'


    def buildKeywords(self, keywords):
        for kw in keywords:
            kw = kw.replace(' ', '')
            keyword, word = kw.split('=')
            word = word[:-1]
            
            self.keywords[word.replace('"', '')] = keyword.replace('"', '')

    def buildTokens(self, tokens):
        listCharacters = list(self.characters.keys())
        listCharacters.sort(key = len)
        listCharacters.reverse()

        for token in tokens:
            token_ = token.split('=', 1)

            isQuote = False
            last = 0
            new = ""

            ident = token_[0].replace(' ', '')
            aEvaluar = token_[1]
            final = ""
            for i in range(len(aEvaluar)):
                text = ""
                if aEvaluar[i] == '"' and not isQuote:
                    isQuote = True
                    last = i + 1

                elif aEvaluar[i] == '"' and isQuote:
                    isQuote = False
                    isApostrophe = False
                    new = aEvaluar[last:i]

                    for i in range(len(new)):
                        text += new[i]

                    final += left + text + right

                elif not isQuote and aEvaluar[i] != ' ':
                    final += aEvaluar[i]

            final = final.replace('|', pipe)
            self.tokens[ident] = {}
            self.tokens[ident]['expresion'] = final[:-1]
            self.tokens[ident]['except'] = {}

        for key, value in self.tokens.items():
            if 'EXCEPT' in value['expresion']:
                exceptions = value['expresion'].split('EXCEPT')
                self.tokens[key]['expresion'] = exceptions[0]

                if exceptions[1].replace('.', '') == 'KEYWORDS':
                    self.tokens[key]['except'] = self.keywords

            if '{' in value['expresion'] and '}' in value['expresion']:
                self.tokens[key]['expresion'] = self.tokens[key]['expresion'].replace('{', '˂')
                self.tokens[key]['expresion'] = self.tokens[key]['expresion'].replace('}', '˃Δ')

            if '[' in value['expresion'] and ']' in value['expresion']:
                self.tokens[key]['expresion'] = self.tokens[key]['expresion'].replace('[', '˂')
                self.tokens[key]['expresion'] = self.tokens[key]['expresion'].replace(']', '˃Ʒ')

        for key, value in self.tokens.items():
            newToken = value['expresion']
            for character in listCharacters:
                if character in value['expresion']:
                    newToken = newToken.replace(character, self.characters[character])

            value['expresion'] = newToken


    def buildProductions(self, productions):
        noterminales = []

        for p in productions:
            production = p.split('=', 1)
            ident = production[0].split('<', 1)[0].replace(' ', '')
            noterminales.append(ident)
            
        self.noterminals = noterminales
        print('\nNO TERMINALES:', self.noterminals)

config_file = []

archivo = input('Ingrese el nombre del archivo ATG: ')

with open(archivo, 'r') as reader:
    for line in reader:
        if line != '\n':
            config_file.append(line.strip())


analisislexico = AnalisisLexico(config_file)


filee = open(archivo, 'r', encoding='utf-8', errors='replace')
lines = filee.readlines()
for i in range(len(lines)):
    if 'PRODUCTIONS' in lines[i]:
        break

contenido_productions = lines[i:-1]
p3 = proy3.Proyecto3(list(analisislexico.tokens.keys()), contenido_productions, analisislexico.compiler)

tokens_program = ''
exception_program = ''

for key, value in analisislexico.tokens.items():
    tokens_program += '"' + key + '":' + repr(value['expresion']) + ',\n'
    exception_program += '"' + key + '": ' + str(value['except']) + ',\n'

for x, y in p3.new_tokens.items():
    tokens_program += '"' + x + '":' + repr(y) + ',\n'
    exception_program += '"' + x + '": {},\n'


programa_completo = '''import automata
import parser''' + analisislexico.compiler + ''' as pf
epsilon = 'ε'

tokens = {
''' + r'{}'.format(tokens_program) + '''}

exceptions = {
''' + f'{exception_program}' + '''}

ignores = ''' + f'{analisislexico.ignores}' + '''

acceptable_characters = []
for k, v in tokens.items():
    for i in v:
        if i not in '˂˃∪ƷΔ∩' and i not in acceptable_characters:
            acceptable_characters.append(i)

exp = '∪'.join(['˂˂' + token + '˃∫˃' for token in tokens.values()])

archivo = input('Ingrese el nombre del archivo a escanear: ')
filee = open(archivo, 'r', encoding='utf-8', errors='replace')
lines = filee.readlines()
w = ''.join(lines)

syntax = automata.DFA(exp, acceptable_characters, [t for t in tokens.keys()])
tokens = []

pos = 0
while pos < len(w):
    resultado, pos, aceptacion = syntax.Simulate_DFA(w, pos, ignores)
    if aceptacion:
        permitido = True
        for excepcion in exceptions[syntax.tokens[aceptacion]].keys():
            if resultado == excepcion:
                permitido = False
                print('     ', repr(excepcion), 'es el keyword', exceptions[syntax.tokens[aceptacion]][excepcion])
                break

        if permitido:
            if syntax.tokens[aceptacion] not in ignores:
                print('     ', repr(resultado), 'es', syntax.tokens[aceptacion])
                tokens.append((syntax.tokens[aceptacion], resultado))
    else:
        if resultado != '':
            print('     ', repr(resultado), 'es un token inesperado')
print('\\n\\nTOKENS:')
print(tokens)
pf.AnalisiSintactico(tokens)
'''

f = open(f'scanner{analisislexico.compiler}.py', 'w', encoding='utf-8')
f.write(programa_completo)
f.close()




