import volq.backend as v
from .instructions import Opcode, Instruction

class Runner:
    
    def __init__(self):
        self._program_major_queue = []
        self._program_minor_queue = []
        # Live mode: Execute instructions immediately as they're loaded, only use the major queue
        self._live_mode = False
        self._circuit = None
        self._circuit_initialised = False
        self._qubits = None
        self._runs = 1
        self._show_style = None
        # Results will be stored as a hashmap, so that a histogram can be generated using matplotlib
        self._results = []

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
        return self._program_major_queue

    def init_circuit(self):
        self._circuit = v.Circuit(self._qubits)
        self._circuit_initialised = True

    def reset_circuit_state(self):
        self.init_circuit()
        self.reload_program()

    def reload_program(self):
        self._program_minor_queue = self._program_major_queue

    def clear_program(self):
        self._program_major_queue = []
        self._program_minor_queue = []

    def load_instruction(self, instruction: Instruction):
        self._instruction_queue.append(instruction)

    # Execute the single next instruction in the loaded program
    def execute_next_instruction(self):
        # TODO: Add exception when there is no next instruction
        # self.execute_immediate(next instruction)
        pass

    # Execute the whole program once
    def execute_all_instructions(self):
        pass

    # Execute the whole program {self._runs} times
    def execute_all_runs(self):
        pass
        #return self.get_results_histogram()

    # Maybe a function that just directly takes an instruction & executes it (for live mode?)
    def execute_immediate(self, instruction: Instruction):
        match instruction.opcode:
            case Opcode.QUBITS:
                if self._circuit_initialised == True:
                    # TODO Throw exception that circuit is already initialised
                    pass
                self._qubits = instruction.operand
            case Opcode.RUNS:
                self._runs = instruction.operand
            case Opcode.INIT:
                self.init_circuit()
            case Opcode.APPLY:
                self._circuit.apply_operator(instruction.operand)
            case Opcode.MEASURE:
                # TODO Implement partial measure in quantum_circuit, then add more detailed operand logic here
                self._circuit.measure()
            case Opcode.NOP:
                pass
            case Opcode.SHOW:
                # TODO Implement show state, histogram, program, config
                self._show_style = instruction.operand

    def get_results_histogram(self):
        pass

    def get_results(self):
        pass