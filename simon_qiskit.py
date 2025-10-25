# simon_qiskit.py
# Requires: qiskit, qiskit-aer, numpy
# pip install qiskit qiskit-aer numpy

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator # Changed import
import numpy as np
import random
from collections import defaultdict

# -----------------------
# Utilities: bit conversions
# -----------------------
def int_to_bits(x, n):
    return [(x >> i) & 1 for i in reversed(range(n))]

def bits_to_int(bits):
    x = 0
    for b in bits:
        x = (x << 1) | (int(b) & 1)
    return x

# -----------------------
# Build a classical Simon function f: {0,1}^n -> {0,1}^n
# Represented as a dict mapping int(x) -> int(f(x))
# Ensure f(x) = f(x ^ s) for all x.
# We do this by partitioning the 2^n inputs into pairs (x, x^s) and assigning each pair a unique n-bit output.
# For s = 0, f is one-to-one.
# -----------------------
def build_simon_function(n, s_int):
    N = 1 << n
    s_bits = int_to_bits(s_int, n)
    seen = [False] * N
    mapping = {}
    next_output = 0
    for x in range(N):
        if seen[x]:
            continue
        y = x ^ s_int
        # If s=0 then y == x; pair is a singleton
        if y == x:
            # unique mapping to next_output
            mapping[x] = next_output
            seen[x] = True
            next_output += 1
        else:
            # pair (x, y)
            mapping[x] = next_output
            mapping[y] = next_output
            seen[x] = seen[y] = True
            next_output += 1
    # map outputs to n-bit integers (we may reuse next_output as label; make sure it's n-bit)
    # If next_output might be > 2^n - 1 (it won't), we would hash; but for this construction next_output <= 2^n
    # For safety, convert label to an n-bit integer (fits).
    # mapping values are already labels 0.. <=2^n-1
    return mapping

# -----------------------
# Build an oracle quantum circuit implementing U_f: |x>|0> -> |x>|f(x)>
# We'll implement the oracle by, for each x in domain, flipping output qubits to match f(x) using multi-controlled X gates.
# For small n this is fine. For larger n you'd build more optimized reversible circuits.
# -----------------------
def build_oracle_circuit(n, mapping):
    qc = QuantumCircuit(2*n, name='U_f')
    # input qubits: 0..n-1 ; output qubits: n..2n-1
    for x, fx in mapping.items():
        x_bits = int_to_bits(x, n)
        fx_bits = int_to_bits(fx, n)
        # For each output bit that should be 1, apply a multi-controlled X controlled by the input qubits
        # Implement multi-control by using the `mcx` method (Qiskit supports ancilla-less for small numbers), but
        # to avoid ancilla complexity, we use technique: apply X to control qubits where control should be 0, then mcx, then undo.
        control_qubits = list(range(n))
        target = [n + i for i, b in enumerate(fx_bits) if b == 1]
        if len(target) == 0:
            continue
        # For each target bit, apply multi-controlled X with controls matching x_bits
        for t in target:
            # Prepare controls: flip those control qubits where x_bit==0
            for idx, bit in enumerate(x_bits):
                if bit == 0:
                    qc.x(idx)
            # apply multi-controlled X to target t controlled by all input qubits
            if n == 0:
                qc.x(t)
            elif n == 1:
                qc.cx(0, t)
            else:
                # Use mcx (multi-controlled Toffoli), which replaced mct
                qc.mcx(list(range(n)), t) # Changed from mct to mcx
            # Undo the control flips
            for idx, bit in enumerate(x_bits):
                if bit == 0:
                    qc.x(idx)
    return qc

# -----------------------
# Simon algorithm circuit builder
# -----------------------
def simon_circuit(n, oracle_qc):
    qc = QuantumCircuit(2*n, n)  # measure only first n bits
    # Apply H on input register
    qc.h(range(n))
    # Append oracle (careful with registers alignment)
    qc.compose(oracle_qc, inplace=True)
    # Apply H again on input
    qc.h(range(n))
    # Measure input register to classical bits
    qc.measure(range(n), range(n))
    return qc

