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
#
# Each function below is defined using only the five primitives above.
# ===========================================================================

# Addition: add(a, b) = a + b
# Base case: add(0, b) = b
# Step: add(a+1, b) = succ(add(a, b))
add = prim_rec(
    proj(0),  # base: identity on b
    compose(succ, proj(1))  # step: increment the accumulator
)

# Multiplication: mult(a, b) = a * b
# Base case: mult(0, b) = 0
# Step: mult(a+1, b) = add(mult(a, b), b)
mult = prim_rec(
    compose(zero),  # base: constant 0 (ignores b)
    compose(add, proj(1), proj(2))  # step: add b to accumulator
)

# Predecessor: pred(n) = max(0, n-1)
# This is a bit subtle. We recurse with no extra arguments:
# Base case: pred(0) = 0
# Step: pred(k+1) = k  (we return the iteration counter, not the accumulator)
pred = prim_rec(
    zero,  # base: 0
    proj(0)  # step: just return k
)

# Monus (truncated subtraction): monus(a, b) = max(0, a - b)
# We want to subtract b from a, but prim_rec recurses on the first argument.
# So we define a helper h(b, a) = max(0, a - b) and then swap arguments.
# Base case: h(0, a) = a
# Step: h(b+1, a) = pred(h(b, a))
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
# Base case: fact(0) = 1
# Step: fact(k+1) = (k+1) * fact(k)
_one = compose(succ, zero)  # the constant 1

factorial = prim_rec(
    _one,
    compose(mult, compose(succ, proj(0)), proj(1))  # (k+1) * acc
)


# Bounded minimization (bounded μ-operator)
# bmin(p, n) returns the smallest k < n where p(k) = 1, or n if none exists.
#
# This is primitive recursive because the search is bounded. The unbounded
# version (μ-operator) would take us outside PRF into general recursion.
#
# Pure PRF construction would use prim_rec with a pair encoding (found, index),
# but a direct implementation is clearer.

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
# Interactive REPL
# ===========================================================================

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
    }


def repl():
    """
    Run an interactive session.

    Enter expressions like add(3, mult(2, 2)) to evaluate them.
    Type 'quit' or Ctrl-D to exit.
    """
    ns = make_namespace()

    print("Primitive Recursive Functions")
    print("Primitives: zero, succ, proj, compose, prim_rec")
    print("Derived: add, mult, pred, monus, factorial, bmin")
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
    """Sanity checks for the derived functions."""
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
    assert pred(0) == 0  # by convention
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
    assert bmin(is_five, 10) == 5  # finds 5
    assert bmin(is_five, 3) == 3  # 5 not in range, returns bound
    always_false = lambda k: 0
    assert bmin(always_false, 10) == 10
    is_even = lambda k: 1 if k % 2 == 0 else 0
    assert bmin(is_even, 10) == 0  # 0 is first even
    is_odd = lambda k: 1 if k % 2 == 1 else 0
    assert bmin(is_odd, 10) == 1  # 1 is first odd

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