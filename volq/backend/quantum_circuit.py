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
        self._compiler = Compiler()


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
