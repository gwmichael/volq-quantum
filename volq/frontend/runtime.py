import volq.backend as v
from .instructions import Opcode, Instruction

class Runtime:
    
    def __init__(self):
        self._program = []
        self._instruction_pointer = 0
        self._marked_instruction_pointer = None
        # Live mode: Execute instructions immediately as they're loaded, only use the major queue
        self._live_mode = False
        self._circuit = None
        self._circuit_initialised = False
        self._qubits = None
        self._runs = 1
        self._iteration = 1
        self._show_style = None # TODO Implement showing multiple string styles
        # Results will be stored as a hashmap, so that a histogram can be generated using matplotlib
        self._results = {}

    def set_qubits(self, qubits):
        if (self._circuit == None):
            self._qubits = qubits
        else:
            # TODO: Throw exception that circuit is already initialised, 
            # therefore qubits can't be changed
            pass
    
    def get_qubits(self):
        return self._qubits
    
    def set_runs(self, runs):
        self._runs = runs

    def get_runs(self):
        return self._runs
    
    def get_program(self):
        return self._program

    def init_circuit(self):
        self._circuit = v.Circuit(self._qubits)
        self._circuit_initialised = True

    def reset_circuit_state(self):
        self.init_circuit()
        self.reload_program()

    def reload_program(self):
        self._instruction_pointer = self._marked_instruction_pointer

    def clear_program(self):
        self._program = []

    def load_instruction(self, instruction: Instruction):
        self._program.append(instruction)

    # Execute the single next instruction in the loaded program
    def execute_next_instruction(self):
        # TODO: Add exception when there is no next instruction
        # self.execute_immediate(next instruction)
        self.execute_immediate(self._program[self._instruction_pointer])
        self._instruction_pointer += 1

    # Execute the whole program once
    def execute_until_last_instruction(self):
        for i in range(self._instruction_pointer, len(self._program)):
            self.execute_next_instruction()

    # Execute the whole program {self._runs} times
    def execute_all_runs(self):
        while True:
            self.execute_until_last_instruction()
            self.save_state_to_results()
            self.reset_circuit_state()
            if self._iteration < self._runs:
                self._iteration += 1
                continue
            else:
                break
        #return self.get_results_histogram()

    def execute_immediate(self, instruction: Instruction):
        match instruction.opcode:
            case Opcode.QUBITS:
                if self._circuit_initialised == True:
                    # TODO Throw exception that circuit is already initialised
                    pass
                self._qubits = int(instruction.operand)
            case Opcode.RUNS:
                if self._circuit_initialised == True:
                    # TODO Throw exception that circuit is already initialised
                    pass
                self._runs = int(instruction.operand)
            case Opcode.INIT:
                self.init_circuit()
                self._marked_instruction_pointer = self._instruction_pointer + 1
            case Opcode.APPLY:
                self._circuit.apply_operator(instruction.operand)
            case Opcode.MEASURE:
                # TODO Implement partial measure in quantum_circuit, then add more detailed operand logic here
                self._circuit.measure()
            case Opcode.NOP:
                pass
            case Opcode.SHOW:
                # TODO Implement show state, histogram, program, config
                pass

    def save_state_to_results(self):
        state = self._circuit.get_state_as_string()
        # Is state already recorded in results?
        if state in self._results:
            # Increment by 1
            self._results[state] += 1
        else:
            # It's showing up for the first time, so set to 1
            self._results[state] = 1

    def get_results_histogram(self):
        pass

    def get_results(self):
        return self._results