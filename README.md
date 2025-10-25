# Simon's Algorithm Implementation in Qiskit

## Abstract

Simon's algorithm is a foundational quantum algorithm that demonstrates an exponential separation between quantum and classical query complexity. Given a black-box function **f:{0,1}^n→{0,1}^m** with the promise that there exists a secret bit-string **s∈{0,1}^n** such that **f(x)=f(y) iff y=x⊕s**, the goal is to determine **s**.

The quantum subroutine uses superposition and interference to obtain linear equations about **s** (over GF(2)); repeated measurements yield enough independent equations to solve for **s** by Gaussian elimination.

This project implements Simon's algorithm in **Qiskit**, demonstrates it on multiple n-bit cases (including trivial, nontrivial, and noisy/approximate scenarios), and compares simulator and hardware behaviour.

---

## Table of Contents

- [Background](#background)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Test Cases](#test-cases)
- [Algorithm Overview](#algorithm-overview)
- [Mathematical Foundation](#mathematical-foundation)
- [Expected Results](#expected-results)
- [Project Structure](#project-structure)
- [References](#references)

---

## Background

**Simon's Algorithm** (1994) was one of the first quantum algorithms to show exponential speedup over classical algorithms. It inspired **Shor's factoring algorithm** and demonstrated that quantum computers could solve certain problems fundamentally faster than classical computers.

### Complexity Comparison

| Approach | Query Complexity |
|----------|-----------------|
| Classical (deterministic) | O(2^(n/2)) |
| Classical (probabilistic) | O(2^(n/2)) |
| **Quantum (Simon's)** | **O(n)** |

This exponential speedup demonstrates quantum supremacy for this problem class.

---

## Features

- ✅ **Complete implementation** of Simon's algorithm using Qiskit
- ✅ **Oracle construction** for arbitrary secret strings
- ✅ **Gaussian elimination** solver over GF(2)
- ✅ **Six comprehensive test cases** covering:
  - Trivial case (s=0)
  - Ideal success scenario
  - Failure modes (dependency, uninformative measurements)
  - Realistic scenarios with redundancy
  - Hardware noise simulation
- ✅ **Linear independence checking** for measurement validation
- ✅ **Automated retry logic** for failure cases
- ✅ **Detailed diagnostics** and verbose output

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download this repository**

```bash
cd C:\Users\DEADSERPENT\Music\QISKIT
```

2. **Install required packages**

```bash
pip install qiskit qiskit-aer numpy
```

### Dependencies

- `qiskit >= 1.1.0` - IBM's quantum computing framework
- `qiskit-aer >= 0.17.0` - High-performance simulators
- `numpy >= 1.16.3` - Numerical computing

---

## Usage

### Run the complete test suite

```bash
python simon_qiskit.py
```

This will execute all 6 test cases and display detailed results.

### Run custom test case

Modify the main section to test your own secret string:

```python
if __name__ == "__main__":
    n = 4  # Number of bits
    s_int = 0b1101  # Secret string (binary)

    counts, circ = run_simon(n, s_int, shots=1024)
    measured = [k[::-1] for k in counts.keys()]
    s_found, status = solve_for_s_enhanced(n, measured, verbose=True)

    print(f"Recovered s: {format(s_found, f'0{n}b')}")
```

### Visualize the quantum circuit

```python
counts, circ = run_simon(4, 0b1101, shots=1024)
print(circ.draw())
```

---

## Test Cases

### Case 1: Trivial Success
- **Input:** n=4, s=0000
- **Description:** Secret is zero (function is one-to-one)
- **Expected:** Correctly identifies s=0000
- **Result:** ✅ SUCCESS

### Case 2: Ideal Success
- **Input:** n=4, s=1101
- **Description:** Perfect quantum measurements with sufficient independence
- **Expected:** Recovers s=1101
- **Result:** ✅ SUCCESS

### Case 3: Failure (Dependency)
- **Input:** n=4, s=1101
- **Description:** Insufficient linearly independent measurement vectors
- **Expected:** System underdetermined, requires retry
- **Result:** ⚠️ RETRY

### Case 4: Failure (Uninformative y)
- **Input:** n=4, s=1101
- **Description:** Measures only uninformative y=0000
- **Expected:** No useful information, requires retry
- **Result:** ⚠️ RETRY

### Case 5: Realistic Success
- **Input:** n=4, s=1101
- **Description:** Redundant measurements but still recovers s
- **Expected:** Robust to redundancy, recovers s=1101
- **Result:** ✅ SUCCESS

### Case 6: Hardware Failure
- **Input:** n=4, s=1101
- **Description:** Noisy measurements simulating real quantum hardware
- **Expected:** Corruption leads to errors, requires retry
- **Result:** ⚠️ RETRY (with multiple attempts)

---

## Algorithm Overview

### Quantum Circuit Structure

```
Input qubits (n):  |0⟩ ─── H ─── [ Oracle U_f ] ─── H ─── Measure → y
Output qubits (n): |0⟩ ────────── [ Oracle U_f ] ─────────
```

### Steps

1. **Initialize:** Prepare n input qubits in |0⟩ and n output qubits in |0⟩

2. **Superposition:** Apply Hadamard gates to input qubits
   ```
   |0⟩^n → (1/√2^n) ∑_{x∈{0,1}^n} |x⟩
   ```

3. **Oracle Query:** Apply quantum oracle U_f
   ```
   |x⟩|0⟩ → |x⟩|f(x)⟩
   ```

4. **Interference:** Apply Hadamard gates again to input qubits
   - Creates interference pattern
   - Amplitudes for y where y·s ≠ 0 (mod 2) cancel out
   - Only y where y·s = 0 (mod 2) survive

5. **Measurement:** Measure input qubits to obtain vector y

6. **Repeat:** Collect n-1 linearly independent y vectors

7. **Classical Post-Processing:**
   - Form linear system: Y·s = 0 (mod 2)
   - Solve using Gaussian elimination over GF(2)
   - Recover secret s

---

## Mathematical Foundation

### The Simon Problem

Given a function **f:{0,1}^n → {0,1}^n** with the promise:

**f(x) = f(y)  ⟺  y = x ⊕ s**

for some unknown **s ∈ {0,1}^n**, find **s**.

### Quantum Measurement Property

After the quantum circuit, measuring the input register yields string **y** with the property:

**y · s = 0 (mod 2)**

where · denotes the binary dot product (XOR of bitwise AND).

### Solving the Linear System

Collecting n-1 linearly independent measurements {y₁, y₂, ..., y_{n-1}}, we form:

```
y₁ · s = 0
y₂ · s = 0
  ⋮
y_{n-1} · s = 0
```

This system over GF(2) has a 1-dimensional nullspace containing **s** (assuming s ≠ 0).

### Example for n=4, s=1101

Measurements might be:
- y₁ = 0010: (0·1) ⊕ (0·1) ⊕ (1·0) ⊕ (0·1) = 0 ✓
- y₂ = 1100: (1·1) ⊕ (1·1) ⊕ (0·0) ⊕ (0·1) = 0 ✓
- y₃ = 0111: (0·1) ⊕ (1·1) ⊕ (1·0) ⊕ (1·1) = 0 ✓

Solving this system recovers s = 1101.

---

## Expected Results

Running `python simon_qiskit.py` produces:

```
================================================================================
SIMON'S ALGORITHM - COMPREHENSIVE TEST SUITE
================================================================================

Case 1: Trivial success
Input: n=4, s=0000
Result: SUCCESS - Recovered s = 0000 ✓

Case 2: Ideal success
Input: n=4, s=1101
Result: SUCCESS - Recovered s = 1101 ✓

Case 3: Failure (dependency)
Input: n=4, s=1101
Result: FAILURE - Insufficient independent vectors (rank=1, need 3)
Status: RETRY needed

Case 4: Failure (uninformative y)
Input: n=4, s=1101
Result: FAILURE - All measurements uninformative
Status: RETRY needed

Case 5: Realistic success
Input: n=4, s=1101
Result: SUCCESS - Recovered s = 1101 ✓ (with redundancy)

Case 6: Hardware failure
Input: n=4, s=1101
Result: FAILURE - Hardware noise corrupted result
Status: RETRY needed (multiple attempts shown)

SUMMARY TABLE
Case   n    s        Description                    Expected Result
1      4    0000     Trivial success                s=0000
2      4    1101     Ideal success                  Recovers s
3      4    1101     Failure (dependency)           Retry
4      4    1101     Failure (uninformative y)      Retry
5      4    1101     Realistic success              Recovers s
6      4    1101     Hardware failure               Retry
```

---

## Project Structure

```
QISKIT/
│
├── simon_qiskit.py          # Main implementation file
├── README.md                # This file
├── .gitignore              # Git ignore rules
└── requirements.txt         # Python dependencies (optional)
```

### Code Organization

**simon_qiskit.py** contains:

- **Utility functions** (lines 14-21): Bit conversion helpers
- **Oracle builder** (lines 30-94): Constructs Simon function and quantum oracle
- **Circuit builder** (lines 99-109): Assembles Simon's quantum circuit
- **Simulator runner** (lines 114-124): Executes on Aer backend
- **Linear algebra solver** (lines 131-209): Gaussian elimination over GF(2)
- **Enhanced diagnostics** (lines 214-265): Linear independence checking
- **Noise simulation** (lines 270-284): Hardware error modeling
- **Test suite** (lines 289-454): All 6 comprehensive test cases

---

## Platform & Language

- **Language:** Python 3.8+
- **Framework:** Qiskit (IBM Quantum)
- **Execution:**
  - Qiskit Aer (statevector & qasm simulators)
  - Compatible with IBM Quantum hardware (with appropriate API setup)
- **Libraries:** NumPy for numerical operations

---

## Running on Real Quantum Hardware

To run on IBM Quantum hardware (requires IBM Quantum account):

```python
from qiskit_ibm_runtime import QiskitRuntimeService

# Save your credentials (one-time)
QiskitRuntimeService.save_account(channel="ibm_quantum", token="YOUR_TOKEN")

# Load service
service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False)

# Run circuit
job = backend.run(circ, shots=1024)
result = job.result()
counts = result.get_counts()
```

**Note:** Real hardware will exhibit noise similar to Case 6, requiring error mitigation.

---

## Key Insights

### Quantum Advantage
- **O(n) quantum queries** vs **O(2^(n/2)) classical queries**
- Exponential speedup for period-finding problems

### Probabilistic Nature
- May need multiple runs to get sufficient independent measurements
- Success probability depends on rank of measurement matrix

### Practical Challenges
1. **Linear Independence:** Need n-1 linearly independent vectors
2. **Uninformative Measurements:** y=0...0 provides no information
3. **Hardware Noise:** Real quantum computers have errors requiring mitigation
4. **Retry Logic:** Algorithm may need multiple executions

### Impact
- **Foundation for Shor's Algorithm:** Inspired quantum factoring
- **Quantum Supremacy:** One of the first demonstrations of quantum advantage
- **Cryptographic Implications:** Threatens certain classical cryptosystems

---

## References

1. **Simon, D. R.** (1994). "On the power of quantum computation". *Proceedings of the 35th Annual Symposium on Foundations of Computer Science*, pp. 116–123.

2. **Nielsen, M. A., & Chuang, I. L.** (2010). *Quantum Computation and Quantum Information*. Cambridge University Press.

3. **Qiskit Documentation** - https://qiskit.org/documentation/

4. **IBM Quantum Experience** - https://quantum-computing.ibm.com/

5. **Kaye, P., Laflamme, R., & Mosca, M.** (2007). *An Introduction to Quantum Computing*. Oxford University Press.

---

## License

This project is created for educational purposes as part of a quantum computing presentation/course.

---

## Author

**DEADSERPENT**
Quantum Computing Implementation Project
Date: 2025

---

## Acknowledgments

- IBM Quantum for the Qiskit framework
- The original Simon's algorithm paper by Daniel Simon (1994)
- Quantum computing community for educational resources

---

## Contact & Contributions

For questions, improvements, or bug reports, please open an issue or submit a pull request.

**Happy Quantum Computing! 🚀⚛️**
