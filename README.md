![Volq](docs/banner.png)

<h1>
  <br>
  WELCOME
</h1>

Volq is a programming language that enables you to simulate quantum computing algorithms on your computer. You can play around with existing algorithms to better understand how they solve problems, or write your own from scratch using the easy-to-learn DSL based on the quantum circuit model.

This project is 100% coded in Python with NumPy.

> Important note: This project does not aim to solve classically difficult problems at quantum running times on a classical computer. Instead, it aims to prove mathematically that quantum algorithms do indeed find correct solutions through quantum mechanics (i.e. lots of linear algebra!).

This project is currently in the **alpha** stage. The DSL syntax and backend API **will** change over time.
## Getting Started
To start running Volq code on your system, follow these steps to setup your environment.
### 1. Python installation
Volq requires Python to run. You can check this is installed by making sure you can run this in your terminal:
```bash
python3 --version
```
### 2. Clone git repository
```bash
git clone https://github.com/michaelchips/volq-quantum.git
cd volq-quantum
```
### 3. Recommended: Create a virtual environment
Creating a virtual environment is optional but recommended, especially if your OS runs a managed Python environment.
```bash
python3 -m venv .venv
# If you're on Linux, use
source .venv/bin/activate
# If you're on Windows, use
.venv\Scripts\activate 
```
### 4. Install dependencies
```bash
pip install -r requirements.txt
```
## Running Volq
Once you've installed dependencies, you can start running Volq programs with the interpreter using:
```bash
python3 -m volq.frontend.interpreter YOURPROGRAMFILENAMEHERE
```
You can execute all of Volq's testing code with:
```bash
python3 -m unittest volq.test
```
You can also check how well Volq adheres to Google's Python code standard using:
```
python3 -m pylint volq
```
## Example Program in Volq
Below is an example Volq program, which runs the Deutsch-Jozsa algorithm on a 9 qubit circuit, using a balanced function with an 8-bit domain as input.
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

In the output space below, we can see that P(|00000000⟩⊗|ψ⟩) = 0, where |ψ⟩ is the ancilla, indicating that this function is indeed balanced. 
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
- Support for running on Nvidia and AMD GPUs
- Extensive documentation on the quantum circuit model and adjacent algorithms

