import enum

class Opcode(enum.Enum):
    QUBITS = "QUBITS"
    RUNS = "RUNS"
    INIT = "INIT"
    APPLY = "APPLY"
    MEASURE = "MEASURE"
    SHOW = "SHOW"


class Instruction():

    def __init__(self, opcode: Opcode, operand: any = None):
        self.opcode = opcode
        self.operand = operand