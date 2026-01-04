from volq.runtime.instructions import Opcode, Instruction
from volq.runtime.runtime import Runtime
import sys

class Interpreter:

    DIRECT_EXECUTE_ARGUMENT = "-e"

    def __init__(self):
        print(">> Volq-quantum v0.4.0-alpha\n" +
              ">> Author: michaelchips / Michael Goodwin")
        # Read program in
        self.arguments = sys.argv[1:]
        self.runtime = Runtime()

        # Start main interpreter loop
        self.main()


    def main(self):
        if self.arguments[0] == self.DIRECT_EXECUTE_ARGUMENT:
            program = self.arguments[1].split("\n")
        else:
            with open(
                file = self.arguments[0],
                mode = "r",
                encoding = "UTF-8"
            ) as file:
                contents = file.read()
            program = contents.split("\n")

        # Parse the program into a stack
        for line in program:
            instruction = None
            line_tokens = line.split(" ", 1)
            match line_tokens[0]:
                case "\n":
                    continue
                case "":
                    continue
                case "NOP":
                    instruction = Instruction(
                        Opcode.NOP
                        )
                case "QUBITS":
                    instruction = Instruction(
                        Opcode.QUBITS,
                        int(line_tokens[1])
                        )
                case "RUNS":
                    instruction = Instruction(
                        Opcode.RUNS,
                        int(line_tokens[1])
                        )
                case "INIT":
                    instruction = Instruction(
                        Opcode.INIT
                        )
                case "APPLY":
                    # Backend circuit class handles all the parsing
                    # so just pass the whole string as operand
                    instruction = Instruction(
                        Opcode.APPLY,
                        line_tokens[1]
                        )
                case "MEASURE":
                    instruction = Instruction(
                        Opcode.MEASURE,
                        line_tokens[1]
                        )
                case "SHOW":
                    instruction = Instruction(
                        Opcode.SHOW,
                        line_tokens[1]
                        )
                case _:
                    print(f"Syntax error: {line_tokens[0]} is not a valid " +
                          "opcode, exiting")
                    quit()

            self.runtime.load_instruction(instruction)

        # Execute the program
        self.runtime.execute_all_runs()

        print(self.runtime.get_results())

if __name__ == "__main__":
    Interpreter()
