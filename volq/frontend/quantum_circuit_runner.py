import volq.backend as v
from .instructions import Opcode, Instruction

class Runner:
    
    def __init__(self):
        self._program_major_queue = []
        self._program_minor_queue = []
        #self._ins_minor_queue_in_use = 
        self._circuit = None
        self._circuit_init = False
        self._qubits = None
        self._runs = 1
        self._show_style = None

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

    def init_circuit(self):
        self._circuit = v.Circuit(self._qubits)

    def reset_circuit(self):
        self.init_circuit()
        self._program_minor_queue = self._program_major_queue

    def reset_program(self):
        self._program_major_queue = []
        self._program_minor_queue = []

    def load_instruction(self, instruction: Instruction):
        self._instruction_queue.append(instruction)

    def execute_next_instruction(self):
        pass

    def execute_all_instructions(self):
        pass

    def execute_program(self):
        pass
        #return self.get_chart()

    def get_chart(self):
        pass