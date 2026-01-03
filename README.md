# Primitive Recursive Functions

A minimal interpreter for primitive recursive functions in Python.

PRFs are built from `zero`, `succ`, `proj`, `compose`, and `prim_rec`. 
This implementation derives `add`, `mult`, `pred`, `monus`, `factorial`, 
and `bmin` (bounded minimization) from these primitives.

## Usage

```
python prf.py
```

Runs tests, then starts a REPL:

```
>>> add(3, mult(2, 2))
7
>>> factorial(6)
720
>>> monus(10, 4)
6
```

## Bounded minimization

The `bmin(p, n)` function finds the smallest `k < n` where predicate `p(k) = 1`,
or returns `n` if none exists. This is the bounded μ-operator — the key to
defining division, remainder, and other search-based functions while staying
within primitive recursion.

```python
from prf import bmin

is_even = lambda k: 1 if k % 2 == 0 else 0
bmin(is_even, 10)  # => 0 (first even number)
```

## examples.py

Additional functions built on the core primitives:

- Predicates: `sg`, `sg_bar`, `is_zero`, `eq`, `leq`, `lt`
- Arithmetic: `exp`, `double`, `square`, `tri` (triangular numbers)
- Division: `div`, `rem`, `divides` (via bounded minimization)
- Pairing: `pair`, `fst`, `snd` (Cantor pairing for encoding pairs)
- Fibonacci: `fib` (uses pairing to encode two accumulators)

```
python examples.py
```

## Cantor pairing

The `pair(a, b)` function encodes two natural numbers as a single number,
bijectively. The inverse functions `fst(p)` and `snd(p)` recover the components.

```python
from examples import pair, fst, snd

p = pair(3, 7)   # => 59
fst(p)           # => 3
snd(p)           # => 7
```

This is how PRFs handle data structures. The Fibonacci function uses pairing
to track two values `(fib(k), fib(k+1))` as a single number at each step.

## Define your own

```python
from prf import *

# double(x) = x + x
double = compose(add, proj(0), proj(0))
double(5)  # => 10

# power(n, b) = b^n
power = prim_rec(
    compose(succ, zero),              # base: 1
    compose(mult, proj(2), proj(1))   # step: b * acc
)
power(3, 2)  # => 8
```

## References

- Kleene (1952), *Introduction to Metamathematics*
- Cutland (1980), *Computability*