import re
import numpy as np

class Compiler:

    def __init__(self):
        
        self.np = np

        self.IDENTITY = np.array([[1,0],[0,1]], dtype = complex)
        self.PAULI_X = np.array([[0,1],[1,0]], dtype = complex)
        self.PAULI_Y = np.array([[0,-1j],[1j,0]], dtype = complex)
        self.PAULI_Z = np.array([[1,0],[0,-1]], dtype = complex)
        self.HADAMARD = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]],
                                                    dtype = complex)
        
        self.KET_0 = np.array([1,0], dtype = complex)             # |0⟩
        self.KET_1 = np.array([0,1], dtype = complex)             # |1⟩
        self.KETBRA_00 = np.outer(self.KET_0, self.KET_0.conj())  # |0⟩⟨0|
        self.KETBRA_11 = np.outer(self.KET_1, self.KET_1.conj())  # |1⟩⟨1|

        # Map strings to gates
        self.SINGLE_QUBIT_GATES = {
            "I": self.IDENTITY,
            "X": self.PAULI_X,
            "Y": self.PAULI_Y,
            "Z": self.PAULI_Z,
            "H": self.HADAMARD
        }
    

    def compile_operator(self, operator_key):
        np = self.np
        # If operator U is already cached, skip
        # Parse string to array of operators
        operator_construction = self.parse_key_to_matrices(operator_key)

        # Start with 1x1 dimensional identity vector
        operator_U = np.array([1], dtype = complex)

        # Construct U by tensoring gates together into one matrix
        for gate in operator_construction:
            operator_U = np.kron(operator_U, gate)
        
        return operator_U


    def parse_key_to_matrices(self, operator_key):
        gates = []
        tokenized_key = re.split(" ", operator_key)

        for token in tokenized_key:
            if token[0] == "C":
                gates.append(self.compile_controlled_gate(token))
            else:
                gates.append(self.SINGLE_QUBIT_GATES[token[0]])

        return gates


    def compile_controlled_gate(self, token):
        np = self.np

        # Count number of control wires
        control_wires = 0
        for char in token:
            if char == "C":
                control_wires += 1

        ## Decompose token into array of [letter, index] pairs
        # Side note: Far from the most beautiful solution, but functional
        # for now. To refactor into something better later
        gate_structure = []
        tail_cursor = len(token) - 1
        for i in range(control_wires + 1):
            gate_structure.append([token[i], 0])

            # Compute the index by passing each digit backwards until we
            # reach a comma or a gate
            digit = 0
            while token[tail_cursor] != ",":
                if i == tail_cursor:
                    break
                gate_structure[i][1] += int(token[tail_cursor]) * (10 ** digit)
                digit += 1
                tail_cursor -= 1
            tail_cursor -= 1

        ## Order operations with insertion sort
        for i in range(1, len(gate_structure)):
            key_item = gate_structure[i]
            key_value = key_item[1]
            j = i - 1
            while j >= 0 and gate_structure[j][1] > key_value:
                gate_structure[j + 1] = gate_structure[j]
                j -= 1
            gate_structure[j + 1] = key_item

        # Currently there's assumed to only be one gate in this operator,
        # to add validation later

        ## Find target gate in gate_structure
        i = 0
        while gate_structure[i][0] == "C":
            i += 1
        target_gate_index = i
        U = self.SINGLE_QUBIT_GATES[gate_structure[target_gate_index][0]]

        ## Tensor matrices together to compile an operator
        # Compile control wires on the left side of the target wire
        operation_cursor = target_gate_index
        for i in range(target_gate_index - 1, -1, -1):
            index_difference = gate_structure[operation_cursor][1] - gate_structure[i][1]  # pylint: disable=line-too-long
            U_0 = np.kron(
                np.kron(
                    self.KETBRA_00,
                    np.eye(2 ** (index_difference - 1))),
                np.eye(U.shape[0]))
            U_1 = np.kron(
                np.kron(
                    self.KETBRA_11,
                    np.eye(2 ** (index_difference - 1))),
                U)
            U = U_0 + U_1
            operation_cursor -= 1

        # Compile control wires on the right side of the target wire
        operation_cursor = target_gate_index
        for i in range(target_gate_index + 1, len(gate_structure)):
            index_difference = gate_structure[i][1] - gate_structure[operation_cursor][1]  # pylint: disable=line-too-long
            U_0 = np.kron(
                np.kron(
                    np.eye(U.shape[0]),
                    np.eye(2 ** (index_difference - 1))),
                self.KETBRA_00)
            U_1 = np.kron(
                np.kron(
                    U,
                    np.eye(2 ** (index_difference - 1))),
                self.KETBRA_11)
            U = U_0 + U_1
            operation_cursor += 1

        return U
