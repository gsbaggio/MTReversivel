# em fases iniciais de teste!

import sys

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
    blank_symbol = 'B'  # BRANCO

    transitions = {}
    for line in lines[4:4+num_transitions]:
        line = line.replace('(', '').replace(')', '').replace(' ', '')
        lhs, rhs = line.split('=')
        q_current, read_symbol = lhs.split(',')
        q_next, write_symbol, direction = rhs.split(',')
        transitions[(q_current, read_symbol)] = (q_next, write_symbol, direction)

    input_string = lines[-1]

    input_tape = list(input_string)
    history = []  
    original_input = list(input_string) 

    # fase 1, computação original
    current_state = initial_state
    head = 0

    while current_state != final_state:
        if head < 0 or head >= len(input_tape):
            current_symbol = blank_symbol
        else:
            current_symbol = input_tape[head]

        key = (current_state, current_symbol)
        if key not in transitions:
            break  

        next_state, write_symbol, direction = transitions[key]

        history.append( (current_symbol, write_symbol, direction, head) )

        if head < 0:
            pass
        elif head >= len(input_tape):
            input_tape.append(write_symbol)
            head += 1
        else:
            input_tape[head] = write_symbol

        if direction == 'R':
            head += 1
        else:
            head -= 1

        current_state = next_state

        if head >= len(input_tape):
            input_tape.append(blank_symbol)
        elif head < 0:
            head = 0
            input_tape.insert(0, blank_symbol)

    # fase 2, copia input tape para output tape
    output_tape = input_tape.copy()

    # fase 3, restaura a fita de entrada e limpa o histórico
    for entry in reversed(history):
        read_symbol, write_symbol, direction, old_head = entry

        head = old_head

        if head >= len(input_tape):
            input_tape.append(read_symbol)
        else:
            input_tape[head] = read_symbol


    history_tape = []

    print("Fita 1:", ''.join(original_input))
    print("Fita 2:", ''.join(history_tape))
    print("Fita 3:", ''.join(output_tape))

if __name__ == "__main__":
    main()