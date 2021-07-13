import numpy as np
import cirq


def main(num_qubits=8):
    # Setup non-eavesdropped protocol
    print('Simulating non-eavesdropped protocol')
    alice_basis = [np.random.randint(0, 2) for _ in range(num_qubits)]
    alice_state = [np.random.randint(0, 2) for _ in range(num_qubits)]
    bob_basis = [np.random.randint(0, 2) for _ in range(num_qubits)]

    expected_key = bitstring(
        [alice_state[i] for i in range(num_qubits) if alice_basis[i] == bob_basis[i]]
    )

    circuit = make_bb84_circ(num_qubits, alice_basis, bob_basis, alice_state)

    # Run simulations.
    repetitions = 1

    result = cirq.Simulator().run(program=circuit, repetitions=repetitions)
    result_bitstring = bitstring([int(result.measurements[str(i)]) for i in range(num_qubits)])

    # Take only qubits where bases match
    obtained_key = ''.join(
        [result_bitstring[i] for i in range(num_qubits) if alice_basis[i] == bob_basis[i]]
    )

    assert expected_key == obtained_key, "Keys don't match"
    print(circuit)
    print_results(alice_basis, bob_basis, alice_state, expected_key, obtained_key)

    # Setup eavesdropped protocol
    print('Simulating eavesdropped protocol')
    np.random.seed(200)  # Seed random generator for consistent results
    alice_basis = [np.random.randint(0, 2) for _ in range(num_qubits)]
    alice_state = [np.random.randint(0, 2) for _ in range(num_qubits)]
    bob_basis = [np.random.randint(0, 2) for _ in range(num_qubits)]
    eve_basis = [np.random.randint(0, 2) for _ in range(num_qubits)]

    expected_key = bitstring(
        [alice_state[i] for i in range(num_qubits) if alice_basis[i] == bob_basis[i]]
    )

    # Eve intercepts the qubits

    alice_eve_circuit = make_bb84_circ(num_qubits, alice_basis, eve_basis, alice_state)

    # Run simulations.
    repetitions = 1
    result = cirq.Simulator().run(program=alice_eve_circuit, repetitions=repetitions)
    eve_state = [int(result.measurements[str(i)]) for i in range(num_qubits)]

    eve_bob_circuit = make_bb84_circ(num_qubits, eve_basis, bob_basis, eve_state)

    # Run simulations.
    repetitions = 1
    result = cirq.Simulator().run(program=eve_bob_circuit, repetitions=repetitions)
    result_bitstring = bitstring([int(result.measurements[str(i)]) for i in range(num_qubits)])

    # Take only qubits where bases match
    obtained_key = ''.join(
        [result_bitstring[i] for i in range(num_qubits) if alice_basis[i] == bob_basis[i]]
    )

    assert expected_key != obtained_key, "Keys shouldn't match"

    circuit = alice_eve_circuit + eve_bob_circuit
    print(circuit)
    print_results(alice_basis, bob_basis, alice_state, expected_key, obtained_key)


def make_bb84_circ(num_qubits, alice_basis, bob_basis, alice_state):

    qubits = [cirq.LineQubit(i) for i in range(num_qubits)]

    circuit = cirq.Circuit()

    # Alice prepares her qubits
    alice_enc = []
    for index, _ in enumerate(alice_basis):
        if alice_state[index] == 1:
            alice_enc.append(cirq.X(qubits[index]))
        if alice_basis[index] == 1:
            alice_enc.append(cirq.H(qubits[index]))

    circuit.append(alice_enc)

    # Bob measures the received qubits
    bob_basis_choice = []
    for index, _ in enumerate(bob_basis):
        if bob_basis[index] == 1:
            bob_basis_choice.append(cirq.H(qubits[index]))

    circuit.append(bob_basis_choice)
    circuit.append(cirq.measure_each(*qubits))

    return circuit


def bitstring(bits):
    return ''.join(str(int(b)) for b in bits)


def print_results(alice_basis, bob_basis, alice_state, expected_key, obtained_key):
    num_qubits = len(alice_basis)
    basis_match = ''.join(
        ['X' if alice_basis[i] == bob_basis[i] else '_' for i in range(num_qubits)]
    )
    alice_basis_str = "".join(['C' if alice_basis[i] == 0 else "H" for i in range(num_qubits)])
    bob_basis_str = "".join(['C' if bob_basis[i] == 0 else "H" for i in range(num_qubits)])

    print('Alice\'s basis:\t{}'.format(alice_basis_str))
    print('Bob\'s basis:\t{}'.format(bob_basis_str))
    print('Alice\'s bits:\t{}'.format(bitstring(alice_state)))
    print(f'Bases match::\t{basis_match}')
    print(f'Expected key:\t{expected_key}')
    print(f'Actual key:\t{obtained_key}')


if __name__ == "__main__":
    main()