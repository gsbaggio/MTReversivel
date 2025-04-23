import sys
import os

class ReversibleTuringMachine:
    def __init__(self):
        self.num_states = 0
        self.num_input_symbols = 0
        self.num_tape_symbols = 0
        self.num_transitions = 0
        
        self.states = []
        self.input_alphabet = []
        self.tape_alphabet = []
        self.transitions_quintuple = {}  # Dictionary for quintuples
        self.transitions_quadruple = {}  # Dictionary for quadruples
        
        self.input_string = ""
        
        # 3 tapes: main, history and output
        self.tapes = [[], [], []]
        self.heads = [0, 0, 0]
        self.current_state = "1"  # Start with state 1
    
    def read_input_file(self, filename):
        """Read a TM definition in quintuple format from file"""
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
                
                # Parse the first line (machine parameters)
                params = lines[0].strip().split()
                self.num_states = int(params[0])
                self.num_input_symbols = int(params[1])
                self.num_tape_symbols = int(params[2])
                self.num_transitions = int(params[3])
                
                # Parse states
                self.states = lines[1].strip().split()
                
                # Parse input alphabet
                self.input_alphabet = lines[2].strip().split()
                
                # Parse tape alphabet
                self.tape_alphabet = lines[3].strip().split()
                
                # Parse transitions
                for i in range(4, 4 + self.num_transitions):
                    transition = lines[i].strip()
                    state, symbol, next_state, write, move = self.parse_quintuple(transition)
                    self.transitions_quintuple[(state, symbol)] = (next_state, write, move)
                
                # Parse input string
                self.input_string = lines[4 + self.num_transitions].strip()
                
                return True
        except Exception as e:
            print(f"Error reading input file: {e}")
            return False
    
    def parse_quintuple(self, transition):
        """Parse a transition like "(1,0)=(2,$,R)" into components"""
        left_side = transition.split('=')[0].strip('()')
        right_side = transition.split('=')[1].strip('()')
        
        current_state, read_symbol = left_side.split(',')
        next_state_data = right_side.split(',')
        next_state = next_state_data[0]
        write_symbol = next_state_data[1]
        direction = next_state_data[2]
        
        return (current_state, read_symbol, next_state, write_symbol, direction)
    
    def convert_to_quadruples(self):
        """Convert quintuple transitions to quadruple transitions"""
        for (state, symbol), (next_state, write, move) in self.transitions_quintuple.items():
            # Create simpler intermediate state using just state and read symbol
            intermediate_state = f"{state}'{symbol}"
            
            # First quadruple: (state, read) = (intermediate_state, write)
            self.transitions_quadruple[(state, symbol)] = (intermediate_state, write)
            
            # Second quadruple: (intermediate_state, /) = (next_state, move)
            # The '/' symbol is used as a placeholder for intermediate states
            self.transitions_quadruple[(intermediate_state, "/")] = (next_state, move)
    
    def write_quadruples_to_file(self, filename):
        """Write quadruple transitions to file"""
        try:
            with open(filename, 'w') as file:
                # Count unique states including intermediate states
                all_states = set(self.states)
                for state, _ in self.transitions_quadruple.keys():
                    if "'" in state:  # If this is an intermediate state
                        all_states.add(state)
                
                # Write machine parameters
                file.write(f"{len(all_states)} {self.num_input_symbols} {self.num_tape_symbols+1} {len(self.transitions_quadruple)}\n")
                
                # Write states
                file.write(" ".join(sorted(all_states)) + "\n")
                
                # Write input alphabet
                file.write(" ".join(self.input_alphabet) + "\n")
                
                # Write tape alphabet with the '/' symbol added
                file.write(" ".join(self.tape_alphabet) + " /\n")
                
                # Write transitions
                for (state, symbol), (next_state, action) in sorted(self.transitions_quadruple.items()):
                    file.write(f"({state},{symbol})=({next_state},{action})\n")
                
                # Write input string
                file.write(self.input_string + "\n")
                
                return True
        except Exception as e:
            print(f"Error writing quadruples file: {e}")
            return False
    
    def initialize_tapes(self):
        """Initialize the three tapes for the RTM"""
        # Initialize tape 1 with input string and blanks
        self.tapes[0] = list(self.input_string) + ["B"] * 100
        
        # Initialize tape 2 (history) and tape 3 (output) with blanks
        self.tapes[1] = ["B"] * 100
        self.tapes[2] = ["B"] * 100
        
        # Initialize head positions
        self.heads = [0, 0, 0]
        
        # Initialize current state
        self.current_state = "1"
    
    def simulate_forward(self):
        """Run the forward phase until reaching a final state"""
        print("Starting Forward Phase")
        print("-" * 60)
        
        final_state = self.states[-1]  # The accepting state is the last one
        steps = 0
        
        # Print initial configuration
        self.print_configuration()
        
        while self.current_state != final_state and steps < 1000:  # Limit steps to avoid infinite loops
            # Check if we're in an intermediate state (with apostrophe)
            if "'" in self.current_state:
                # For intermediate states, always use "/" and just move the head
                if (self.current_state, "/") in self.transitions_quadruple:
                    next_state, action = self.transitions_quadruple[(self.current_state, "/")]
                    
                    # Store the intermediate state in history tape
                    # This captures both the original state and symbol read
                    self.tapes[1][self.heads[1]] = self.current_state
                    self.heads[1] += 1  # Move history head after writing
                    
                    # Update state
                    self.current_state = next_state
                    
                    # Move head on tape 1
                    if action == "R":
                        self.heads[0] += 1
                    elif action == "L":
                        self.heads[0] = max(0, self.heads[0] - 1)
                else:
                    print(f"No transition found for intermediate state {self.current_state}")
                    return False
            else:
                # Regular state - read symbol from tape
                current_symbol = self.tapes[0][self.heads[0]]
                
                # Find transition
                if (self.current_state, current_symbol) in self.transitions_quadruple:
                    next_state, action = self.transitions_quadruple[(self.current_state, current_symbol)]
                    
                    # Write new symbol on tape 1
                    self.tapes[0][self.heads[0]] = action
                    
                    # Update state
                    self.current_state = next_state
                    
                    # We don't store anything in history tape at this step
                    # It will be stored after the movement operation
                else:
                    print(f"No transition found for state {self.current_state} and symbol {current_symbol}")
                    return False
            
            steps += 1
            # Print configuration after every step
            self.print_configuration()
        
        print(f"Forward phase completed in {steps} steps")
        return True
    
    def simulate_copy(self):
        """Copy the output from tape 1 to tape 3"""
        print("\nStarting Copy Phase")
        print("-" * 60)
        
        # Reset head positions for tape 1 and 3
        self.heads[0] = 0
        self.heads[2] = 0
        
        # Note: The history tape head position remains where it was
        # (pointing to the rightmost non-blank cell, containing the state N)
        
        # Print initial configuration for copy phase
        self.print_configuration()
        
        # Copy symbols from tape 1 to tape 3 until reaching blank
        # No writing to history tape during this phase
        while self.tapes[0][self.heads[0]] != "B":
            self.tapes[2][self.heads[2]] = self.tapes[0][self.heads[0]]
            self.heads[0] += 1
            self.heads[2] += 1
            
            # Print configuration after every copy operation
            self.print_configuration()
        
        print("Copy phase completed")
        return True
    
    def simulate_retrace(self):
        """Execute the retrace phase (reverse execution)"""
        print("\nStarting Retrace Phase")
        print("-" * 60)
        
        # Move to the last written history position
        self.heads[1] = 0
        while self.heads[1] < len(self.tapes[1]) and self.tapes[1][self.heads[1]] != "B":
            self.heads[1] += 1
        self.heads[1] = max(0, self.heads[1] - 1)  # Step back to the last written entry
        
        # Print initial configuration for retrace phase
        self.print_configuration()
        
        steps = 0
        
        # Continue until we reach the initial state or run out of history
        while self.current_state != "1" and self.heads[1] >= 0 and steps < 1000:
            # Get intermediate state from history
            if self.heads[1] >= 0 and self.tapes[1][self.heads[1]] != "B":
                intermediate_state = self.tapes[1][self.heads[1]]
                
                # Parse the intermediate state to get original state and symbol
                # Format is "state'symbol"
                if "'" in intermediate_state:
                    parts = intermediate_state.split("'")
                    original_state = parts[0]
                    original_symbol = parts[1]
                    
                    # Determine the direction from the quadruple
                    if (intermediate_state, "/") in self.transitions_quadruple:
                        _, direction = self.transitions_quadruple[(intermediate_state, "/")]
                        
                        # Move in the opposite direction
                        if direction == "R":
                            # First move left
                            if self.heads[0] > 0:
                                self.heads[0] -= 1
                        elif direction == "L":
                            # First move right
                            self.heads[0] += 1
                        
                        # Write the original symbol back to tape 1
                        self.tapes[0][self.heads[0]] = original_symbol
                        
                        # Set the state to the original state
                        self.current_state = original_state
                    else:
                        print(f"Error: No transition found for intermediate state {intermediate_state}")
                        return False
                else:
                    print(f"Error: Invalid intermediate state format: {intermediate_state}")
                    return False
                
                # Clear this history entry
                self.tapes[1][self.heads[1]] = "B"
                
                # Move to previous history entry
                self.heads[1] -= 1
                
                steps += 1
                # Print configuration after every retrace step
                self.print_configuration()
            else:
                # No more valid history entries
                break
        
        print(f"Retrace phase completed in {steps} steps")
        return True
    
    def print_configuration(self):
        """Print the current configuration of the machine"""
        def format_tape(tape, head_pos):
            visible_range = range(max(0, head_pos - 10), min(len(tape), head_pos + 11))
            result = "... " if head_pos > 10 else ""
            
            for i in visible_range:
                if i == head_pos:
                    result += f"[{tape[i]}] "  # Add space after the head position
                else:
                    result += f"{tape[i]} "  # Add space after each symbol
            
            result = result.rstrip()  # Remove trailing space
            result += " ..." if head_pos + 10 < len(tape) and tape[head_pos + 10] != "B" else ""
            return result
        
        print(f"State: {self.current_state}")
        print(f"Tape 1 (Main):    {format_tape(self.tapes[0], self.heads[0])}")
        print(f"Tape 2 (History): {format_tape(self.tapes[1], self.heads[1])}")
        print(f"Tape 3 (Output):  {format_tape(self.tapes[2], self.heads[2])}")
        print("-" * 60)
    
    def simulate(self):
        """Run the complete simulation of the Reversible Turing Machine"""
        # Initialize tapes
        self.initialize_tapes()
        
        # Run the three phases
        forward_success = self.simulate_forward()
        if not forward_success:
            return False
        
        copy_success = self.simulate_copy()
        if not copy_success:
            return False
        
        retrace_success = self.simulate_retrace()
        if not retrace_success:
            return False
        
        print("\nSimulation completed successfully")
        print(f"Final output on tape 3: {''.join(symbol for symbol in self.tapes[2] if symbol != 'B')}")
        return True

def main():
    # Check for input file path
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "entrada-quintupla.txt"
    
    # Process and simulate
    rtm = ReversibleTuringMachine()
    
    # Read input file
    print(f"Reading quintuple transition file: {input_file}")
    if not rtm.read_input_file(input_file):
        print(f"Failed to read input file: {input_file}")
        return
    
    # Convert to quadruple transitions
    rtm.convert_to_quadruples()
    
    # Write the quadruple transitions to a file
    output_file = "entrada-quadrupla.txt"
    if rtm.write_quadruples_to_file(output_file):
        print(f"Wrote quadruple transitions to: {output_file}")
    
    # Simulate the reversible Turing machine
    print("\nStarting simulation of Reversible Turing Machine...")
    rtm.simulate()

if __name__ == "__main__":
    main()
