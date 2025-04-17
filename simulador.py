import sys

class Tape:
    def __init__(self, initial=[], blank='B', name="", track_head=False):
        self.tape = list(initial)
        self.head = 0
        self.blank = blank
        self.name = name
        self.track_head = track_head

    def read(self):
        if self.head < 0 or self.head >= len(self.tape):
            return self.blank
        return self.tape[self.head]

    def write(self, symbol):
        if self.head < 0:
            self.tape.insert(0, symbol)
            self.head = 0
        elif self.head >= len(self.tape):
            self.tape.append(symbol)
        else:
            self.tape[self.head] = symbol

    def move(self, direction):
        if direction == 'R':
            self.head += 1
        elif direction == 'L':
            self.head -= 1
        
        if self.head >= len(self.tape):
            self.tape.append(self.blank)
        elif self.head < 0:
            self.tape.insert(0, self.blank)
            self.head = 0

    def __str__(self):
        s = []
        for i, symbol in enumerate(self.tape):
            if i == self.head and self.track_head:
                s.append(f"[{symbol}]")
            else:
                s.append(symbol)
        return ' '.join(s).strip()

def main():
    lines = [line.strip() for line in sys.stdin if line.strip()]

    parts = lines[0].split()
    num_states = int(parts[0])
    num_input_symbols = int(parts[1])
    num_tape_symbols = int(parts[2])
    num_transitions = int(parts[3])

    states = lines[1].split()
    initial_state = states[0]
    final_state = states[-1]

    input_alphabet = lines[2].split()
    tape_alphabet = lines[3].split()
    blank = 'B'

    transitions = {}
    for line in lines[4:4+num_transitions]:
        line = line.replace('(', '').replace(')', '').replace(' ', '')
        lhs, rhs = line.split('=')
        q_from, read = lhs.split(',')
        q_to, write, move = rhs.split(',')
        transitions[(q_from, read)] = (q_to, write, move)

    input_str = lines[-1]

    input_tape = Tape(list(input_str), blank, "Entrada", track_head=True)
    history_tape = Tape([], blank, "Histórico")
    output_tape = Tape([], blank, "Saída")

    # fase 1, execução direta
    print("\n=== Fase 1: Execução Original ===")
    current_state = initial_state
    step = 0
    history = []

    while current_state != final_state:
        step += 1
        current_symbol = input_tape.read()

        key = (current_state, current_symbol)
        if key not in transitions:
            break

        q_to, write, move = transitions[key]

        history.append((current_state, current_symbol, write, move, input_tape.head))
        
        input_tape.write(write)
        input_tape.move(move)

        history_tape.write(current_state)
        history_tape.move('R')

        print(f"\nPasso {step} (Fase 1):")
        print(f"Estado Atual: {current_state} -> {q_to}")
        print(input_tape)
        print(history_tape)
        print(output_tape)

        current_state = q_to

    # fase 2, copiar para saída
    print("\n=== Fase 2: Copiar Saída ===")
    input_tape.head = 0
    step = 0
    
    while True:
        symbol = input_tape.read()
        if symbol == blank and input_tape.head >= len(input_tape.tape) - 1:
            output_tape.write(blank)
            output_tape.move('R')
            
            print(f"\nPasso {step + 1} (Fase 2):")
            print(input_tape)
            print(history_tape)
            print(output_tape)
            break
            
        step += 1
        output_tape.write(symbol)
        output_tape.move('R')
        input_tape.move('R')

        print(f"\nPasso {step} (Fase 2):")
        print(input_tape)
        print(history_tape)
        print(output_tape)

    # fase 3, reversão
    print("\n=== Fase 3: Reversão ===")
    step = 0
    
    for old_state, old_symbol, write, move, old_head in reversed(history):
        step += 1
        
        reverse_move = 'L' if move == 'R' else 'R'
        input_tape.move(reverse_move)
        
        input_tape.write(old_symbol)
        
        history_tape.head = max(0, history_tape.head - 1)
        if history_tape.head > 0:
            history_tape.write(blank)

        print(f"\nPasso {step} (Fase 3):")
        print(f"Revertendo de {old_state}")
        print(input_tape)
        print(history_tape)
        print(output_tape)

    print("\n=== Resultado Final ===")
    print("Fita 1 (Entrada):", input_tape)
    print("Fita 2 (Histórico):", history_tape)
    print("Fita 3 (Saída):", output_tape)

if __name__ == "__main__":
    main()