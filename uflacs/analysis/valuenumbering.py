
from six.moves import xrange as range
from ufl.algorithms import MultiFunction
from uflacs.analysis.indexing import map_indexed_arg_components, map_component_tensor_arg_components

class ValueNumberer(MultiFunction):
    """An algorithm to map the scalar components of an expression node to unique value numbers,
    with fallthrough for types that can be mapped to the value numbers of their operands."""
    def __init__(self, e2i, V_sizes, V_symbols):
        MultiFunction.__init__(self)
        self.symbol_count = 0
        self.e2i = e2i
        self.V_sizes = V_sizes
        self.V_symbols = V_symbols

    def new_symbols(self, n):
        "Generator for new symbols with a running counter."
        begin = self.symbol_count
        end = begin + n
        self.symbol_count = end
        return list(range(begin, end))

    def get_node_symbols(self, expr):
        return self.V_symbols[self.e2i[expr]]

    def expr(self, v, i):
        "Create new symbols for expressions that represent new values."
        n = self.V_sizes[i]
        return self.new_symbols(n)

    def form_argument(self, v, i):
        "Create new symbols for expressions that represent new values."
        symmetry = v.element().symmetry()

        if False and symmetry:
            # FIXME: Ignoring symmetries for now, handle by creating only
            # some new symbols and mapping the rest using the symmetry map.
            actual_components = sorted(set(symmetry.values()))
            m = len(actual_components)
            actual_symbols = self.new_symbols(m)
            symbols = mapping_of_actual_symbols_to_all_components(actual_symbols, symmetry) # Need to implement this

        else:
            n = self.V_sizes[i]
            symbols = self.new_symbols(n)

        return symbols

    def indexed(self, Aii, i):
        # Reuse symbols of arg A for Aii
        A = Aii.operands()[0]

        # Get symbols of argument A
        A_symbols = self.get_node_symbols(A)

        # Map A_symbols to Aii_symbols
        d = map_indexed_arg_components(Aii)
        symbols = [A_symbols[k] for k in d]
        return symbols

    def component_tensor(self, A, i):
        # Reuse symbols of arg Aii for A
        Aii = A.operands()[0]

        # Get symbols of argument Aii
        Aii_symbols = self.get_node_symbols(Aii)

        # Map A_symbols to Aii_symbols
        d = map_component_tensor_arg_components(A)
        symbols = [Aii_symbols[k] for k in d]
        return symbols

    def list_tensor(self, v, i):
        row_symbols = [self.get_node_symbols(row) for row in v.operands()]
        symbols = []
        for rowsymb in row_symbols:
            symbols.extend(rowsymb) # FIXME: Test that this produces the right transposition
        return symbols

    def transposed(self, AT, i):
        A, = AT.operands()

        assert not A.free_indices(), "Assuming no free indices in transposed (for now), report as bug if needed." # FIXME
        r, c = A.shape()

        A_symbols = self.get_node_symbols(A)
        assert len(A_symbols) == r*c

        # AT[j,i] = A[i,j]
        # sh(A) = (r,c)
        # sh(AT) = (c,r)
        # AT[j*r+i] = A[i*c+j]
        symbols = [None]*(r*c)
        for j in range(c):
            for i in range(r):
                symbols[j*r+i] = A_symbols[i*c+j]
        return symbols

    def variable(self, v, i):
        "Direct reuse of all symbols."
        return self.get_node_symbols(v.operands()[0])
