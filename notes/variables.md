# Variables

Variables are (for now) stored in heap. They (for now) are never released and are held by the program until the end of runtime. In the future, they will be stored on the stack and will be released dynamically. Additionally, there are two types are variable creation statements, as detailed below.

## 1. `let`

This statment allocates 1 "byte" and assigns the passed value. Except this is not actually 8 bits. Instead, it allocates the smallest number of bits allocated by C call [`crt_malloc`](https://docs.microsoft.com/en-us/cpp/c-runtime-library/reference/malloc?view=msvc-170). In the case of 64-bit processors, this will be 64 bits. There is an intrinsic titled `sizeof_byte` that will push this value to stack, depending on the operating system and processor architecture.

#### **Interacting With The Variable**

There are two main ways to interact with a `let` variable. First, is by simply writing its name. This pushes that value in the variable onto the stack. If you use the `&` operator (attached to the front of the variable name, no space), it will push the address of the variable to the stack.

```
let x 8 end     # creates a 64-bit signed integer and assigns it a value of 8
x               # returns 8
&x              # returns a memory address
```

## 2. `letmem`

Similarly to `let`, this keyword assigns memory. However, instead of allocating a static 1 byte it allocates a number of bytes equivalent to the value passed to it. This allows for the creation of arrays and more complex datastructres.

#### **Interacting With The Variable**

There are actually three ways to interact with a `letmem` variable. To understand why, we must look how the variables are created in assembly. Before the code body is run, an address is allocated to the variable, but with no data. Using the aforementioned [`crt_malloc`](https://docs.microsoft.com/en-us/cpp/c-runtime-library/reference/malloc?view=msvc-170), memory is allocated and the address is stored in the variable's value. As a result, we can access the variable's memory address, its value (which is also a memory address), and the value(s) at that address (using the `@` operator). Similarly to before, it will push all these values to the stack.
```
letmem x 1 end  # allocates 1 byte worth of memory and assigns its address to x
x               # returns the allocated memory's address
&x              # returns the memory address of x
x @             # returns the value in the allocated memory
```

