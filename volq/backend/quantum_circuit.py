import re
from .parser import Parser
from .compiler import Compiler

class Circuit:

    def __init__(
            self,
            qubits: int,
            operator_cache: bool = False,
            hardware_mode: str = "CPU",
            DEBUG_syntax_validation: bool = True,
            output_rounding_dp = 5
        ):

        if qubits < 1:
            raise ValueError(
                "Qubits parameter must be at least 1, got " + str(qubits))

        # Choose to load cupy (numpy but for GPUs) or numpy
        if hardware_mode == "GPU":
            import cupy as np
        else:
            import numpy as np
        self.np = np
        np.set_printoptions(
            threshold = np.inf,
            linewidth = np.inf,
            precision = 15,
            suppress = True
        )

        # Setup basis vector of qubit states
        self._qubits = qubits
        self._circuit_state = np.zeros(2 ** self._qubits, dtype = complex)
        # Set circuit state to |00...0⟩
        self._circuit_state[0] = 1
        self._operator_cache_state = operator_cache
        self._operator_cache = {}
        self._output_rounding_dp = output_rounding_dp

        # Load parser and compiler
        self._parser = Parser(self._qubits, DEBUG_syntax_validation)
        self._compiler = Compiler(operator_cache)

        # Gates
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

        self.ALIASES = {
            "NOT" : "X",
            "TOFFOLI" : "CCX",
            "TOFF" : "CCX"
        }

        # WARNING: This option is intended for testing new syntax before
        #          validation is implemented.
        #          Disabling this creates a risk of infinite loops or crashes!


    def reset_circuit_state(self):
        np = self.np
        # Soft reset the circuit state to |00...0⟩
        self._circuit_state = np.zeros(2 ** self._qubits, dtype = complex)
        self._circuit_state[0] = 1


    def apply_operator(self, key):
        np = self.np
        normalised_key = self._parser.normalise_key(key)
        if normalised_key in self._operator_cache:
            U = self._operator_cache[normalised_key]
        else:
            U = self._compiler.compile_operator(normalised_key)
            # If operator cache is enabled, then add compiled operator
            if self._operator_cache_state:
                self._operator_cache[normalised_key] = U
        self._circuit_state = np.dot(U, self._circuit_state)


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

        # If cache is enabled, then add it to the cache
        if self._operator_cache_state:
            self._operator_cache[operator_key] = operator_U
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
        # Side note: Far from the most beautiful solution, but functional for a
        # prototype. To refactor into something less cursed later
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


    def measure(self):
        np = self.np
        # Make a copy of self._circuit_state with Born's rule applied
        probabilities = np.abs(self._circuit_state) ** 2
        # Select a random state based on the probability of that outcome
        outcome = np.random.choice(2 ** self._qubits, p = probabilities)
        # Collapse circuit state to the selected state
        collapsed_circuit_state = np.zeros(2 ** self._qubits, dtype = complex)
        collapsed_circuit_state[outcome] = 1 + 0j
        self._circuit_state = collapsed_circuit_state


    def get_state_as_string(self):
        np = self.np

        ## Get list of all states with a non-zero amplitude
        all_circuit_states = []
        for i in range(2 ** self._qubits):
            if (np.real(self._circuit_state[i]) != 0 or
                np.imag(self._circuit_state[i]) != 0):
                all_circuit_states.append(i)

        # Sort states by basis position
        sorted_all_circuit_states = []

        for i in range(2 ** self._qubits):
            target_bitstring = self.generate_bitstring(i)
            for j in all_circuit_states:
                if self.generate_bitstring(j) == target_bitstring:
                    sorted_all_circuit_states.append(j)

        all_circuit_states = sorted_all_circuit_states

        ## Construct string of kets
        output = ""
        for state in all_circuit_states:
            amplitude = self._circuit_state[state]
            # Separate real and imaginary parts
            amp_real = np.round(np.real(amplitude), self._output_rounding_dp)
            amp_imag = np.round(np.imag(amplitude), self._output_rounding_dp)
            state_string = ""
            # Add real part
            # If it is equal to 1, we don't add the real part
            if amp_real != 0 and np.abs(amp_real) != 1:
                state_string += str(np.abs(amp_real))
            # Add imaginary part
            if amp_imag != 0:
                # If there's a real number, add the sign in the complex number
                if amp_real != 0 and amp_imag < 0:
                    state_string += "-"
                elif amp_real != 0 and amp_imag > 0:
                    state_string += "+"

                # Simplify algebraically if amp_imag == 1
                if np.abs(amp_imag) == 1:
                    state_string += "i"
                else:
                    state_string += str(np.abs(amp_imag)) + "i"

            # Add ket of state
            state_string += "|" + self.generate_bitstring(state) + "⟩"

            ## Add state string to output
            # First iteration?
            if output == "":
                # Real part or imag part w/o real part is positive
                if amp_real > 0 or (amp_real == 0 and amp_imag > 0):
                    output += state_string
                # Real part or imag part w/o real part is negative
                elif amp_real < 0 or (amp_real == 0 and amp_imag < 0):
                    output += "-" + state_string

            # Not first iteration, so add operands between kets
            else:
                # Real part or imag part w/o real part is positive
                if amp_real > 0 or (amp_real == 0 and amp_imag > 0):
                    output += " + " + state_string
                # Real part or imag part w/o real part is negative
                elif amp_real < 0 or (amp_real == 0 and amp_imag < 0):
                    output += " - " + state_string

        return output


    def generate_bitstring(self, basis):
        bitstring = ""
        for i in range(self._qubits):
            if basis >= 2 ** (self._qubits - i - 1):
                bitstring += "1"
                basis -= 2 ** (self._qubits - i - 1)
            else:
                bitstring += "0"
        return bitstring


    def DEBUG_get_circuit_state(self):
        return self._circuit_state


    def DEBUG_is_operator_cached(self, operator_key):
        return operator_key in self._operator_cache
