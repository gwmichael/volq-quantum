import pytest as pt
import numpy as np
import volq as v
import volq.exceptions as ve

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

def generate_uniform_single_gate_circuit_dsl(gate: str, qubits: int):
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

# The warning protected-access is suppressed because encapsulated attributes
# are never accessed in production code, only for testing purposes.

# pylint: disable=protected-access

def test_initialise_circuit():
    for i in range(1, MAX_QUBITS + 1):
        qubits = i
        test_circuit = v.Circuit(qubits)
        expected_state = generate_ket_0_state(qubits)
        assert np.array_equal(test_circuit.get_circuit_state(), expected_state)

def test_invalid_qubits():
    # Test zero
    with pt.raises(ve.VolqSyntaxError):
        v.Circuit(0)
    # Test negative
    with pt.raises(ve.VolqSyntaxError):
        v.Circuit(-1)

def test_invalid_gates():
    test_circuit = v.Circuit(2)
    ## Syntactically incorrect operator testing
    # Empty/no gates
    with pt.raises(ve.VolqSyntaxError):
        test_circuit.apply_operator("")
    # Gate only
    with pt.raises(ve.VolqSyntaxError):
        test_circuit.apply_operator("H")
    # Index only
    with pt.raises(ve.VolqSyntaxError):
        test_circuit.apply_operator("00")
    # Whitespace
    with pt.raises(ve.VolqSyntaxError):
        test_circuit.apply_operator("  ")
    # Symbols that are not valid syntax
    with pt.raises(ve.VolqSyntaxError):
        test_circuit.apply_operator("!!")

    # Test too many gates
    with pt.raises(ve.VolqSyntaxError):
        test_circuit.apply_operator("H0 H1 H2")

    # Test gate outside index
    with pt.raises(ve.VolqSyntaxError):
        test_circuit.apply_operator("H9999")
    with pt.raises(ve.VolqSyntaxError):
        test_circuit.apply_operator("CNOT0,9999")
    with pt.raises(ve.VolqSyntaxError):
        test_circuit.apply_operator("CNOT9999,0")

    # Test invalid syntax splitting indices in a controlled gate
    with pt.raises(ve.VolqSyntaxError):
        test_circuit.apply_operator("CNOT0;1")
    with pt.raises(ve.VolqSyntaxError):
        test_circuit.apply_operator("CNOT0#1")
    with pt.raises(ve.VolqSyntaxError):
        test_circuit.apply_operator("CNOT0.1")

def test_equivalent_cached_operators():
    test_circuit = v.Circuit(4, operator_cache = True)
    # Test ordering
    assert "H0 H1 H2 H3" not in test_circuit._context._operator_cache
    test_circuit.apply_operator("H3 H1 H2 H0")
    assert "H0 H1 H2 H3" in test_circuit._context._operator_cache

    # Test prepending padding
    assert "I0 H1 H2 H3" not in test_circuit._context._operator_cache
    test_circuit.apply_operator("H1 H2 H3")
    assert "I0 H1 H2 H3" in test_circuit._context._operator_cache

    # Test appending padding
    assert "H0 I1 I2 I3" not in test_circuit._context._operator_cache
    test_circuit.apply_operator("H0")
    assert "H0 I1 I2 I3" in test_circuit._context._operator_cache

    # Test prepending padding and appending padding
    assert "I0 H1 I2 I3" not in test_circuit._context._operator_cache
    test_circuit.apply_operator("H1")
    assert "I0 H1 I2 I3" in test_circuit._context._operator_cache

    # Test prepending padding, appending padding, and ordering
    assert "I0 H1 H2 I3" not in test_circuit._context._operator_cache
    test_circuit.apply_operator("H2 H1")
    assert "I0 H1 H2 I3" in test_circuit._context._operator_cache

    # Alias translation testing is separate,
    # in order to test all possible aliases

def test_single_qubit_gate_start():
    for gate in SINGLE_QUBIT_GATES:
        for i in range(1, MAX_QUBITS + 1):
            qubits = i
            test_circuit = v.Circuit(qubits)
            zero_state = generate_ket_0_state(qubits)
            expected_state = zero_state
            U = SINGLE_QUBIT_GATES[gate]
            for _ in range(1, i):
                U = np.kron(U, IDENTITY)
            expected_state = np.dot(U, expected_state)
            test_circuit.apply_operator(gate + "0")
            assert np.array_equal(
                test_circuit.get_circuit_state(), expected_state)

