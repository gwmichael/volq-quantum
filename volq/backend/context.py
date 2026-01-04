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

        # WARNING: This option is intended for testing new syntax before
        #          validation is implemented.
        #          Disabling this creates a risk of infinite loops or crashes!
        self._syntax_validation_enabled = syntax_validation


    def get_qubits(self):
        return self._qubits


    def operator_cache_enabled(self):
        return self._operator_cache_enabled


    def toggle_operator_cache(self):
        self._operator_cache_enabled = not self._operator_cache_enabled


    def add_operator_to_cache(self, normalised_key, U):
        if self._operator_cache_enabled:
            self._operator_cache[normalised_key] = U


    def load_cached_operator(self, key):
        if (self._operator_cache_enabled == False):
            return None
        else:
            return self._operator_cache[key] if key in \
                self._operator_cache else None


    def hardware_mode(self):
        return self._hardware_mode


    def syntax_validation_enabled(self):
        return self._syntax_validation_enabled
