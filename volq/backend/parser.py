import re
import numpy as np  # Note to self for later: May conflict with cupy, implement class-level np passthrough?
from .single_qubit_gates import Gate as single_qubit_gates

class Parser:
    
    def __init__(
            self,
            qubits: int,
            DEBUG_syntax_validation = True
        ):

        self._qubits = qubits

        # WARNING: This option is intended for testing new syntax before
        #          validation is implemented.
        #          Disabling this creates a risk of infinite loops or crashes!
        self.DEBUG_syntax_validation = DEBUG_syntax_validation

        self.ALIASES = {
            "NOT" : "X",
            "TOFFOLI" : "CCX",
            "TOFF" : "CCX"
        }
    
    
    def normalise_key(self, operator_key):

        operator_key = self.translate_aliases(operator_key)

        if self.DEBUG_syntax_validation:
            self.check_legal_syntax(operator_key)

        ## Tokenization
        # Remove spaces at start and end
        stripped_key = operator_key.strip(" ")
        # Split operator into tokens
        tokenized_key = re.split(" ", stripped_key)

        ## Ordering
        # Tokenize into tuples
        aux_gates = []
        for token in tokenized_key:
            # Check how many letters there are
            token_cursor = 0
            while token[token_cursor].isalpha():
                token_cursor += 1
            local_gate = token[:token_cursor]
            # Get the wire(s)
            wires = list(map(int, token[token_cursor:].split(",")))
            aux_gates.append((local_gate, wires))
        aux_gates.sort(key=lambda gw: gw[1][0])

        ## Padding
        # Pad empty space with I gates
        gate_cursor = 0
        gates = []
        for gate in aux_gates:
            while gate_cursor < min(gate[1]):
                gates.append(("I", [gate_cursor]))
                gate_cursor += 1

            # Add gate to list
            gates.append((gate[0], gate[1]))
            gate_cursor += 1 + max(gate[1]) - min(gate[1])

        # gate_cursor should not be larger than the number of qubits. If so,
        # this means more gates have been added than there are qubits in the
        # circuit
        if gate_cursor > self._qubits:
            raise ValueError("Operator has more gates than there are " +
            "qubits in the circuit, invalid shape. Qubits in circuit is " + 
            str(self._qubits))

        # Pad with identity gates after all gates have been added
        while gate_cursor < self._qubits:
            gates.append(("I", [gate_cursor]))
            gate_cursor += 1

        # To add a check that the shape of the final matrix will match

        ## Parse tuples back into a string
        output_key = ""

        for gate in gates:
            # Build a string that supports multiple wires
            wire_string = ""
            for i in range(len(gate[1])):
                if i > 0:
                    wire_string += ","
                wire_string += str(gate[1][i])

            # First gate?
            if output_key != "":
                output_key += " "

            output_key += gate[0] + wire_string

        return output_key


    def translate_aliases(self, operator_key):

        new_ok = operator_key
        for alias, resolution in self.ALIASES.items():
            new_ok = new_ok.replace(alias, resolution)

        return new_ok
    
    
    def check_legal_syntax(self, operator_key):
        # This is quite a rudimentary way of checking the syntax
        #
        # Someday this entire process will be refactored to a cleaner parser
        # and I will write a EBNF grammar for the DSL, but there are other
        # priorities first.

        stripped_key = operator_key.strip(" ")
        tokenized_key = re.split(" ", stripped_key)

        for token in tokenized_key:
            ## Length check
            if len(token) < 2:
                raise ValueError(f"Invalid gate provided: Received {token}, " +
                    "expected a gate of length at least 2")

            ## Gate validity check
            # Advance past any set control wires
            operator_cursor = 0
            while token[operator_cursor] == "C":
                operator_cursor += 1
            # Then check gate
            gate = token[operator_cursor]
            if gate not in single_qubit_gates:
                raise ValueError(f"Invalid gate provided: Received {token}, " +
                    "{gate} cannot be resolved to a valid gate")

            ## Index check
            # Indices should start at the index after the operator
            gate_indices = token[operator_cursor + 1:]
            split_gate_indices = gate_indices.split(",")
            for gate_index in split_gate_indices:
                if int(gate_index) > self._qubits:
                    raise ValueError("Invalid gate provided: Received " +
                        f"{token}, applies to wire {gate_index} but there " +
                        f"are only {str(self._qubits)} qubits")