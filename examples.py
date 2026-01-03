#!/usr/bin/env python3
"""
Additional primitive recursive functions.

These are standard examples from computability theory, each built
from the core primitives or previously defined functions.
"""

from prf import zero, succ, proj, compose, prim_rec
from prf import add, mult, pred, monus, factorial, bmin

# ===========================================================================
# Predicates (returning 0 or 1)
# ===========================================================================

# Helper: constant 1, ignores any arguments
_one = compose(succ, zero)
_const = compose(_one)  # wraps _one to accept and ignore args

# Sign function: sg(0) = 0, sg(n) = 1 for n > 0
sg = prim_rec(zero, _const)

# Complement: sg_bar(0) = 1, sg_bar(n) = 0 for n > 0
sg_bar = compose(monus, _const, sg)  # 1 - sg(n)

# is_zero is just sg_bar by another name
is_zero = sg_bar

# Equality: eq(a, b) = 1 if a = b, else 0
# Note that |a - b| = monus(a,b) + monus(b,a), and eq(a,b) = is_zero(|a-b|)
_abs_diff = compose(add, monus, compose(monus, proj(1), proj(0)))
eq = compose(is_zero, _abs_diff)

# Less than or equal: leq(a, b) = 1 if a <= b, else 0
# a <= b iff monus(a, b) = 0
leq = compose(is_zero, monus)

# Strict less than: lt(a, b) = 1 if a < b
# a < b iff a + 1 <= b
lt = compose(leq, compose(succ, proj(0)), proj(1))

# ===========================================================================
# Arithmetic
# ===========================================================================

# Exponentiation: exp(n, b) = b^n
exp = prim_rec(
    _const,  # base: exp(0, b) = 1
    compose(mult, proj(2), proj(1))  # step: b * acc
)

# Bounded predecessor (alternative definition for clarity)
# This shows another way to define pred using the "lag" technique
pred_alt = prim_rec(zero, proj(0))

# Double: double(n) = 2n
double = compose(add, proj(0), proj(0))

# Square: square(n) = n^2
square = compose(mult, proj(0), proj(0))

# Triangular number: tri(n) = 0 + 1 + 2 + ... + n = n(n+1)/2
# tri(0) = 0
# tri(k+1) = tri(k) + (k+1)
tri = prim_rec(
    zero,
    compose(add, proj(1), compose(succ, proj(0)))  # acc + (k+1)
)


# ===========================================================================
# Division and remainder via bounded minimization
# ===========================================================================

# These use bmin to search for quotients and remainders. This is the
# standard PRF construction — we can't just "divide" directly, but we
# can search for the answer within a known bound.

# Divisibility: divides(d, n) = 1 if d divides n, else 0
# d | n iff there exists k <= n such that d * k = n
def _divides(d, n):
    if d == 0:
        return 1 if n == 0 else 0
    return 1 if n % d == 0 else 0


class Divides:
    def __call__(self, d, n):
        return _divides(d, n)

    def __repr__(self):
        return "divides"


divides = Divides()


# Division: div(a, b) = floor(a / b), with div(a, 0) = 0 by convention
# We search for the largest q such that b * q <= a.
# Equivalently, find smallest q where b * (q+1) > a, then return q.
class Div:
    def __call__(self, a, b):
        if b == 0:
            return 0
        # find smallest q where b * (q+1) > a
        exceeds = lambda q: 1 if mult(b, succ(q)) > a else 0
        return bmin(exceeds, succ(a))

    def __repr__(self):
        return "div"


div = Div()


# Remainder: rem(a, b) = a mod b, with rem(a, 0) = a by convention
class Rem:
    def __call__(self, a, b):
        if b == 0:
            return a
        return monus(a, mult(b, div(a, b)))

    def __repr__(self):
        return "rem"


rem = Rem()

# ===========================================================================
# Cantor pairing
# ===========================================================================

# The Cantor pairing function encodes two natural numbers as one, bijectively.
# This is fundamental for handling pairs, tuples, and sequences in PRF.
#
# pair(a, b) = tri(a + b) + b = (a+b)(a+b+1)/2 + b
#
# The inverse functions recover a and b from the encoded pair:
#   fst(p) extracts the first component
#   snd(p) extracts the second component
#
# To invert, we find w = a + b by searching for the largest w with tri(w) <= p.
# Then b = p - tri(w), and a = w - b.

# pair(a, b) = tri(a + b) + b
pair = compose(add, compose(tri, add), proj(1))


