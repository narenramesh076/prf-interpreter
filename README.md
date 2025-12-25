# prf-interpreter

A minimal interpreter for primitive recursive functions in Python.

PRFs are built from `zero`, `succ`, `proj`, `compose`, and `prim_rec`. 
This implementation derives `add`, `mult`, `pred`, `monus`, and `factorial` 
from these primitives alone.

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

## Define your own
```python
from prf import *

# double(x) = x + x
double = compose(add, proj(0), proj(0))

# power(n, b) = b^n
power = prim_rec(
    compose(succ, zero),              # base: 1
    compose(mult, proj(1), proj(2))   # step: acc * b
)
```

## References

- Kleene (1952), *Introduction to Metamathematics*
- Cutland (1980), *Computability*