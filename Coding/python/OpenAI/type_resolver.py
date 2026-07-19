"""A tiny generic type system: bind type variables from a call's arguments.

Overview:
  Types are modeled as small tree-shaped objects. Given a function's
  declared parameter types (which may contain generic placeholders) and
  the concrete types of an actual call, we "unify" them position by
  position to learn what each generic stands for, then substitute those
  learnings into the declared return type to get the concrete result type.

Interface:
  - Primitive(name) -> a concrete named type (int, str, bool, ...).
  - Generic(name) -> a type variable; by convention its name starts with
    an uppercase letter (T, K, V, X).
  - TupleType(elements) -> an ordered list of element types.
  - FunctionType(params, output) -> a signature: a list of parameter types
    plus one output type.
  - Every type has render() -> str: a Primitive/Generic renders to its
    name, a TupleType to "[a, b]", a FunctionType to "[p1, p2] -> out".
  - parse(spec) -> a type: a list becomes a TupleType (recursively); a
    string whose first character is uppercase becomes a Generic, otherwise
    a Primitive.
  - resolve_return(function, args) -> the substituted return type, a type
    object whose render() gives the concrete result (e.g. "[bool, str]").

Semantics and rules:
  - Matching (unification) is structural: a Primitive must meet the same
    Primitive; a TupleType must meet a TupleType of equal length, matched
    element by element.
  - A Generic binds to whatever concrete type sits opposite it the first
    time it is seen; meeting a different type later is a conflict.
  - Substitution copies the return type and swaps each bound generic for
    its learned type; unbound generics are left as-is.

Errors (all raise ResolutionError):
  - the argument count does not match the parameter count;
  - a primitive or tuple shape does not line up;
  - one generic is forced to two different concrete types.

Example:
  sig = [[K, int], V, K] -> [V, K]; call with [[str, int], bool, str]
  resolve_return(sig, args).render() -> "[bool, str]"
"""


class ResolutionError(Exception):
    """Raised when a generic function call cannot be resolved."""


class Primitive:
    """A primitive type such as int or str."""

    def __init__(self, name):
        # Time: O(1), Space: O(1).
        self.name = name

    def render(self):
        # Time: O(1), Space: O(1).
        return self.name


class Generic:
    """A generic type variable such as T or K."""

    def __init__(self, name):
        # Time: O(1), Space: O(1).
        self.name = name

    def render(self):
        # Time: O(1), Space: O(1).
        return self.name


class TupleType:
    """A tuple type: an ordered list of element types."""

    def __init__(self, elements):
        # Time: O(1), Space: O(1) - keeps a reference to the element list.
        self.elements = elements

    def render(self):
        # Time: O(size of the type tree). Space: O(same) - the string.
        parts = []
        for element in self.elements:
            parts.append(element.render())
        return "[" + ", ".join(parts) + "]"


class FunctionType:
    """A function signature: parameter types plus one output type."""

    def __init__(self, params, output):
        # Time: O(1), Space: O(1).
        self.params = params
        self.output = output

    def render(self):
        # Time: O(size of the type tree). Space: O(same) - the string.
        parts = []
        for param in self.params:
            parts.append(param.render())
        return "[" + ", ".join(parts) + "] -> " + self.output.render()


def parse(spec):
    """Build a type from a nested spec: a list -> TupleType, an uppercase-first
    string -> Generic, any other string -> Primitive."""
    # Time: O(size of spec). Space: O(size of spec) - the built type.
    if isinstance(spec, list):
        elements = []
        for item in spec:
            elements.append(parse(item))
        return TupleType(elements)
    if spec[:1].isupper():
        return Generic(spec)
    return Primitive(spec)


def _same_type(left, right):
    """True if two types have identical structure."""
    # Time: O(size). Space: O(depth) - the recursion.
    if isinstance(left, Primitive) and isinstance(right, Primitive):
        return left.name == right.name
    if isinstance(left, Generic) and isinstance(right, Generic):
        return left.name == right.name
    if isinstance(left, TupleType) and isinstance(right, TupleType):
        if len(left.elements) != len(right.elements):
            return False
        for i in range(len(left.elements)):
            if not _same_type(left.elements[i], right.elements[i]):
                return False
        return True
    if isinstance(left, FunctionType) and isinstance(right, FunctionType):
        if len(left.params) != len(right.params):
            return False
        for i in range(len(left.params)):
            if not _same_type(left.params[i], right.params[i]):
                return False
        return _same_type(left.output, right.output)
    return False