# -----------------------
# Run on Aer simulator and collect measurement results
# -----------------------
def run_simon(n, s_int, shots=1024):
    mapping = build_simon_function(n, s_int)
    oracle = build_oracle_circuit(n, mapping)
    circ = simon_circuit(n, oracle)
    # draw circuit if you want: print(circ.draw())
    backend = AerSimulator() # Changed simulator initialization
    # transpile into a form where we'll run statevector or qasm
    job = backend.run(circ, shots=shots) # Changed from execute() to backend.run()
    result = job.result()
    counts = result.get_counts()
    return counts, circ

# -----------------------
# Classical postprocessing: solve for s (GF(2) linear algebra)
# Given measured strings y satisfying y·s=0, collect n-1 independent rows to solve.
# We'll use Gaussian elimination mod 2 to find s (up to 2 solutions when s=0 => trivial).
# -----------------------
def solve_for_s_from_measurements(n, measured_bitstrings):
    # measured_bitstrings: list of strings like '010'
    # Build matrix over GF(2). Each measured string is a row vector; we want the nullspace vector s != 0 (if exists)
    # We'll collect rows and perform elimination to find a non-trivial s.
    rows = []
    # Convert bitstrings to integer rows
    for b in measured_bitstrings:
        rows.append([int(ch) for ch in b])
    # Gaussian elimination to row echelon form
    # We'll find the nullspace by finding vector s where rows * s = 0
    # Convert to numpy for convenience
    A = np.array(rows, dtype=int)
    # If A has fewer than n-1 independent rows, algorithm may need more shots
    # We'll compute nullspace over GF(2) using simple elimination
    # Form augmented matrix? We solve A s = 0.
    # Compute nullspace by performing row reduction and extracting free variables.
    # Use basic GF(2) elimination
    A = A.copy()
    r, c = A.shape if A.size else (0, n)
    # pad rows if needed
    if r == 0:
        return None
    rank = 0
    pivot_cols = []
    for col in range(n):
        # find pivot row with A[row,col] == 1 for row >= rank
        pivot = None
        for row in range(rank, r):
            if A[row, col] == 1:
                pivot = row
                break
        if pivot is None:
            continue
        # swap
        if pivot != rank:
            A[[pivot, rank]] = A[[rank, pivot]]
        pivot_cols.append(col)
        # eliminate below
        for row in range(rank+1, r):
            if A[row, col] == 1:
                A[row] ^= A[rank]  # xor row
        rank += 1
        if rank == r:
            break
    # If rank < n, nullspace dimension >= 1. Find one non-zero vector s in nullspace.
    # We'll solve by setting free variables to produce a non-zero s.
    if rank == n:
        # Only trivial solution
        return 0  # s = 0
    # find a vector in nullspace:
    # We can brute-force all 2^n candidates small n; but for generality perform back-substitution:
    # We'll select one free column, set it to 1, others free=0, then solve for pivot variables.
    pivot_set = set(pivot_cols)
    free_cols = [col for col in range(n) if col not in pivot_set]
    if len(free_cols) == 0:
        return 0
    # Build reduced echelon form for back-substitution (we already have upper-triangular)
    # We'll create an augmented matrix for solving A_reduced * s = 0. We will pick s[free_cols[0]] = 1
    s = [0]*n
    free_choice = free_cols[0]
    s[free_choice] = 1
    # Backsolve for pivot variables from bottom to top
    # Work on the rows of A (which are r x n, in echelon form).
    for i in reversed(range(rank)):
        # find pivot col for this row
        row = A[i]
        pivot_col = None
        for j in range(n):
            if row[j] == 1:
                pivot_col = j
                break
        if pivot_col is None:
            continue
        # compute rhs = sum(row[j]*s[j]) for j>pivot_col
        rhs = 0
        for j in range(pivot_col+1, n):
            rhs ^= (row[j] & s[j])
        s[pivot_col] = rhs  # because total must be 0 => pivot * s[pivot] ^ rhs = 0 => s[pivot] = rhs
    return bits_to_int(s)

