from quantum_circuit import Circuit
from instructions import Opcode, Instruction
import sys

class Interpreter:

    DIRECT_EXECUTE_ARGUMENT = "-e"

    def __init__(self):
        # Read program in
        direct_execution_mode = False
        file_execution_mode = False
        self.arguments = sys.argv[1:]
        self._execution_stack = []
        self._circuit = None
        self._circuit_init = False
        self._qubits = None
        self._runs = 1
        self._show_style = None
        
        # Start main interpreter loop
        self.main()


    def main(self):
        if (self.arguments[0] == self.DIRECT_EXECUTE_ARGUMENT):
            self.direct_execution_mode = True
            program = self.arguments[1].split("\n")
        else:
            self.file_execution_mode = True
            with open(self.arguments[0], "r") as file:
                contents = file.read()
            program = contents.split("\n")
        
        # Parse the program into a stack
        for line in program:
            instruction = None
            line_tokens = line.split(" ")
            match line_tokens[0]:
                case "\n":
                    continue
                case "":
                    continue
                case "QUBITS":
                    instruction = Instruction(Opcode.QUBITS, int(line_tokens[1]))
                case "RUNS":
                    instruction = Instruction(Opcode.RUNS, int(line_tokens[1]))
                case "INIT":
                    instruction = Instruction(Opcode.INIT)
                case "APPLY":
                    # Backend circuit class handles all the parsing, so just pass the whole string as operand
                    instruction = Instruction(Opcode.APPLY, line_tokens[1])
                case "MEASURE":
                    instruction = Instruction(Opcode.MEASURE, line_tokens[1])
                case "SHOW":
                    instruction = Instruction(Opcode.SHOW, line_tokens[1])
                case _:
                    print(f"Fatal error: {line_tokens[0]} is not a valid opcode")
                    quit()

            self._execution_stack.append(instruction)

        # Execute the program
        execution_substack = []
        for instruction in self._execution_stack:
            match instruction.opcode:
                case Opcode.QUBITS:
                    self._qubits = instruction.operand
                case Opcode.RUNS:
                    self._runs = instruction.operand
                case Opcode.INIT:
                    self._circuit = Circuit(self._qubits)
                case Opcode.APPLY:
                    execution_substack.append(instruction)
                case Opcode.MEASURE:
                    execution_substack.append(instruction)
                case Opcode.SHOW:
                    self._show_style = instruction.operand
        
        results = []

        for i in range(0, self._runs):
            self._circuit.reset_circuit_state()
            for instruction in execution_substack:
                match instruction.opcode:
                    case Opcode.APPLY:
                        self._circuit.apply_operator(instruction.operand)
                    case Opcode.MEASURE:
                        self._circuit.measure()
            
            results.append(self._circuit.DEBUG_get_circuit_state())

        # Show style not yet implemented, just print for now
        print(results)

        

if __name__ == "__main__":
    Interpreter()