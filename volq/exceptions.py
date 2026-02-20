# Raised when syntax is spelled incorrectly and cannot be parsed
class VolqSyntaxError(Exception):
    pass

# Raised when an invalid number of qubits is given to initialise a circuit
class VolqQubitsError(Exception):
    pass