# -----------------------
# Enhanced solver with dependency checking and validation
# -----------------------
def check_linear_independence(vectors, n):
    """Check if vectors are linearly independent over GF(2)"""
    if not vectors:
        return False, 0
    A = np.array([[int(ch) for ch in v] for v in vectors], dtype=int)
    # Row reduction to find rank
    A = A.copy()
    r, c = A.shape
    rank = 0
    for col in range(min(n, r)):
        pivot = None
        for row in range(rank, r):
            if A[row, col] == 1:
                pivot = row
                break
        if pivot is None:
            continue
        if pivot != rank:
            A[[pivot, rank]] = A[[rank, pivot]]
        for row in range(rank+1, r):
            if A[row, col] == 1:
                A[row] ^= A[rank]
        rank += 1
        if rank == r:
            break
    return rank >= n - 1, rank

def solve_for_s_enhanced(n, measured_bitstrings, verbose=False):
    """Enhanced solver with detailed diagnostics"""
    if not measured_bitstrings:
        return None, "No measurements"

    # Remove '0000...' uninformative measurements
    useful_measurements = [m for m in measured_bitstrings if m != '0'*n]

    if not useful_measurements:
        return None, "All measurements uninformative (y=0...0)"

    # Check linear independence
    is_independent, rank = check_linear_independence(useful_measurements, n)

    if verbose:
        print(f"  Measured vectors: {set(measured_bitstrings)}")
        print(f"  Useful vectors: {set(useful_measurements)}")
        print(f"  Rank: {rank}/{n-1} needed")

    if not is_independent and rank < n - 1:
        return None, f"Insufficient independent vectors (rank={rank}, need {n-1})"

    # Solve using the original solver
    s_int = solve_for_s_from_measurements(n, useful_measurements)
    return s_int, "Success"

# -----------------------
# Simulate noisy measurements (for hardware failure case)
# -----------------------
def add_measurement_noise(counts, noise_prob=0.3):
    """Simulate hardware noise by flipping bits in measurement results"""
    noisy_counts = {}
    for bitstring, count in counts.items():
        # Randomly corrupt some measurements
        if random.random() < noise_prob:
            # Flip a random bit
            bits = list(bitstring)
            flip_pos = random.randint(0, len(bits)-1)
            bits[flip_pos] = '1' if bits[flip_pos] == '0' else '0'
            noisy_bitstring = ''.join(bits)
            noisy_counts[noisy_bitstring] = noisy_counts.get(noisy_bitstring, 0) + count
        else:
            noisy_counts[bitstring] = noisy_counts.get(bitstring, 0) + count
    return noisy_counts

# -----------------------
# Test case executor
# -----------------------
def run_test_case(case_num, description, n, s_int, shots=1024,
                  limit_measurements=None, add_noise=False, max_retries=3):
    """Run a single test case with detailed output"""
    s_str = format(s_int, f'0{n}b')
    print(f"\n{'='*80}")
    print(f"Case {case_num}: {description}")
    print(f"{'='*80}")
    print(f"Input: n={n}, s={s_str}")
    print(f"Expected: {description}")

    for attempt in range(max_retries):
        if attempt > 0:
            print(f"\n--- Retry #{attempt} ---")

        # Run Simon's algorithm
        counts, circ = run_simon(n, s_int, shots=shots)

        # Add noise if simulating hardware failure
        if add_noise:
            counts = add_measurement_noise(counts, noise_prob=0.4)
            print(f"Simulated hardware noise applied")

        # Extract measurements
        measured = []
        for k, v in counts.items():
            reversed_k = k[::-1]
            measured.append(reversed_k)

        # Limit measurements if needed (for dependency failure)
        if limit_measurements:
            measured = measured[:limit_measurements]

        print(f"Measurements obtained: {set(measured)}")

        # Solve for s
        s_found, status = solve_for_s_enhanced(n, measured, verbose=True)

        if s_found is not None:
            s_found_str = format(s_found, f'0{n}b')
            print(f"\nResult: SUCCESS")
            print(f"Recovered s = {s_found_str}")

            if s_found == s_int:
                print(f"Verification: CORRECT (matches expected s={s_str})")
                return True
            else:
                print(f"Verification: INCORRECT (expected s={s_str})")
                if add_noise:
                    print(f"Status: Hardware noise corrupted the result - RETRY")
                    continue
                return False
        else:
            print(f"\nResult: FAILURE")
            print(f"Reason: {status}")
            print(f"Status: RETRY needed")
            if attempt < max_retries - 1:
                continue
            else:
                print(f"Max retries reached")
                return False

    return False

