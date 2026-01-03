class Context:

    def __init__(
            self,
            qubits,
            operator_cache,
            hardware_mode,
            syntax_validation
        ):
        
        self._qubits = qubits # Qubits has no setter by design
        self._operator_cache_enabled = operator_cache
        self._operator_cache = {}
        self._hardware_mode = hardware_mode
        self._syntax_validation_enabled = syntax_validation


    def get_qubits(self):
        return self._qubits
    

    def operator_cache_enabled(self):
        return self._operator_cache_enabled


    def toggle_operator_cache(self):
        self._operator_cache_enabled = not self._operator_cache_enabled


    def is_operator_cached(self, operator):
        return True if operator in self._operator_cache else False
    

    def hardware_mode(self):
        return self._hardware_mode
    

    def syntax_validation_enabled(self):
        return self._syntax_validation_enabled
