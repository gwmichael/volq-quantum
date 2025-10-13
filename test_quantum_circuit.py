import unittest
import numpy as np
from quantum_circuit import Circuit

# For repeating tests, set the max qubits that the tests will repeat up until
# A higher MAX_QUBITS value means more rigorous testing,
# but an increase in 1 results in double the memory usage and 8x testing time
MAX_QUBITS = 12

IDENTITY = np.array([[1,0],[0,1]], dtype = complex)
PAULI_X = np.array([[0,1],[1,0]], dtype = complex)
PAULI_Y = np.array([[0,-1j],[1j,0]], dtype = complex)
PAULI_Z = np.array([[1,0],[0,-1]], dtype = complex)
HADAMARD = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype = complex)

SINGLE_QUBIT_GATES = {
    "I": IDENTITY,
    "X": PAULI_X,
    "Y": PAULI_Y,
    "Z": PAULI_Z,
    "H": HADAMARD
}

def generate_ket_0_state(qubits):
    state = np.zeros(2 ** qubits, dtype = complex)
    state[0] = 1 + 0j
    return state

def generate_ket_1_state(qubits):
    state = np.zeros(2 ** qubits, dtype = complex)
    state[(2 ** qubits) - 1] = 1 + 0j
    return state

def generate_uniform_single_gate_circuit_DSL(gate: str, qubits: int):
    dsl = gate + "0"
    for i in range(1, qubits):
        dsl += " " + gate + str(i)
    return dsl

def convert_bitstring_to_decimal(bitstring):
    decimal_value = 0
    for i in range(len(bitstring)):
        # If i'th wire in bitstring == "1" starting from the right side,
        # then add 2^i to decimal_value.
        if bitstring[len(bitstring) - i - 1] == "1":
            decimal_value += 2 ** i
    return decimal_value

