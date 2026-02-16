#!/usr/bin/env python3
class Zero:
    """The constant zero function: Z() = 0"""

    def __call__(self):
        return 0

    def __repr__(self):
        return "zero"


class Succ:
    """The successor function: S(n) = n + 1"""

    def __call__(self, n):
        return n + 1

    def __repr__(self):
        return "succ"


class Proj:
    """
    Projection function: P^n_i extracts the i-th component (0-indexed).
    For example, proj(1)(a, b, c) returns b.
    """

    def __init__(self, index):
        self.index = index

    def __call__(self, *args):
        if self.index >= len(args):
            raise IndexError(
                f"projection index {self.index} out of range for {len(args)} arguments"
            )
        return args[self.index]

    def __repr__(self):
        return f"proj({self.index})"


# singletons for the nullary/unary base functions
zero = Zero()
succ = Succ()


def proj(i):
    """Construct a projection function for index i."""
    return Proj(i)


class Compose:
    """
    Composition: given f and g_1,...,g_m, produces h where
    h(x_1,...,x_n) = f(g_1(x_1,...,x_n), ..., g_m(x_1,...,x_n)).
    compose(f) with no g's calls f() -- useful for lifting constants.
    """

    def __init__(self, f, *gs):
        self.f = f
        self.gs = gs

    def __call__(self, *args):
        if len(self.gs) == 0:
            return self.f()
        inner_results = [g(*args) for g in self.gs]
        return self.f(*inner_results)

    def __repr__(self):
        if self.gs:
            inner = ", ".join(repr(g) for g in self.gs)
            return f"compose({self.f!r}, {inner})"
        return f"compose({self.f!r})"


class PrimRec:
    """
    Primitive recursion: given base f and step g, produces h where
        h(0, xs)   = f(xs)
        h(k+1, xs) = g(k, h(k, xs), xs)
    Uses iteration internally to avoid Python's stack limit.
    """

    def __init__(self, base, step):
        self.base = base
        self.step = step

    def __call__(self, n, *xs):
        acc = self.base(*xs)
        for k in range(n):
            acc = self.step(k, acc, *xs)
        return acc

    def __repr__(self):
        return f"prim_rec({self.base!r}, {self.step!r})"


def compose(f, *gs):
    return Compose(f, *gs)


def prim_rec(base, step):
    return PrimRec(base, step)


# ===========================================================================
# Derived functions
# ===========================================================================

# Addition: add(a, b) = a + b
add = prim_rec(
    proj(0),  # base: identity on b
    compose(succ, proj(1))  # step: increment the accumulator
)

# Multiplication: mult(a, b) = a * b
mult = prim_rec(
    compose(zero),  # base: constant 0 (ignores b)
    compose(add, proj(1), proj(2))  # step: add b to accumulator
)

# Predecessor: pred(n) = max(0, n-1)
pred = prim_rec(
    zero,  # base: 0
    proj(0)  # step: just return k
)

# Monus (truncated subtraction): monus(a, b) = max(0, a - b)
_monus_helper = prim_rec(
    proj(0),  # base: return a
    compose(pred, proj(1))  # step: decrement accumulator
)


class Monus:
    """Truncated subtraction: monus(a, b) = max(0, a - b)"""

    def __call__(self, a, b):
        return _monus_helper(b, a)

    def __repr__(self):
        return "monus"


monus = Monus()

# Factorial: fact(n) = n!
_one = compose(succ, zero)  # the constant 1

factorial = prim_rec(
    _one,
    compose(mult, compose(succ, proj(0)), proj(1))  # (k+1) * acc
)


# Bounded minimization (bounded μ-operator)
class BoundedMin:
    """
    Bounded minimization: bmin(p, n) finds least k < n with p(k) = 1.
    Returns n if no such k exists.
    """

    def __call__(self, p, n):
        for k in range(n):
            if p(k) == 1:
                return k
        return n

    def __repr__(self):
        return "bmin"


bmin = BoundedMin()


# ===========================================================================
# Presburger Extension Explorer
# ===========================================================================

