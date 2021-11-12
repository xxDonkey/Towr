# Intrinsics

The operators are inherent to the language. They take values of the stack and pushes resultant values back. They can also not take values from the stack, and only push. Similarly, there are operators that only push values to the stack. 

### Plus [ `+` ]

Takes the top 2 values on the stack and pushes the sum.
```
a = pop
b = pop
push a + b
```

***

### MINUS [ `-` ]

Takes the top 2 values on the stack and pushes the difference.
```
a = pop

***
b = pop
push a - b
```

***

### MULTIPLY [ `*` ]

Takes the top 2 values on the stack and pushes the product.
```
a = pop
b = pop
push a * b
```

***

### DIVMOD [ `/` ]

Takes the top 2 values on the stack and pushes the integer value from the division, and the remainder, where `b` is the dividend and `a` is the divisor.
```
a = pop
b = pop
push b % a
push floor(b / a)
```

***

### PRINT [ `^` ]

Takes the top value on the stack and prints it.
```
a = pop
print a
```

***

### SWAP [ `~` ]

Takes the top 2 values on the stack and switches their order.
```
a = pop
b = pop
push a
push b
```

***

### EQUALS [ `==` ]

Takes the top 2 values on the stack and compares them. Returns `1` if they are equal and `0` if they are not equal.
```
a = pop
b = pop
push a == b
```

***

### GREATER [ `>` ]

Takes the top 2 values on the stack and compares them. Returns `1` if `a > b` otherwise `0`.
```
a = pop
b = pop
push a > b
```

***

### LESS [ `<` ]

Takes the top 2 values on the stack and compares them. Returns `1` if `a < b` otherwise `0`.
```
a = pop
b = pop
push a < b
```

***

### DUP [ `dup` ]

Duplicates the top value on the stack.
```
a = pop
push a
push a
```

***

### DROP [ `drop` ]

Removes the top value from the stack.
```
a = pop
```

***

### STORE [ `=` ]

Stores `val` into the address `ref`. This is used to set variable values after declaration.
```
ref = pop
val = pop
&ref = val
```

***

### READ [ `@` ]

Retrieves the value at address `ref` and pushes it to the stack.
```
*ref = pop
val = *ref
push val
```

***

### INC [ `++` ]

Increments the top value on the stack.
```
pop a
a += 1
push a
```

***

### DEC [ `--` ]

Decrement the top value on the stack.
```
pop a
a -= 1
push a
```