class TestQuantumCircuit(unittest.TestCase):

    def test_initialise_circuit(self):
        for i in range(1, MAX_QUBITS + 1):
            qubits = i
            testCircuit = Circuit(qubits)
            expectedState = generate_ket_0_state(qubits)
            self.assertTrue(np.array_equal(
                testCircuit.DEBUG_get_circuit_state(), expectedState),
                msg = f"test_initialise_circuit: Test failed with {i} qubits;" +
                      f"\nExpected: {expectedState}" +
                      f"\nActual: {testCircuit.DEBUG_get_circuit_state()}")
            print(f"test_initialise_circuit: Test passed with {i} qubits")

    def test_invalid_qubits(self):
        # Test zero
        self.assertRaises(ValueError, Circuit, 0)
        # Test negative
        self.assertRaises(ValueError, Circuit, -1)
        print("test_invalid_qubits: Test passed")

    def test_invalid_gates(self):
        testCircuit = Circuit(2)
        ## Syntactically incorrect operator testing
        # Empty/no gates
        self.assertRaises(ValueError, testCircuit.apply_operator, "")
        # Gate only
        self.assertRaises(ValueError, testCircuit.apply_operator, "H")
        # Index only
        self.assertRaises(ValueError, testCircuit.apply_operator, "00")
        # Whitespace
        self.assertRaises(ValueError, testCircuit.apply_operator, "  ")
        # Symbols that are not valid syntax
        self.assertRaises(ValueError, testCircuit.apply_operator, "!!")

        # Test too many gates
        self.assertRaises(ValueError, testCircuit.apply_operator, "H0 H1 H2")

        # Test gate outside index
        self.assertRaises(ValueError, testCircuit.apply_operator, "H99999")
        self.assertRaises(ValueError, testCircuit.apply_operator, "CNOT0,99999")
        self.assertRaises(ValueError, testCircuit.apply_operator, "CNOT99999,0")

        # Test invalid syntax splitting indices in a controlled gate
        self.assertRaises(ValueError, testCircuit.apply_operator, "CNOT0;1")
        self.assertRaises(ValueError, testCircuit.apply_operator, "CNOT0#1")
        self.assertRaises(ValueError, testCircuit.apply_operator, "CNOT0.1")

        print("test_invalid_gates: Test passed")

    def test_equivalent_cached_operators(self):
        testCircuit = Circuit(4, operator_cache = True)
        # Test ordering
        self.assertFalse(testCircuit.DEBUG_is_operator_cached("H0 H1 H2 H3"),
            msg = "test_equivalent_cached_operators: Test failed at the " +
                  "ordering subtest, assertFalse received True")
        testCircuit.apply_operator("H3 H1 H2 H0")
        self.assertTrue(testCircuit.DEBUG_is_operator_cached("H0 H1 H2 H3"),
            msg = "test_equivalent_cached_operators: Test failed at the " +
                  "ordering subtest, assertTrue received False")

        # Test front padding
        self.assertFalse(testCircuit.DEBUG_is_operator_cached("I0 H1 H2 H3"),
            msg = "test_equivalent_cached_operators: Test failed at the " +
                  "front padding subtest, assertFalse received True")
        testCircuit.apply_operator("H1 H2 H3")
        self.assertTrue(testCircuit.DEBUG_is_operator_cached("I0 H1 H2 H3"),
            msg = "test_equivalent_cached_operators: Test failed at the " +
                  "front padding subtest, assertTrue received False")

        # Test end padding
        self.assertFalse(testCircuit.DEBUG_is_operator_cached("H0 I1 I2 I3"),
            msg = "test_equivalent_cached_operators: Test failed at the "
                  "end padding subtest, assertFalse received True")
        testCircuit.apply_operator("H0")
        self.assertTrue(testCircuit.DEBUG_is_operator_cached("H0 I1 I2 I3"),
            msg = "test_equivalent_cached_operators: Test failed at the " +
                  "end padding subtest, assertTrue received False")

        # Test front padding and end padding
        self.assertFalse(testCircuit.DEBUG_is_operator_cached("I0 H1 I2 I3"),
            msg = "test_equivalent_cached_operators: Test failed at the " +
                  "front padding and end padding subtest, assertFalse " +
                  "received True")
        testCircuit.apply_operator("H1")
        self.assertTrue(testCircuit.DEBUG_is_operator_cached("I0 H1 I2 I3"),
            msg = "test_equivalent_cached_operators: Test failed at the " +
                  "front padding and end padding subtest, assertTrue " +
                  "received False")

        # Test front padding, end padding, and ordering
        self.assertFalse(testCircuit.DEBUG_is_operator_cached("I0 H1 H2 I3"),
            msg = "test_equivalent_cached_operators: " +
                  "Test failed at the ordering, front padding and end " +
                  "padding subtest, assertFalse received True")
        testCircuit.apply_operator("H2 H1")
        self.assertTrue(testCircuit.DEBUG_is_operator_cached("I0 H1 H2 I3"),
            msg = "test_equivalent_cached_operators: Test failed at the " +
                  "ordering, front padding and end padding subtest, " +
                  "assertTrue received False")

        # Alias translation testing is separate,
        # in order to test all possible aliases

        print("test_equivalent_cached_operators: Test passed")

    def test_single_qubit_gate_start(self):
        for gate in SINGLE_QUBIT_GATES:
            for i in range(1, MAX_QUBITS + 1):
                qubits = i
                testCircuit = Circuit(qubits)
                zero_state = generate_ket_0_state(qubits)
                expectedState = zero_state
                U = SINGLE_QUBIT_GATES[gate]
                for j in range(1, i):
                    U = np.kron(U, IDENTITY)
                expectedState = np.dot(U, expectedState)
                testCircuit.apply_operator(gate + "0")
                self.assertTrue(
                    np.array_equal(testCircuit.DEBUG_get_circuit_state(),
                                   expectedState),
                    msg = "test_single_qubit_gate_start: Test failed with " +
                         f"{gate} gate and {i} qubits;" +
                         f"\nExpected: {expectedState}" +
                         f"\nActual: {testCircuit.DEBUG_get_circuit_state()}")
                print("test_single_qubit_gate_start: Test passed with " +
                     f"{gate} gate and {i} qubits")

    def test_single_qubit_gate_end(self):
        for gate in SINGLE_QUBIT_GATES:
            for i in range(1, MAX_QUBITS + 1):
                qubits = i
                testCircuit = Circuit(qubits)
                expectedState = generate_ket_0_state(qubits)
                U = np.array([1], dtype = complex)
                for j in range(0, i - 1):
                    U = np.kron(U, IDENTITY)
                U = np.kron(U, SINGLE_QUBIT_GATES[gate])
                expectedState = np.dot(U, expectedState)
                testCircuit.apply_operator(gate + str(i - 1))
                self.assertTrue(
                    np.array_equal(testCircuit.DEBUG_get_circuit_state(),
                                   expectedState),
                    msg = "test_single_qubit_gate_end: Test failed with " +
                         f"{gate} gate and {i} qubits;" +
                         f"\nExpected: {expectedState}" +
                         f"\nActual: {testCircuit.DEBUG_get_circuit_state()}")
                print("test_single_qubit_gate_end: Test passed with " +
                     f"{gate} gate and {i} qubits")

    def test_uniform_single_qubit_gate(self):
        for gate in SINGLE_QUBIT_GATES:
            for i in range(1, MAX_QUBITS + 1):
                qubits = i
                testCircuit = Circuit(qubits)
                expectedState = generate_ket_0_state(qubits)
                U = np.array([1], dtype = complex)
                for j in range(0, i):
                    U = np.kron(SINGLE_QUBIT_GATES[gate], U)
                expectedState = np.dot(U, expectedState)
                U_key = generate_uniform_single_gate_circuit_DSL(gate, qubits)
                testCircuit.apply_operator(U_key)
                self.assertTrue(
                    np.array_equal(
                        testCircuit.DEBUG_get_circuit_state(),
                        expectedState),
                    msg = "test_uniform_single_qubit_gate: Test failed with " +
                         f"{gate} gate and {i} qubits;" +
                         f"\nExpected: {expectedState}" +
                         f"\nActual: {testCircuit.DEBUG_get_circuit_state()}")
                print("test_uniform_single_qubit_gate: Test passed with " +
                     f"{gate} gate and {i} qubits")

    def test_measurement(self):
        for i in range(1, MAX_QUBITS + 1):
            qubits = i
            testCircuit = Circuit(qubits)
            # testCircuit is initialised as |0..0>, check that we measure zero
            expectedState = generate_ket_0_state(qubits)
            testCircuit.measure()
            self.assertTrue(
                np.array_equal(
                    testCircuit.DEBUG_get_circuit_state(),
                    expectedState))
            print("test_measurement: Test measurement of " +
                 f"|{"0" * qubits}> state passed")

            # Apply X⊗n to testCircuit to get the state |1..1>
            # Then apply measurement and check
            expectedState = generate_ket_1_state(qubits)
            testCircuit.apply_operator(
                generate_uniform_single_gate_circuit_DSL("X", qubits))
            testCircuit.measure()
            self.assertTrue(
                np.array_equal(
                    testCircuit.DEBUG_get_circuit_state(),
                    expectedState))
            print("test_measurement: Test measurement of " +
                 f"|{"1" * qubits}> state passed")

            # Revert circuit to |0..0> and apply Y⊗n to get |i..i>,
            # Then check that it collapses to |1..1>
            expectedState = generate_ket_1_state(qubits)
            testCircuit.apply_operator(
                generate_uniform_single_gate_circuit_DSL("X", qubits))
            testCircuit.apply_operator(
                generate_uniform_single_gate_circuit_DSL("Y", qubits))
            testCircuit.measure()
            self.assertTrue(
                np.array_equal(
                    testCircuit.DEBUG_get_circuit_state(),
                    expectedState))
            print("test_measurement: Test measurement of " +
                 f"|{"1" * qubits}> state collapsed from complex plane passed")

    def test_random_measurement_sampling(self):
        for i in range(1, MAX_QUBITS + 1):
            qubits = i
            samples = (2 ** qubits) / 2
            coverage_threshold = 0.375
            test_passed = False
            reruns = 5
            while reruns != 0:
                testCircuit = Circuit(qubits, operator_cache = True)
                seen_states = set()
                for j in range(0, int(samples)):
                    testCircuit.reset_circuit_state()
                    testCircuit.apply_operator(
                        generate_uniform_single_gate_circuit_DSL("H", qubits))
                    testCircuit.measure()
                    collapsed_state = testCircuit.DEBUG_get_circuit_state()
                    for k in range(0, 2 ** qubits):
                        if collapsed_state[k] == 1:
                            seen_states.add(k)
                            break
                coverage = len(seen_states) / len(collapsed_state)
                if coverage >= coverage_threshold:
                    reruns = 0
                    test_passed = True
                else:
                    reruns -= 1
                    print("test_random_measurement_sampling: Repeating test " +
                         f"for {i} qubits")
            self.assertTrue(
                test_passed,
                "test_random_measurement_sampling: Test failed, coverage " +
                f"threshold of {coverage_threshold} has been passed too " +
                 "many times")
            print(f"test_random_measurement_sampling: Test passed with {i} " +
                  f"qubits and {coverage}% coverage")

    def test_partial_superposition_measurement(self):
        for i in range(2, MAX_QUBITS + 1):
            qubits = i
            testCircuit = Circuit(qubits, operator_cache = True)
            repeats = 10
            accepted_0_state = np.zeros(2 ** qubits, dtype = complex)
            accepted_0_state[0] = 1 + 0j
            accepted_1_state = np.zeros(2 ** qubits, dtype = complex)
            accepted_1_state[2 ** (qubits - 1)] = 1 + 0j
            for j in range(0, repeats):
                testCircuit.reset_circuit_state()
                testCircuit.apply_operator("H0")
                testCircuit.measure()
                measuredState = testCircuit.DEBUG_get_circuit_state()
                self.assertTrue(
                    np.array_equal(accepted_0_state, measuredState) or
                    np.array_equal(accepted_1_state, measuredState))
            print("test_partial_superposition_measurement: Test passed with " +
                  f"{i} qubits")

    def test_alias_translation(self):
        testCircuit = Circuit(4, operator_cache = True)

        # CNOT -> CX
        self.assertFalse(testCircuit.DEBUG_is_operator_cached("CX0,1 I2 I3"),
            msg = "test_alias_translation: Test failed when translating CNOT " +
                  "to CX, assertFalse received True")
        testCircuit.apply_operator("CNOT0,1")
        self.assertTrue(testCircuit.DEBUG_is_operator_cached("CX0,1 I2 I3"),
            msg = "test_alias_translation: Test failed when translating CNOT " +
                  "to CX, assertTrue received False")

        # TOFFOLI -> CCX
        self.assertFalse(testCircuit.DEBUG_is_operator_cached("CCX0,1,2 I3"),
            msg = "test_alias_translation: Test failed when translating " +
                  "TOFFOLI to CCX, assertFalse received True")
        testCircuit.apply_operator("TOFFOLI0,1,2")
        self.assertTrue(testCircuit.DEBUG_is_operator_cached("CCX0,1,2 I3"),
            msg = "test_alias_translation: Test failed when translating " +
                  "TOFFOLI to CCX, assertTrue received False")

        # TOFF -> CCX
        self.assertFalse(testCircuit.DEBUG_is_operator_cached("I0 CCX1,2,3"),
            msg = "test_alias_translation: Test failed when translating TOFF " +
                  "to CCX, assertFalse received True")
        testCircuit.apply_operator("TOFF1,2,3")
        self.assertTrue(testCircuit.DEBUG_is_operator_cached("I0 CCX1,2,3"),
            msg = "test_alias_translation: Test failed when translating TOFF " +
                  "to CCX, assertTrue received False")

        print("test_alias_translation: Test passed")

    def test_cnot_compilation(self):
        testCircuit = Circuit(2, operator_cache = True)
        testCircuit.apply_operator("CNOT1,0")
        testCircuit.apply_operator("CNOT0,1")
        # Check correctness against known correct CNOT matrix
        cnot = np.array(
            [[1,0,0,0],
             [0,1,0,0],
             [0,0,0,1],
             [0,0,1,0]],
            dtype = complex)
        self.assertTrue(
            np.array_equal(
                cnot,
                testCircuit._operator_cache["CX1,0"]))
        reverse_cnot = np.array(
            [[1,0,0,0],
             [0,0,0,1],
             [0,0,1,0],
             [0,1,0,0]],
             dtype = complex)
        self.assertTrue(
            np.array_equal(
                reverse_cnot,
                testCircuit._operator_cache["CX0,1"]))
        print("test_cnot_compilation: Test passed")

    def test_cnot_execution(self):
        for i in range(2, MAX_QUBITS + 1):
            qubits = i
            testCircuit = Circuit(qubits, operator_cache = True)

            ## Test flipping a target when the control wire is 1
            testCircuit.apply_operator("X0")
            # Apply CNOT that targets last wire
            testCircuit.apply_operator(f"CNOT{qubits - 1},0")
            testCircuit.apply_operator("X0")
            circuit_state = testCircuit.DEBUG_get_circuit_state()
            # Check the 1st index
            # i.e. the circuit state is transformed to |0>⊗(n-1)|1>
            self.assertEqual(circuit_state[1], 1 + 0j)

            ## Test doing nothing when the control wire is 0
            # Apply CNOT that targets last wire
            testCircuit.apply_operator(f"CNOT{qubits - 1},0")
            # Check the 1st index
            # i.e. the circuit state is still |0>⊗(n-1)|1>
            self.assertEqual(circuit_state[1], 1 + 0j)

            print(f"test_cnot_execution: Test passed with {i} qubits")

    def test_entanglement(self):
        for i in range(2, MAX_QUBITS + 1):
            qubits = i
            outcome_ghz_0 = np.zeros(2 ** qubits, dtype = complex)
            outcome_ghz_0[0] = 1 + 0j
            outcome_ghz_1 = np.zeros(2 ** qubits, dtype = complex)
            outcome_ghz_1[(2 ** qubits) - 1] = 1 + 0j
            samples = 100
            testCircuit = Circuit(qubits, operator_cache = True)
            for j in range(0, samples):
                # Reset circuit and apply Hadamard on first wire
                testCircuit.reset_circuit_state()
                testCircuit.apply_operator("H0")
                for k in range(0, qubits - 1):
                    testCircuit.apply_operator(f"CNOT{k+1},{k}")
                # Collapse state
                testCircuit.measure()
                # Check that it collapses to one of the two GHZ states
                state = testCircuit.DEBUG_get_circuit_state()
                if not (np.array_equal(outcome_ghz_0, state) or
                        np.array_equal(outcome_ghz_1, state)):
                    self.fail(f"test_entanglement: Test failed with {i} " +
                              "qubits, circuit collapsed to a state which was" +
                             " not a GHZ state")
            print(f"test_entanglement: Test passed with {i} qubits")

    def test_generate_bitstring(self):
        for i in range(1, MAX_QUBITS + 1):
            qubits = i
            testCircuit = Circuit(qubits)
            for j in range(2 ** qubits):
                converted_generated_bitstring = convert_bitstring_to_decimal(
                    testCircuit.generate_bitstring(j))
                self.assertEqual(
                    j,
                    converted_generated_bitstring,
                    f"test_generate_bitstring: Test failed with {i} qubits, " +
                     "generate_bitstring() generated an incorrect bitstring." +
                    f" Expected {j}, received {converted_generated_bitstring}")
            print(f"test_generate_bitstring: Test passed with {i} qubits")
