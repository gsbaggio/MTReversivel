import sys
import os

class ReversibleTuringMachine:
    def __init__(self):
        # aqui definimos as informações principais da MT reversível
        self.num_states = 0
        self.num_input_symbols = 0
        self.num_tape_symbols = 0
        self.num_transitions = 0
        
        self.states = [] # lista pra guardar os estados
        self.input_alphabet = [] # lista pra guardar o alfabeto de entrada
        self.tape_alphabet = [] # lista pra guardar o alfabeto da fita
        self.transitions_quintuple = {}  # dicionario pra guardar as transições em formato quintúpla
        self.transitions_quadruple = {}  # dicionario pra guardar as transições em formato quadrúpla
        
        self.input_string = "" # inicializa a string de entrada, que sera lida do arquivo
        
        # 3 fitas: input, history and output
        self.tapes = [[], [], []] # inicializa as 3 fitas como listas vazias
        self.heads = [0, 0, 0] # inicializa as posicoes das 3 cabeças das 3 fitas como posicao 0 (inicial)
        self.current_state = "1"  # define o estado atual como 1 (inicial)
    
    def read_input_file(self, filename): # func pra ler o entrada-quintupla.txt
        try:
            with open(filename, 'r') as file:
                lines = file.readlines() # le todas as linhas do arquivo, armazenando em uma lista (cada linha é um elemento da lista)
                
                params = lines[0].strip().split() # separa os parâmetros da primeira linha
                self.num_states = int(params[0]) # primeiro é o num de estados
                self.num_input_symbols = int(params[1]) # segundo num alfabeto de entrada
                self.num_tape_symbols = int(params[2]) # terceiro num alfabeto da fita
                self.num_transitions = int(params[3]) # quarto num de transições
                
                self.states = lines[1].strip().split() # a segunda linha do arquivo é a lista de estados
                
                self.input_alphabet = lines[2].strip().split() # a terceira linha do arquivo é o alfabeto de entrada

                self.tape_alphabet = lines[3].strip().split() # a quarta linha do arquivo é o alfabeto da fita
                
                for i in range(4, 4 + self.num_transitions): # da quarta linha em diante, le as transições
                    transition = lines[i].strip()

                    # separa os componentes da transição 
                    state, symbol, next_state, write, move = self.parse_quintuple(transition)

                    # armazena a transição no dicionário de quintúplas, com a chave sendo o par ÚNICO (estado, símbolo)
                    self.transitions_quintuple[(state, symbol)] = (next_state, write, move) 
                
                self.input_string = lines[4 + self.num_transitions].strip() # lê a input (i.e, '0011')
                
                return True
        except Exception as e:
            print(f"Erro ao tentar ler o arquivo de entrada 'entrada-quintupla.txt': {e}")
            return False
    
    def parse_quintuple(self, transition): # funcaozinha pra separar os componentes da transição (tirar ',', '()' e '=')
        left_side = transition.split('=')[0].strip('()')
        right_side = transition.split('=')[1].strip('()')
        
        current_state, read_symbol = left_side.split(',')
        next_state_data = right_side.split(',')
        next_state = next_state_data[0]
        write_symbol = next_state_data[1]
        direction = next_state_data[2]
        
        return (current_state, read_symbol, next_state, write_symbol, direction)
    
    def convert_to_quadruples(self): # converte as transições de quintúpla para quadrúpla
        for (state, symbol), (next_state, write, move) in self.transitions_quintuple.items():
            # o nome do estado intermediário é o estado atual seguido de um apóstrofo e o símbolo lido
            intermediate_state = f"{state}'{symbol}"
            
            # o dicionário de transições quadrúpla tem o par (estado, símbolo) como chave e o valor é uma tupla (estado intermediario, escrita)
            self.transitions_quadruple[(state, symbol)] = (intermediate_state, write)
            
            # segunda tupla: (estado intermediário, /) -> (próximo estado, movimento)
            # o '/' é porque nao lemos nada na fita 1, apenas movemos a cabeça
            self.transitions_quadruple[(intermediate_state, "/")] = (next_state, move)
    
    def write_quadruples_to_file(self, filename): # essa função é opcional, só escreve num arquivo
        try:
            with open(filename, 'w') as file:
                all_states = set(self.states)
                for state, _ in self.transitions_quadruple.keys():
                    if "'" in state: 
                        all_states.add(state)
                
                # escreve parametros
                file.write(f"{len(all_states)} {self.num_input_symbols} {self.num_tape_symbols+1} {len(self.transitions_quadruple)}\n")
                
                # escreve estados, incluindo os intermediários
                file.write(" ".join(sorted(all_states)) + "\n")
                
                # escreve alfabeto de entrada
                file.write(" ".join(self.input_alphabet) + "\n")
                
                # escreve alfabeto da fita, incluindo o '/' novo
                file.write(" ".join(self.tape_alphabet) + " /\n")
                
                # escreve as quadruplas
                for (state, symbol), (next_state, action) in sorted(self.transitions_quadruple.items()):
                    file.write(f"({state},{symbol})=({next_state},{action})\n")
                
                # escreve a string de entrada ('0011')
                file.write(self.input_string + "\n")
                
                return True
        except Exception as e:
            print(f"Erro ao tentar escrever o arquivo 'entrada-quadrupla.txt': {e}")
            return False
    
    def initialize_tapes(self):
        # todas as fitas tem tamanho 100, mas podem ser aumentadas se necessário
        self.tapes[0] = list(self.input_string) + ["B"] * 100 # fita de input começa com a entrada + B
        self.tapes[1] = ["B"] * 100 # fita de histórico começa com B's (vazia)
        self.tapes[2] = ["B"] * 100 # fita de output começa com B's (vazia)
    
    def simulate_forward(self): # primeira fase
        print("Começando a fase de execução (1ª fase)")
        print("-" * 60)
        
        final_state = self.states[-1]  # na MT reversivel, o último estado é o final
        steps = 0
        
        self.print_configuration()
        
        while self.current_state != final_state and steps < 1000:  # se a máquina etra em loop, para depois de 1000 passos
            if (self.current_state, "/") in self.transitions_quadruple: # isso entra quando o estado é intermediário
                next_state, action = self.transitions_quadruple[(self.current_state, "/")]
                    
                # coloca o estado intermediário na fita de histórico	
                self.tapes[1][self.heads[1]] = self.current_state
                self.heads[1] += 1  
                    
                # move o estado atual para o próximo estado
                self.current_state = next_state
                    
                # move a cabeça da fita de input
                if action == "R":
                    self.heads[0] += 1
                elif action == "L":
                    self.heads[0] = max(0, self.heads[0] - 1)
            else:
                # estado normal, sem ser intermediário
                current_symbol = self.tapes[0][self.heads[0]]
                
                # acha a transição correspondente no dicionário de transições quadrúpla
                if (self.current_state, current_symbol) in self.transitions_quadruple:
                    next_state, action = self.transitions_quadruple[(self.current_state, current_symbol)]
                    
                    # escreve o símbolo na fita de input
                    self.tapes[0][self.heads[0]] = action
                    
                    # move o estado atual para o próximo estado
                    self.current_state = next_state
                    
                else:
                    print(f"Sem transicao do estado {self.current_state} com o simbolo {current_symbol}")
                    return False
            
            steps += 1
            self.print_configuration()
        
        print(f"1ª fase de execucao normal terminada em {steps} passos")
        return True
    
    def simulate_copy(self, end_pos): # copia a fita de input para a fita de output
        print("\nComecando a fase de cópia (2ª fase)")
        print("-" * 60)
        
        # coloca as cabeças das fitas de input e output na posição inicial
        self.heads[0] = 0
        self.heads[2] = 0  
        
        self.print_configuration()
        
        # copia cada símbolo da fita de input para a fita de output até encontrar o símbolo 'B'
        while self.tapes[0][self.heads[0]] != "B":
            self.tapes[2][self.heads[2]] = self.tapes[0][self.heads[0]]
            self.heads[0] += 1
            self.heads[2] += 1  
            
            self.print_configuration()
        
        # coloca a cabeça da fita de output na posição final de onde ela parou
        self.heads[2] = end_pos
        print("Colocando a cabeca da output na posicao final:")
        self.print_configuration()
        
        print("2ª fase de cópia terminada")
        return True
    
    def simulate_retrace(self, input_pos, history_pos): # retrace
        print("\nComecando a fase de retrace (3ª fase)")
        print("-" * 60)
        
        # coloca as cabeças das fitas de input e histórico na posição inicial delas
        self.heads[0] = input_pos
        self.heads[1] = history_pos - 1 # history vai pro final
        
        self.print_configuration()
        
        steps = 0
        
        # continua até o estado for o '1' (inicial) ou a fita de histórico estiver vazia (ou entrar em loop)
        while self.current_state != "1" and self.heads[1] >= 0 and steps < 1000:
            if self.heads[1] >= 0 and self.tapes[1][self.heads[1]] != "B": # se não estiver lendo branco
                intermediate_state = self.tapes[1][self.heads[1]] # armazena o estado intermediário lido da fita de histórico
                
                # separa pelo apóstrofo, ex. "q1'$" -> ["q1", "$"]
                parts = intermediate_state.split("'")
                original_state = parts[0]
                original_symbol = parts[1]
                    
                # determina a direcao do movimento
                if (intermediate_state, "/") in self.transitions_quadruple:
                    _, direction = self.transitions_quadruple[(intermediate_state, "/")]
                    
                    # move na direcao contraria
                    if direction == "R":
                        # esquerda
                        if self.heads[0] > 0:
                            self.heads[0] -= 1
                    elif direction == "L":
                        # direita
                        self.heads[0] += 1
                    
                    # escreve o símbolo original na fita de input
                    self.tapes[0][self.heads[0]] = original_symbol
                        
                    # atualiza o estado
                    self.current_state = original_state
                else:
                    print(f"Erro: Sem estado de transicao encontrado para {intermediate_state}")
                    return False
                
                
                # limpa a primeira posição da fita de histórico (onde estava o estado intermediário)
                self.tapes[1][self.heads[1]] = "B"
                
                # coloca a cabeça da fita de histórico na posição do inicio
                self.heads[1] -= 1
                
                steps += 1
                self.print_configuration()
            else:
                break
        
        print(f"3ª fase de retrace terminada em {steps} passos")
        return True
    
    def print_configuration(self): # funcao auxiliar pra printar a configuração atual da máquina
        def format_tape(tape, head_pos):
            # mostra no minimo 11 simbolos total e maximo 10 antes da cabeça
            visible_range = range(max(0, head_pos - 10), min(len(tape), head_pos + 11)) 
            result = "... " if head_pos > 10 else "" # coloca os ... antes da cabeça se necessário
            
            for i in visible_range:
                if i == head_pos:
                    result += f"[{tape[i]}] "  # coloca a cabeça entre colchetes
                else:
                    result += f"{tape[i]} " # simbolo normal
            
            result = result.rstrip()  
            result += " ..." if head_pos + 10 < len(tape) and tape[head_pos + 10] != "B" else "" # coloca os ... no final se necessário
            return result
        
        print(f"Estado {self.current_state}")
        print(f"Fita 1 (Input):    {format_tape(self.tapes[0], self.heads[0])}")
        print(f"Fita 2 (History): {format_tape(self.tapes[1], self.heads[1])}")
        print(f"Fita 3 (Output):  {format_tape(self.tapes[2], self.heads[2])}")
        print("-" * 60)
    
    def simulate(self): # nossa função principal de simulação, chama as outras funções
        self.initialize_tapes()
        
        forward_success = self.simulate_forward() # primeira fase
        if not forward_success:
            return False
        
        # salva posições finais das fitas de input e histórico, pra chamar depois só
        forward_end_input_pos = self.heads[0]
        forward_end_history_pos = self.heads[1]
        
        copy_success = self.simulate_copy(forward_end_input_pos) # segunda fase
        if not copy_success:
            return False
        
        retrace_success = self.simulate_retrace(forward_end_input_pos, forward_end_history_pos) # terceira fase
        if not retrace_success:
            return False
        
        print(f"\n\n--> Saída na fita de Output: {''.join(symbol for symbol in self.tapes[2] if symbol != 'B')}")
        return True

def main():
    # pega o arquivo de entrada da máquina de Turing reversível (em formato de quintúpla)
    input_file = "entrada-quintupla.txt"
    
    # cria a classe da máquina de Turing reversível
    rtm = ReversibleTuringMachine()
    
    print(f"Carregando arquivo de entrada: {input_file}")
    if not rtm.read_input_file(input_file):
        print(f"Erro ao ler, arquivo inexistente ou invalido: {input_file}")
        return
    
    # converte em quadruplas
    rtm.convert_to_quadruples()
    
    # passa pra um arquivo opcional pra facilitar a leitura
    output_file = "entrada-quadrupla.txt"
    if rtm.write_quadruples_to_file(output_file):
        print(f"Quadruplas escritas para demonstracao em: {output_file}")
    
    # chama a função principal de simulação
    rtm.simulate()

if __name__ == "__main__":
    main()
