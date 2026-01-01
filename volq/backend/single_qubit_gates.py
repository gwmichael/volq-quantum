import enum
import numpy as np

class Gate(enum.Enum):
    I = "I"  # Identity
    H = "H"  # Hadamard
    X = "X"  # Pauli X
    Y = "Y"  # Pauli Y
    Z = "Z"  # Pauli Z

    GATE_TO_MATRIX = {
        "I": np.array([[1,0],[0,1]], dtype = complex),
        "H": (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype = complex),
        "X": np.array([[0,1],[1,0]], dtype = complex),
        "Y": np.array([[0,-1j],[1j,0]], dtype = complex),
        "Z": np.array([[1,0],[0,-1]], dtype = complex)
    }

    def matrix(self):
        return self.GATE_TO_MATRIX[self.value]