def test_single_qubit_gate_end():
    for gate in SINGLE_QUBIT_GATES:
        for i in range(1, MAX_QUBITS + 1):
            qubits = i
            test_circuit = v.Circuit(qubits)
            expected_state = generate_ket_0_state(qubits)
            U = np.array([1], dtype = complex)
            for _ in range(0, i - 1):
                U = np.kron(U, IDENTITY)
            U = np.kron(U, SINGLE_QUBIT_GATES[gate])
            expected_state = np.dot(U, expected_state)
            test_circuit.apply_operator(gate + str(i - 1))
            assert np.array_equal(
                test_circuit.get_circuit_state(), expected_state)

def test_uniform_single_qubit_gate():
    for gate in SINGLE_QUBIT_GATES:
        for i in range(1, MAX_QUBITS + 1):
            qubits = i
            test_circuit = v.Circuit(qubits)
            expected_state = generate_ket_0_state(qubits)
            U = np.array([1], dtype = complex)
            for _ in range(0, i):
                U = np.kron(SINGLE_QUBIT_GATES[gate], U)
            expected_state = np.dot(U, expected_state)
            U_key = generate_uniform_single_gate_circuit_dsl(gate, qubits)
            test_circuit.apply_operator(U_key)
            assert np.array_equal(
                test_circuit.get_circuit_state(), expected_state)

def test_measurement():
    for i in range(1, MAX_QUBITS + 1):
        qubits = i
        test_circuit = v.Circuit(qubits)
        # test_circuit is initialised as |0..0>, check that we measure zero
        expected_state = generate_ket_0_state(qubits)
        test_circuit.measure()
        assert np.array_equal(test_circuit.get_circuit_state(), expected_state)

        # Apply X⊗n to test_circuit to get the state |1..1>
        # Then apply measurement and check
        expected_state = generate_ket_1_state(qubits)
        test_circuit.apply_operator(
            generate_uniform_single_gate_circuit_dsl("X", qubits))
        test_circuit.measure()
        assert np.array_equal(test_circuit.get_circuit_state(), expected_state)

        # Revert circuit to |0..0> and apply Y⊗n to get |i..i>,
        # Then check that it collapses to |1..1>
        expected_state = generate_ket_1_state(qubits)
        test_circuit.apply_operator(
            generate_uniform_single_gate_circuit_dsl("X", qubits))
        test_circuit.apply_operator(
            generate_uniform_single_gate_circuit_dsl("Y", qubits))
        test_circuit.measure()
        assert np.array_equal(test_circuit.get_circuit_state(), expected_state)

def test_random_measurement_sampling():
    for i in range(1, MAX_QUBITS + 1):
        qubits = i
        samples = (2 ** qubits) / 2
        coverage_threshold = 0.375
        test_passed = False
        reruns = 5
        while reruns != 0:
            test_circuit = v.Circuit(qubits, operator_cache = True)
            seen_states = set()
            for _ in range(0, int(samples)):
                test_circuit.reset_circuit_state()
                test_circuit.apply_operator(
                    generate_uniform_single_gate_circuit_dsl("H", qubits))
                test_circuit.measure()
                collapsed_state = test_circuit.get_circuit_state()
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
        assert test_passed

def test_partial_superposition_measurement():
    for i in range(2, MAX_QUBITS + 1):
        qubits = i
        test_circuit = v.Circuit(qubits, operator_cache = True)
        repeats = 10
        accepted_0_state = np.zeros(2 ** qubits, dtype = complex)
        accepted_0_state[0] = 1 + 0j
        accepted_1_state = np.zeros(2 ** qubits, dtype = complex)
        accepted_1_state[2 ** (qubits - 1)] = 1 + 0j
        for _ in range(0, repeats):
            test_circuit.reset_circuit_state()
            test_circuit.apply_operator("H0")
            test_circuit.measure()
            measured_state = test_circuit.get_circuit_state()
            assert np.array_equal(accepted_0_state, measured_state)\
                or np.array_equal(accepted_1_state, measured_state)

