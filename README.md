![Volq](docs/banner.png)

<h1>
  <br>
  WELCOME
</h1>

Volq is a programming language that enables you to simulate quantum computing algorithms on your computer. You can play around with existing algorithms to better understand how they solve problems, or write your own from scratch using the easy-to-learn DSL based on the quantum circuit model.

This project is 100% coded in Python with NumPy.

> Important note: This project does not aim to solve classically difficult problems at quantum running times on a classical computer. Instead, it aims to prove mathematically that quantum algorithms do indeed find correct solutions through quantum mechanics (i.e. lots of linear algebra!).

This project is currently in the **alpha** stage. The DSL syntax and backend API will change over time.
## Getting Started
Volq requires Python and NumPy to run. You can check these are installed with the following:
```bash
python3 --version
python3 -m pip show numpy
```
Next, clone this Git repository using the command below:
```bash
git clone https://github.com/michaelchips/volq-quantum.git
```
Change directory into the cloned repository folder, then you can start running Volq programs with the interpreter using:
```bash
python3 -m volq.frontend.interpreter YOURPROGRAMFILENAMEHERE
```
You can also execute all of Volq's testing code with:
```bash
python3 -m unittest volq.test
```
## Example Program
Below is an example program, which runs the Deutsch-Jozsa algorithm on a 9 qubit circuit, using a balanced function with an 8-bit domain as input.
```
QUBITS 9
RUNS 1000
INIT

APPLY X8
APPLY H0 H1 H2 H3 H4 H5 H6 H7 H8
APPLY CNOT8,0
APPLY CNOT8,1
APPLY CNOT8,2
APPLY CNOT8,3
APPLY CNOT8,4
APPLY CNOT8,5
APPLY CNOT8,6
APPLY CNOT8,7
APPLY H0 H1 H2 H3 H4 H5 H6 H7
MEASURE ALL
```
We only need to pay attention to the first 8 qubits of the output, as the 9th qubit is the ancilla qubit of the oracle and can be discarded.

This gives us the output below, indicating that we used a balanced function, since P(|00000000⟩⊗|ψ⟩) = 0, where |ψ⟩ is the ancilla. 
```
>> Volq-quantum v0.4.0-alpha
>> Author: michaelchips / Michael Goodwin
{'|111111111⟩': 524, '|111111110⟩': 476}
```
## Current Features of v0.4.0-alpha
- Functional quantum circuit model backend with probabilistic measurement and single qubit gates, including:
  - Identity (**I**) - No effect on the qubit
  - Hadamard (**H**) - Transforms a qubit into & out of superposition
  - Pauli X (**X**) - Flips a qubit state
  - Pauli Y (**Y**) - Flips a qubit state and applies a phase flip & rotation into the complex plane
  - Pauli Z (**Z**) - Flips the phase of a qubit in the |1⟩ state
- Multi-qubit gates
  - Two-qubit gates, such as CNOT gates
  - Three-qubit gates, such as Toffoli (CCNOT) gates
  - General n-qubit controlled gates, which can be generated from scratch and apply any single qubit gate for any n control bits in any order
- Domain Specific Language (DSL) with an interpreter and runtime, for generating unitary matrix operators from string inputs
- Easy-to-read string representation of the quantum circuit state
- Support for running on the CPU or GPU
- Thorough unit testing, to rigorously prove the validity and correctness of the framework

## Planned Features
This list is not exhaustive, nor are any features below guaranteed:
- SWAP and Fredkin (CSWAP) gate generation
- Integration with Matplotlib for generating histograms of the resulting probability distribution
- Partial measurement
- Oracle and Phase Oracle parsing and compiling, with predefined functions and support for user-defined functions
- Quantum Fourier Transforms
- Simulations of several quantum algorithms for solving different problems
	- Deutsch's Algorithm
	- Deutsch-Jozsa Algorithm
	- Bernstein-Vazirani Algorithm
	- Simon's Algorithm
	- Grover's Algorithm
	- Shor's Algorithm
- Compiler and runtime optimisations to speed up simulation of large-scale circuits
- Extensive documentation on the quantum circuit model and adjacent algorithms