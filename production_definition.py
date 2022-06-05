import sintaxis
import automata
epsilon = 'ε'

tokens = {
"ident":'˂A∪B∪C∪D∪E∪F∪G∪H∪I∪J∪K∪L∪M∪N∪O∪P∪Q∪R∪S∪T∪U∪V∪W∪X∪Y∪Z∪a∪b∪c∪d∪e∪f∪g∪h∪i∪j∪k∪l∪m∪n∪o∪p∪q∪r∪s∪t∪u∪v∪w∪x∪y∪z˃˂˂A∪B∪C∪D∪E∪F∪G∪H∪I∪J∪K∪L∪M∪N∪O∪P∪Q∪R∪S∪T∪U∪V∪W∪X∪Y∪Z∪a∪b∪c∪d∪e∪f∪g∪h∪i∪j∪k∪l∪m∪n∪o∪p∪q∪r∪s∪t∪u∪v∪w∪x∪y∪z˃∪˂0∪1∪2∪3∪4∪5∪6∪7∪8∪9˃˃Δ',
"equivalence":'˂=˃',
"end_of_prod":'˂.˃',
"start_kleene":'˂{˃',
"end_kleene":'˂}˃',
"start_optional":'˂[˃',
"end_optional":'˂]˃',
"start_parenthesis":'˂(˃',
"end_parenthesis":'˂)˃',
"union":'˂|˃',
"attr":'˂<˃˂˂X∪P∪k∪:∪O∪%∪/∪}∪U∪\t∪S∪Q∪r∪D∪9∪\\∪@∪G∪C∪W∪p∪b∪R∪8∪e∪\'∪v∪F∪\r∪(∪u∪d∪"∪f∪!∪+∪j∪ ∪y∪E∪K∪Z∪]∪T∪>∪=∪6∪g∪`∪{∪c∪H∪n∪^∪M∪4∪V∪0∪7∪I∪a∪m∪w∪1∪s∪[∪*∪,∪;∪q∪.∪~∪_∪t∪&∪)∪h∪l∪3∪z∪Y∪#∪A∪i∪<∪-∪?∪$∪o∪5∪x∪2∪B∪|∪J∪L∪N˃˃Δ˂>˃',
"semantic_action":'˂(.˃˂˂X∪P∪k∪:∪O∪%∪/∪}∪U∪\t∪S∪Q∪r∪D∪9∪\\∪@∪G∪C∪W∪p∪b∪R∪8∪e∪\'∪v∪F∪\r∪(∪u∪d∪"∪f∪!∪+∪j∪ ∪y∪E∪K∪Z∪]∪T∪>∪=∪6∪g∪`∪{∪c∪H∪n∪^∪M∪4∪V∪0∪7∪I∪a∪m∪w∪1∪s∪[∪*∪,∪;∪q∪.∪~∪_∪t∪&∪)∪h∪l∪3∪z∪Y∪#∪A∪i∪<∪-∪?∪$∪o∪5∪x∪2∪B∪|∪J∪L∪N˃˃Δ˂.)˃',
"string":'˂\\∪"˃˂˂X∪P∪k∪:∪O∪%∪/∪}∪U∪\t∪S∪Q∪r∪D∪9∪@∪G∪C∪W∪\n∪p∪b∪R∪8∪e∪\'∪v∪F∪\r∪(∪u∪d∪f∪!∪+∪j∪ ∪y∪E∪K∪Z∪]∪T∪>∪=∪6∪g∪`∪{∪c∪H∪n∪^∪M∪4∪V∪0∪7∪I∪a∪m∪w∪1∪s∪[∪*∪,∪;∪q∪.∪~∪_∪t∪&∪)∪h∪l∪3∪z∪Y∪#∪A∪i∪<∪-∪?∪$∪o∪5∪x∪2∪B∪|∪J∪L∪N˃˃Δ˂\\∪"˃',
"white":'˂\n∪\r∪\t∪ ˃˂˂\n∪\r∪\t∪ ˃˃Δ',
}

exceptions = {
"ident": {},
"equivalence": {},
"end_of_prod": {},
"start_kleene": {},
"end_kleene": {},
"start_optional": {},
"end_optional": {},
"start_parenthesis": {},
"end_parenthesis": {},
"union": {},
"attr": {},
"semantic_action": {},
"string": {},
"white": {},
}

ignores = []

acceptable_characters = []

class ProductionDefinition():
    def __init__(self, tokens, lines, compiler):
        self.all_tokens = tokens
        self.lines = lines
        self.compiler = compiler
        print('EXISTING TOKENS:', tokens)
        self.new_tokens = {}
        self.parser()        

    def parser(self):
        for k, v in tokens.items():
            for i in v:
                if i not in '˂˃∪ƷΔ∩' and i not in acceptable_characters:
                    acceptable_characters.append(i)

        exp = '∪'.join(['˂˂' + token + '˃∫˃' for token in tokens.values()])

        lines = self.lines
        w = ''.join(lines)
        productions = sintaxis.Productions(lines, self.compiler)

        syntax = automata.SyntaxTree(exp, acceptable_characters, [t for t in tokens.keys()])

        pos = 0
        while pos < len(w):
            resultado, pos, aceptacion = syntax.Simulate_DFA(w, pos, ignores)
            if aceptacion:
                permitido = True
                for excepcion in exceptions[syntax.tokens[aceptacion]].keys():
                    if resultado == excepcion:
                        permitido = False
                        print(repr(excepcion), ' = ', exceptions[syntax.tokens[aceptacion]][excepcion])
                        break

                if permitido:
                    if syntax.tokens[aceptacion] not in ignores:
                        print(repr(resultado), ' = ', syntax.tokens[aceptacion])
                        productions.getToken(syntax.tokens[aceptacion], resultado)
            else:
                if resultado != '':
                    print(repr(resultado), ' = caracter inesperado')
        productions.build()
        self.new_tokens = productions.new_tokens
