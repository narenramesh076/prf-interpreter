#!/usr/bin/env python3
"""
Additional primitive recursive functions and Presburger Extension Explorer.
"""

from prf import zero, succ, proj, compose, prim_rec, bmin
from prf import add, mult, pred, monus, factorial, PresburgerExtension

# ===========================================================================
# Predicates (returning 0 or 1)
# ===========================================================================

_one = compose(succ, zero)
_const = compose(_one)

sg = prim_rec(zero, _const)
sg_bar = compose(monus, _const, sg)
is_zero = sg_bar

_abs_diff = compose(add, monus, compose(monus, proj(1), proj(0)))
eq = compose(is_zero, _abs_diff)

leq = compose(is_zero, monus)
lt = compose(leq, compose(succ, proj(0)), proj(1))

# ===========================================================================
# Arithmetic
# ===========================================================================

exp = prim_rec(
    _const,
    compose(mult, proj(2), proj(1))
)

pred_alt = prim_rec(zero, proj(0))
double = compose(add, proj(0), proj(0))
square = compose(mult, proj(0), proj(0))

tri = prim_rec(
    zero,
    compose(add, proj(1), compose(succ, proj(0)))
)

# ===========================================================================
# Division and remainder
# ===========================================================================

class Divides:
    def __call__(self, d, n):
        if d == 0:
            return 1 if n == 0 else 0
        return 1 if n % d == 0 else 0
    def __repr__(self):
        return "divides"
divides = Divides()

class Div:
    def __call__(self, a, b):
        if b == 0:
            return 0
        exceeds = lambda q: 1 if mult(b, succ(q)) > a else 0
        return bmin(exceeds, succ(a))
    def __repr__(self):
        return "div"
div = Div()

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

pair = compose(add, compose(tri, add), proj(1))

class CantorW:
    def __call__(self, p):
        exceeds = lambda w: 1 if tri(succ(w)) > p else 0
        return bmin(exceeds, succ(p))
    def __repr__(self):
        return "_cantor_w"
_cantor_w = CantorW()

class Snd:
    def __call__(self, p):
        w = _cantor_w(p)
        return monus(p, tri(w))
    def __repr__(self):
        return "snd"
snd = Snd()

class Fst:
    def __call__(self, p):
        w = _cantor_w(p)
        return monus(w, snd(p))
    def __repr__(self):
        return "fst"
fst = Fst()

# ===========================================================================
# Fibonacci
# ===========================================================================

_initial_fib_pair = pair(0, 1)

class FibStep:
    def __call__(self, k, state):
        a = fst(state)
        b = snd(state)
        return pair(b, add(a, b))
    def __repr__(self):
        return "_fib_step"
_fib_step = FibStep()

fib_pair = prim_rec(
    compose(lambda: _initial_fib_pair),
    _fib_step
)

class Fib:
    def __call__(self, n):
        return fst(fib_pair(n))
    def __repr__(self):
        return "fib"
fib = Fib()

# ===========================================================================
# Predicates for Presburger Extension Explorer
# ===========================================================================

# is_prime
def _has_proper_divisor(n):
    if n <= 2:
        return 0
    def divisor_exists(d):
        if d >= n:
            return 0
        return divides(d, n)
    d0 = bmin(divisor_exists, n)
    return 1 if d0 < n else 0

def _is_prime(n):
    if n < 2:
        return 0
    return 1 if _has_proper_divisor(n) == 0 else 0
is_prime_prf = _is_prime

# is_power_of_two
def _is_power_of_two(n):
    if n == 0:
        return 0
    def check(k):
        return eq(exp(k, 2), n)
    k0 = bmin(check, n)
    return 1 if k0 < n else 0
is_power_of_two_prf = _is_power_of_two

# is_perfect_square
def _is_perfect_square(n):
    def check(k):
        return eq(mult(k, k), n)
    k0 = bmin(check, n+1)
    return 1 if k0 <= n else 0
is_square_prf = _is_perfect_square

# odd_parity (uses Python bin, not pure PRF, for demo)
def _odd_parity(n):
    return bin(n).count('1') % 2
odd_parity_prf = _odd_parity

# is_smooth (demo, not pure PRF)
def _is_smooth(n, primes=[2,3,5]):
    if n == 0:
        return 0
    m = n
    for p in primes:
        while m % p == 0:
            m //= p
    return 1 if m == 1 else 0
smooth_prf = _is_smooth

# ===========================================================================
# PresburgerExtension instances
# ===========================================================================

prime_ext = PresburgerExtension("is_prime", is_prime_prf)
power_ext = PresburgerExtension("is_power_of_two", is_power_of_two_prf)
square_ext = PresburgerExtension("is_perfect_square", is_square_prf)
parity_ext = PresburgerExtension("odd_parity", odd_parity_prf)
smooth_ext = PresburgerExtension("is_{2,3,5}_smooth", smooth_prf)

# ===========================================================================
# Interactive exploration function
# ===========================================================================

def explore_extensions():
    extensions = [
        prime_ext,
        power_ext,
        square_ext,
        parity_ext,
        smooth_ext
    ]

    print("="*60)
    print("Presburger Extension Explorer")
    print("="*60)
    print("We look at theories Th(ℕ; +, <, P).")
    print("If P helps define multiplication, the theory becomes")
    print("as complex as full arithmetic (degree 0').")
    print("If not, it stays decidable (degree 0).")
    print("Intermediate degrees are rare and delicate.")
    print()

    for ext in extensions:
        ext.describe()
        print(f"First 20 values: {[ext(i) for i in range(20)]}")
        ext.check_multiplication_heuristic(max_samples=20)
        print("-"*60)

    print("\nObservations from the literature:")
    print("- Feferman (1957) constructed intermediate-degree theories")
    print("  but they are artificial (via consistency statements).")
    print("- Peretyat'kin (1991) showed the undecidable Lindenbaum")
    print("  algebra is unique, suggesting natural undecidable theories")
    print("  are all max degree.")
    print("- Your 'all-or-nothing' hypothesis: natural theories either")
    print("  interpret full arithmetic (0') or stay decidable (0).")
    print()
    print("Try your own predicate: squares = PresburgerExtension('is_square', is_square_prf)")
    print("Then run squares.check_multiplication_heuristic().")

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
    assert div(7, 0) == 0

    assert rem(10, 3) == 1 and rem(9, 3) == 0 and rem(8, 3) == 2
    assert rem(0, 5) == 0 and rem(5, 1) == 0
    assert rem(7, 0) == 7

    # fibonacci
    assert [fib(i) for i in range(10)] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

    # cantor pairing
    for a in range(15):
        for b in range(15):
            p = pair(a, b)
            assert fst(p) == a
            assert snd(p) == b

    # new predicates (basic checks)
    assert is_prime_prf(2) == 1
    assert is_prime_prf(4) == 0
    assert is_prime_prf(17) == 1
    assert is_power_of_two_prf(1) == 1
    assert is_power_of_two_prf(16) == 1
    assert is_power_of_two_prf(6) == 0
    assert is_square_prf(0) == 1
    assert is_square_prf(25) == 1
    assert is_square_prf(26) == 0

    print("all examples passed")
    print("\n" + "="*60)
    print("Run explore_extensions() to start the explorer.")
    print("="*60)