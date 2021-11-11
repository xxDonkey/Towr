# Towr

A stack based language inspired by [Porth](https://github.com/tsoding/porth), and is compiled by Python. It also has memory storage outside of the stack, and many interesting features.

## Goals

- [ ] Native
- [ ] Compiled
- [ ] Stack-based 

## Intrinsics

### `+` - PLUS
Expects: `a, b`
Returns: `a + b`

### `-` - MINUS
Expects: `a, b`
Returns: `a - b`

### `*` - MULTIPLY
Expects: `a, b`
Returns: `a * b`

### `/` - DIVMOD
Expects: `a, b`
Returns: `b % a, floor(b / a)`

### `^` - PRINT
Expects: `a`
Returns: `none`

### `~` - SWAP
Expects: `a, b`
Returns: `b, a`

### `~` - EQUALS
Expects: `a, b`
Returns: `a == b`

### `~` - GREATER
Expects: `a, b`
Returns: `a > b`

### `~` - LESS
Expects: `a, b`
Returns: `a < b`

### `dup` - DUP
Expects: `a`
Returns: `a, a`

### `drop` - DROP
Expects: `a`
Returns: `none`

### `=` - STORE
Expects: `ref, val`
Returns: `none`

### `@a` - READ
Expects: `ref`
Returns: `val`

### `++` - INC
Expects: `a`
Returns: `a + 1`

### `--` - DEC
Expects: `a`
Returns: `a - 1`