class PresburgerExtension:
    """
    Represents the theory Th(ℕ; +, <, A) where A is a predicate
    defined by a primitive recursive function.
    Use this to explore whether adding A might let you define multiplication.
    """

    def __init__(self, name, predicate_prf):
        self.name = name
        self.predicate = predicate_prf

    def __call__(self, n):
        return self.predicate(n)

    def __repr__(self):
        return f"PresburgerExtension({self.name!r}, {self.predicate!r})"

    def describe(self):
        print(f"Theory: Th(ℕ; +, <, {self.name})")
        print(f"Predicate defined by: {self.predicate!r}")

    def check_multiplication_heuristic(self, max_samples=20):
        """
        Simple heuristic: print first few values and note if the predicate
        looks like it could directly encode multiplication. This is not a proof.
        """
        print(f"\nHeuristic check for {self.name} (samples 0..{max_samples-1}):")
        samples = [self(i) for i in range(max_samples)]
        print("  values:", samples)

        if all(v == 0 for v in samples):
            print("  → always false; likely too weak.")
            return False
        if all(v == 1 for v in samples):
            print("  → always true; likely too weak.")
            return False

        print("  → No obvious direct definition of multiplication.")
        print("    (This does not guarantee decidability.)")
        return False


def make_namespace():
    """Build the evaluation namespace for the REPL."""
    return {
        "zero": zero,
        "succ": succ,
        "proj": proj,
        "compose": compose,
        "prim_rec": prim_rec,
        "add": add,
        "mult": mult,
        "pred": pred,
        "monus": monus,
        "factorial": factorial,
        "bmin": bmin,
        "PresburgerExtension": PresburgerExtension,
    }


# ===========================================================================
# Interactive REPL
# ===========================================================================

def repl():
    ns = make_namespace()

    print("Primitive Recursive Functions")
    print("Primitives: zero, succ, proj, compose, prim_rec")
    print("Derived: add, mult, pred, monus, factorial, bmin")
    print("New: PresburgerExtension(name, predicate)")
    print("Type 'quit' to exit, 'help' for examples.")
    print()

    while True:
        try:
            line = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue
        if line in ("quit", "exit", "q"):
            break
        if line == "help":
            print("  add(3, 4)        => 7")
            print("  mult(6, 7)       => 42")
            print("  factorial(5)     => 120")
            print("  monus(10, 3)     => 7")
            print("  add(3,mult(2,2)) => 7")
            print("  # New example:")
            print("  square = PresburgerExtension('is_square', lambda n: 1 if int(n**0.5)**2 == n else 0)")
            print("  square.check_multiplication_heuristic()")
            continue

        try:
            result = eval(line, {"__builtins__": {}}, ns)
            if callable(result) and not isinstance(result, int):
                print(f"[function: {result!r}]")
            else:
                print(result)
        except Exception as err:
            print(f"error: {err}")


# ===========================================================================
# Tests
# ===========================================================================

def run_tests():
    # base functions
    assert zero() == 0
    assert succ(0) == 1
    assert succ(99) == 100
    assert proj(0)(10, 20) == 10
    assert proj(1)(10, 20) == 20

    # addition
    assert add(0, 0) == 0
    assert add(0, 5) == 5
    assert add(3, 4) == 7
    assert add(17, 25) == 42

    # multiplication
    assert mult(0, 5) == 0
    assert mult(5, 0) == 0
    assert mult(6, 7) == 42
    assert mult(12, 12) == 144

    # predecessor
    assert pred(0) == 0
    assert pred(1) == 0
    assert pred(10) == 9

    # monus
    assert monus(5, 3) == 2
    assert monus(3, 5) == 0
    assert monus(10, 0) == 10

    # factorial
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120
    assert factorial(7) == 5040

    # bounded minimization
    is_five = lambda k: 1 if k == 5 else 0
    assert bmin(is_five, 10) == 5
    assert bmin(is_five, 3) == 3
    always_false = lambda k: 0
    assert bmin(always_false, 10) == 10
    is_even = lambda k: 1 if k % 2 == 0 else 0
    assert bmin(is_even, 10) == 0
    is_odd = lambda k: 1 if k % 2 == 1 else 0
    assert bmin(is_odd, 10) == 1

    # composition example
    double = compose(add, proj(0), proj(0))
    assert double(7) == 14

    # nested expressions
    assert add(3, mult(2, 2)) == 7
    assert factorial(add(2, 3)) == 120

    print("tests passed")


if __name__ == "__main__":
    import sys

    if "--test" in sys.argv:
        run_tests()
    elif "--repl" in sys.argv:
        repl()
    else:
        run_tests()
        print()
        repl()