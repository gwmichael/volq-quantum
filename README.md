![Volq](docs/banner.png)

<h1 align="center">
  <br>
  WELCOME
</h1>

Volq is a programming language that enables you to simulate quantum computing algorithms on your computer. You can play around with existing algorithms to better understand how they solve problems, or write your own from scratch using the easy to learn DSL based on the quantum circuit model.

This project is 100% coded in Python with NumPy.

> Important note: This project does not aim to solve classically difficult problems at quantum running times on a classical computer. Instead, it aims to prove mathematically that quantum algorithms do indeed find correct solutions through quantum mechanics (i.e. lots of linear algebra!).
## Current Features of v0.2.0-alpha
- Functional quantum circuit model backend with probabilistic measurement and single qubit gates, including:
  - Identity (**I**) - No effect on the qubit
  - Hadamard (**H**) - Transforms a qubit into & out of superposition
  - Pauli X (**X**) - Flips a qubit state
  - Pauli Y (**Y**) - Flips a qubit state and applies a phase flip & rotation into the complex plane
  - Pauli Z (**Z**) - Flips the phase of a qubit in the |1> state
- Multi Qubit Gates
  - Two-qubit gates, such as CNOT gates
  - Three-qubit gates, such as Toffoli (CCNOT) gates
  - General n-qubit controlled gates, which can be generated from scratch and apply any single qubit gate for any n control bits in any order
- Domain Specific Language (DSL) for generating unitary matrix operators from string inputs
- Easy-to-read string representation of the quantum circuit state
- Support for running on the CPU or GPU
- Thorough unit testing, to rigorously prove the validity and correctness of the framework
## Planned Features
- Frontend interpreter for running code
- SWAP and Fredkin (CSWAP) gate generation
- Partial measurement
- Oracles and Phase Oracles, with predefined functions and support for user-defined functions
- Quantum Fourier Transforms
- Simulations of several quantum algorithms for solving different problems
	- Deutsch's Algorithm
	- Deutsch-Jozsa Algorithm
	- Bernstein-Vazirani Algorithm
	- Simon's Algorithm
	- Grover's Algorithm
	- Shor's Algorithm
- Optimisations to speed up simulation of circuits
- Extensive documentation on the quantum circuit model and adjacent algorithms