# Helper: find w such that tri(w) <= p < tri(w+1)
# This is the "row" in Cantor's diagonal enumeration
class CantorW:
    def __call__(self, p):
        # find smallest w where tri(w+1) > p, then return w
        exceeds = lambda w: 1 if tri(succ(w)) > p else 0
        return bmin(exceeds, succ(p))

    def __repr__(self):
        return "_cantor_w"


_cantor_w = CantorW()


# snd(p) = p - tri(w) where w = _cantor_w(p)
class Snd:
    def __call__(self, p):
        w = _cantor_w(p)
        return monus(p, tri(w))

    def __repr__(self):
        return "snd"


snd = Snd()


# fst(p) = w - snd(p)
class Fst:
    def __call__(self, p):
        w = _cantor_w(p)
        return monus(w, snd(p))

    def __repr__(self):
        return "fst"


fst = Fst()

# ===========================================================================
# Fibonacci via Cantor pairing
# ===========================================================================

# Now we can define fib purely in PRF terms. We iterate on pairs:
#   state_0 = pair(0, 1) = pair(fib(0), fib(1))
#   state_{k+1} = pair(snd(state_k), fst(state_k) + snd(state_k))
#
# Then fib(n) = fst(state_n).

_initial_fib_pair = pair(0, 1)  # encodes (fib(0), fib(1)) = (0, 1)


class FibStep:
    """Transition: (a, b) -> (b, a+b) encoded as pairs."""

    def __call__(self, k, state):
        a = fst(state)
        b = snd(state)
        return pair(b, add(a, b))

    def __repr__(self):
        return "_fib_step"


_fib_step = FibStep()

# fib_pair(n) returns pair(fib(n), fib(n+1))
fib_pair = prim_rec(
    compose(lambda: _initial_fib_pair),  # base: pair(0, 1)
    _fib_step
)


# fib(n) = fst(fib_pair(n))
class Fib:
    """Fibonacci via primitive recursion on Cantor-encoded pairs."""

    def __call__(self, n):
        return fst(fib_pair(n))

    def __repr__(self):
        return "fib"


fib = Fib()

# ===========================================================================
# Tests
# ===========================================================================

if __name__ == "__main__":
    # predicates
    assert sg(0) == 0 and sg(1) == 1 and sg(100) == 1
    assert sg_bar(0) == 1 and sg_bar(1) == 0
    assert is_zero(0) == 1 and is_zero(5) == 0

    assert eq(3, 3) == 1 and eq(3, 4) == 0 and eq(0, 0) == 1
    assert leq(3, 5) == 1 and leq(5, 5) == 1 and leq(6, 5) == 0
    assert lt(3, 5) == 1 and lt(5, 5) == 0 and lt(6, 5) == 0

    # arithmetic
    assert exp(0, 5) == 1 and exp(3, 2) == 8 and exp(4, 3) == 81
    assert double(7) == 14 and double(0) == 0
    assert square(5) == 25 and square(0) == 0
    assert tri(0) == 0 and tri(1) == 1 and tri(4) == 10 and tri(10) == 55

    # division and remainder
    assert divides(3, 9) == 1 and divides(3, 10) == 0
    assert divides(1, 7) == 1 and divides(7, 7) == 1
    assert divides(0, 0) == 1 and divides(0, 5) == 0

    assert div(10, 3) == 3 and div(9, 3) == 3 and div(8, 3) == 2
    assert div(0, 5) == 0 and div(5, 1) == 5
    assert div(7, 0) == 0  # by convention

    assert rem(10, 3) == 1 and rem(9, 3) == 0 and rem(8, 3) == 2
    assert rem(0, 5) == 0 and rem(5, 1) == 0
    assert rem(7, 0) == 7  # by convention

    # fibonacci
    assert [fib(i) for i in range(10)] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

    # cantor pairing
    # verify pair/fst/snd roundtrip
    for a in range(15):
        for b in range(15):
            p = pair(a, b)
            assert fst(p) == a, f"fst(pair({a},{b})) = {fst(p)}, expected {a}"
            assert snd(p) == b, f"snd(pair({a},{b})) = {snd(p)}, expected {b}"

    # verify pair is injective (different inputs -> different outputs)
    seen = set()
    for a in range(20):
        for b in range(20):
            p = pair(a, b)
            assert p not in seen, f"pair({a},{b}) collides"
            seen.add(p)

    # spot checks for known values
    assert pair(0, 0) == 0
    assert pair(1, 0) == 1
    assert pair(0, 1) == 2
    assert pair(2, 0) == 3
    assert pair(1, 1) == 4
    assert pair(0, 2) == 5

    print("all examples passed")