def _unify(declared, concrete, mapping):
    """Match a declared type against a concrete one, recording generic ->
    concrete bindings in mapping. Raises ResolutionError on any mismatch."""
    # Time: O(size). Space: O(depth) - the recursion.
    if isinstance(declared, Generic):
        bound = mapping.get(declared.name)
        if bound is None:
            mapping[declared.name] = concrete
        elif not _same_type(bound, concrete):
            raise ResolutionError(f"conflicting types for {declared.name}")
        return
    if isinstance(declared, Primitive):
        if (not isinstance(concrete, Primitive)
                or concrete.name != declared.name):
            raise ResolutionError("primitive/type-shape mismatch")
        return
    if isinstance(declared, TupleType):
        if (not isinstance(concrete, TupleType)
                or len(concrete.elements) != len(declared.elements)):
            raise ResolutionError("tuple structure mismatch")
        for i in range(len(declared.elements)):
            _unify(declared.elements[i], concrete.elements[i], mapping)
        return
    raise ResolutionError("cannot match this type form")


def _substitute(declared, mapping):
    """Replace every bound generic in declared with its concrete type."""
    # Time: O(size). Space: O(depth) - the recursion.
    if isinstance(declared, Generic):
        bound = mapping.get(declared.name)
        return bound if bound is not None else declared
    if isinstance(declared, Primitive):
        return declared
    if isinstance(declared, TupleType):
        new_elements = []
        for element in declared.elements:
            new_elements.append(_substitute(element, mapping))
        return TupleType(new_elements)
    if isinstance(declared, FunctionType):
        new_params = []
        for param in declared.params:
            new_params.append(_substitute(param, mapping))
        return FunctionType(new_params, _substitute(declared.output, mapping))
    return declared


# Approach (in plain terms):
#   Think of each type as a little tree: a leaf is a primitive (int) or a
#   generic placeholder (T), and a branch is a tuple/function holding more
#   types. To resolve a call we walk the declared parameter tree and the
#   concrete argument tree together, position by position. A primitive must
#   match the same primitive; a tuple must match a tuple of the same shape; a
#   generic "learns" whatever concrete type sits opposite it - and if it later
#   meets a different type, that is a conflict and we reject the call. Once
#   every generic knows its type, we copy the declared return tree and swap
#   each generic for what it learned.
#   Data structures used:
#     - small classes (Primitive/Generic/TupleType/FunctionType) - a tagged
#       tree representing each type form.
#     - dict generic name -> concrete type - the bindings learned while
#       matching; a repeat with a different type means a conflict.
#     - recursion - matches and substitutes the nested type trees.
def resolve_return(function, args):
    """Concrete return type of function when called with args. Binds each
    generic by matching declared params to concrete args, then fills those
    bindings into the return type. Raises ResolutionError on invalid calls."""
    # s = total size of the types involved.
    # Time: O(s) - one recursive match, then one recursive substitution.
    # Space: O(number of generics + recursion depth).
    if len(args) != len(function.params):
        raise ResolutionError("wrong number of arguments")
    mapping = {}
    for i in range(len(function.params)):
        _unify(function.params[i], args[i], mapping)
    return _substitute(function.output, mapping)


if __name__ == "__main__":
    # Example 1: [[K, int], V, K] -> [V, K] with args [[str, int], bool, str]
    signature = FunctionType(
        [parse(["K", "int"]), parse("V"), parse("K")],
        parse(["V", "K"]),
    )
    print(signature.render())     # [[K, int], V, K] -> [V, K]
    call_args = [parse(["str", "int"]), parse("bool"), parse("str")]
    print(resolve_return(signature, call_args).render())   # [bool, str]

    # Example 2: [X, [X, bool]] -> X with [int, [str, bool]] -> conflict
    conflicting = FunctionType(
        [parse("X"), parse(["X", "bool"])], parse("X"))
    try:
        resolve_return(conflicting, [parse("int"), parse(["str", "bool"])])
    except ResolutionError as err:
        print("error:", err)      # error: conflicting types for X

    # Wrong number of arguments -> rejected
    try:
        resolve_return(conflicting, [parse("int")])
    except ResolutionError as err:
        print("error:", err)      # error: wrong number of arguments

    # Primitive mismatch -> rejected
    identity = FunctionType([parse("int")], parse("int"))
    try:
        resolve_return(identity, [parse("str")])
    except ResolutionError as err:
        print("error:", err)      # error: primitive/type-shape mismatch
