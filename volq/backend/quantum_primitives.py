import enum
import numpy as np

_SV_TO_MATRIX = {
        "|0⟩": np.array([1,0], dtype = complex),
        "|1⟩": np.array([0,1], dtype = complex),
        "⟨0|": np.array([1,0], dtype = complex).conj(),
        "⟨1|": np.array([0,1], dtype = complex).conj()
    }

_PROJ_TO_MATRIX = {
        "|0⟩⟨0|": np.array([[1,0], [0,0]], dtype = complex),
        "|1⟩⟨1|": np.array([[0,0], [0,1]], dtype = complex)
    }

class StateVector(enum.Enum):
    KET_0 = "|0⟩"
    KET_1 = "|1⟩"
    BRA_0 = "⟨0|"
    BRA_1 = "⟨1|"

    def matrix(self):
        return _SV_TO_MATRIX[self.value]


class Projector(enum.Enum):
    KETBRA_00 = "|0⟩⟨0|"
    KETBRA_11 = "|1⟩⟨1|"

    def matrix(self):
        return _PROJ_TO_MATRIX[self.value]