# -----------------------
# Main test suite - All 6 cases from synopsis
# -----------------------
if __name__ == "__main__":
    print("="*80)
    print("SIMON'S ALGORITHM - COMPREHENSIVE TEST SUITE")
    print("Implementation of Simon's algorithm for different cases")
    print("="*80)

    # Case 1: Trivial Success (s=0000)
    run_test_case(
        case_num=1,
        description="Trivial success",
        n=4,
        s_int=0b0000,
        shots=1024
    )

    # Case 2: Ideal Success (s=1101)
    run_test_case(
        case_num=2,
        description="Ideal success",
        n=4,
        s_int=0b1101,
        shots=1024
    )

    # Case 3: Failure (dependency) - insufficient independent vectors
    # We simulate this by limiting the number of distinct measurements
    print(f"\n{'='*80}")
    print(f"Case 3: Failure (dependency)")
    print(f"{'='*80}")
    print(f"Input: n=4, s=1101")
    print(f"Expected: Insufficient independent y vectors - Retry")

    # Manually create dependent measurements to demonstrate the failure
    n = 4
    s_int = 0b1101
    # Create only 2 dependent measurements (need 3 independent for n=4)
    dependent_measurements = ['0110', '0110']  # Same vector repeated
    s_found, status = solve_for_s_enhanced(n, dependent_measurements, verbose=True)
    if s_found is None:
        print(f"\nResult: FAILURE")
        print(f"Reason: {status}")
        print(f"Status: RETRY needed")

    # Case 4: Failure (uninformative y) - measures only y=0000
    print(f"\n{'='*80}")
    print(f"Case 4: Failure (uninformative y)")
    print(f"{'='*80}")
    print(f"Input: n=4, s=1101")
    print(f"Expected: Measures uninformative y=0000 - Retry")

    # Manually create uninformative measurements
    uninformative_measurements = ['0000', '0000', '0000']
    s_found, status = solve_for_s_enhanced(n, uninformative_measurements, verbose=True)
    if s_found is None:
        print(f"\nResult: FAILURE")
        print(f"Reason: {status}")
        print(f"Status: RETRY needed")

    # Case 5: Realistic Success - redundant y vectors but still recovers
    print(f"\n{'='*80}")
    print(f"Case 5: Realistic success")
    print(f"{'='*80}")
    print(f"Input: n=4, s=1101")
    print(f"Expected: Redundant y vectors measured but recovers s")

    # Run with more shots to get redundant measurements
    counts, circ = run_simon(4, 0b1101, shots=2048)
    measured = [k[::-1] for k in counts.keys()]
    print(f"Measurements obtained: {set(measured)}")
    s_found, status = solve_for_s_enhanced(4, measured, verbose=True)
    if s_found is not None:
        s_found_str = format(s_found, '04b')
        print(f"\nResult: SUCCESS")
        print(f"Recovered s = {s_found_str}")
        print(f"Verification: {'CORRECT' if s_found == 0b1101 else 'INCORRECT'}")

    # Case 6: Hardware Failure - noisy measurements
    run_test_case(
        case_num=6,
        description="Hardware failure (noisy run)",
        n=4,
        s_int=0b1101,
        shots=1024,
        add_noise=True,
        max_retries=3
    )

    # Summary table
    print(f"\n{'='*80}")
    print("SUMMARY TABLE")
    print(f"{'='*80}")
    print(f"{'Case':<6} {'n':<4} {'s':<8} {'Description':<30} {'Expected Result':<20}")
    print(f"{'-'*80}")
    print(f"{'1':<6} {'4':<4} {'0000':<8} {'Trivial success':<30} {'s=0000':<20}")
    print(f"{'2':<6} {'4':<4} {'1101':<8} {'Ideal success':<30} {'Recovers s':<20}")
    print(f"{'3':<6} {'4':<4} {'1101':<8} {'Failure (dependency)':<30} {'Retry':<20}")
    print(f"{'4':<6} {'4':<4} {'1101':<8} {'Failure (uninformative y)':<30} {'Retry':<20}")
    print(f"{'5':<6} {'4':<4} {'1101':<8} {'Realistic success':<30} {'Recovers s':<20}")
    print(f"{'6':<6} {'4':<4} {'1101':<8} {'Hardware failure':<30} {'Retry':<20}")
    print(f"{'='*80}")