def test_alias_translation():
    test_circuit = v.Circuit(4, operator_cache = True)

    # CNOT -> CX
    assert "CX0,1 I2 I3" not in test_circuit._context._operator_cache
    test_circuit.apply_operator("CNOT0,1")
    assert "CX0,1 I2 I3" in test_circuit._context._operator_cache

    # TOFFOLI -> CCX
    assert "CCX0,1,2 I3" not in test_circuit._context._operator_cache
    test_circuit.apply_operator("TOFFOLI0,1,2")
    assert "CCX0,1,2 I3" in test_circuit._context._operator_cache

    # TOFF -> CCX
    assert "I0 CCX1,2,3" not in test_circuit._context._operator_cache
    test_circuit.apply_operator("TOFF1,2,3")
    assert "I0 CCX1,2,3" in test_circuit._context._operator_cache

def test_cnot_compilation():
    test_circuit = v.Circuit(2, operator_cache = True)
    test_circuit.apply_operator("CNOT1,0")
    test_circuit.apply_operator("CNOT0,1")
    # Check correctness against known correct CNOT matrix
    cnot = np.array(
        [[1,0,0,0],
         [0,1,0,0],
         [0,0,0,1],
         [0,0,1,0]],
        dtype = complex)
    assert np.array_equal(cnot, test_circuit._context._operator_cache["CX1,0"])
    reverse_cnot = np.array(
        [[1,0,0,0],
         [0,0,0,1],
         [0,0,1,0],
         [0,1,0,0]],
        dtype = complex)
    assert np.array_equal(
        reverse_cnot, test_circuit._context._operator_cache["CX0,1"])

def test_cnot_execution():
    for i in range(2, MAX_QUBITS + 1):
        qubits = i
        test_circuit = v.Circuit(qubits, operator_cache = True)

        ## Test flipping a target when the control wire is 1
        test_circuit.apply_operator("X0")
        # Apply CNOT that targets last wire
        test_circuit.apply_operator(f"CNOT{qubits - 1},0")
        test_circuit.apply_operator("X0")
        circuit_state = test_circuit.get_circuit_state()
        # Check the 1st index
        # i.e. the circuit state is transformed to |0>⊗(n-1)|1>
        assert circuit_state[1] == 1 + 0j

        ## Test doing nothing when the control wire is 0
        # Apply CNOT that targets last wire
        test_circuit.apply_operator(f"CNOT{qubits - 1},0")
        # Check the 1st index
        # i.e. the circuit state is still |0>⊗(n-1)|1>
        assert circuit_state[1] == 1 + 0j

def test_entanglement():
    for i in range(2, MAX_QUBITS + 1):
        qubits = i
        outcome_ghz_0 = np.zeros(2 ** qubits, dtype = complex)
        outcome_ghz_0[0] = 1 + 0j
        outcome_ghz_1 = np.zeros(2 ** qubits, dtype = complex)
        outcome_ghz_1[(2 ** qubits) - 1] = 1 + 0j
        samples = 100
        test_circuit = v.Circuit(qubits, operator_cache = True)
        for _ in range(0, samples):
            # Reset circuit and apply Hadamard on first wire
            test_circuit.reset_circuit_state()
            test_circuit.apply_operator("H0")
            for k in range(0, qubits - 1):
                test_circuit.apply_operator(f"CNOT{k+1},{k}")
            # Collapse state
            test_circuit.measure()
            # Check that it collapses to one of the two GHZ states
            state = test_circuit.get_circuit_state()
            if not (np.array_equal(outcome_ghz_0, state) or
                    np.array_equal(outcome_ghz_1, state)):
                pt.fail(f"test_entanglement: Test failed with {i} " +
                            "qubits, circuit collapsed to a state which was" +
                            " not a GHZ state")

def test_generate_bitstring():
    for i in range(1, MAX_QUBITS + 1):
        qubits = i
        test_circuit = v.Circuit(qubits)
        for j in range(2 ** qubits):
            converted_generated_bitstring = convert_bitstring_to_decimal(
                test_circuit.generate_bitstring(j))
            assert j == converted_generated_bitstring
