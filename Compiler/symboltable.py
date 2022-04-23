class SymbolTable:

    def __init__(self):
        self.class_st = {}
        self.function_st = {}
        self.varCounts = {"static": 0, "field": 0, "argument": 0, "var": 0}

    def startSubroutine(self):
        self.function_st = {}
        self.varCounts["argument"] = 0
        self.varCounts["var"] = 0

    def define(self, name, type, kind):
        # Declare a new variable in this scope
        number_of_kind = self.varCounts[kind]
        record = [type, kind, number_of_kind]
        if kind in ("static", "field"):
            assert(self.class_st.get(name) is None)
            self.class_st[name] = record
        elif kind in ("argument", "var"):
            assert(self.function_st.get(name) is None)
            self.function_st[name] = record
        self.varCounts[kind] += 1

    def varCount(self, kind):
        # Get count of number of variables of this kind in this scope
        return self.varCounts[kind]

    def _getRecord(self, name):
        record = self.function_st.get(name)
        if record is None:
            record = self.class_st.get(name)
        assert(record is not None)
        return record

    def kindOf(self, name):
        record = self._getRecord(name)
        return record[1]

    def typeOf(self, name):
        record = self._getRecord(name)
        return record[0]

    def indexOf(self, name):
        record = self._getRecord(name)
        return record[2]

