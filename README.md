# **Latinium Programming Language**


```Latinium``` is a small programming language designed to run on a Virtual Machine. The Virtual Machine executable is located in ```vm/```. This programming language was built using the library [ply](www.dabeaz.com/ply/). 

**Note**: The Virtual Machine was developed by students at the University of Minho, Portugal.I did not develop the Virtual Machine, I only developed the programming language. To learn more about the Virtual Machine, please refer to the zip file ```vms-vf.zip``` in the ```vm/``` directory. Also note that I made some modifications to the Virtual Machine in order to make it compatible with the Virtual Machine at [EWVM](https://ewvm.epl.di.uminho.pt/). Those modifications include:
- Adding a new instructions to the Virtual Machine (```AND```, ```OR```).
- Improving the memory consumption of the Virtual Machine by reducing the number of memory leaks.

## **Installation**

Installing through pip:

```rustonsole
git clone https://github.com/fabiocfabini/Latinium.git
cd Latinium
make install
pip install -e .
```

**Note**: Only works on linux.

## **Quick Start**

```rustonsole
Latinium run examples/hello_world.Latinium
```

## **Features**

### **Comments**

To add one line comments, simply type ```//``` followed by the comment. For example:

```rust
// This is a comment
```

Multiline comments can be added by typing ```/*``` followed by the comment and ```*/``` at the end. For example:

```rust
/*
This is a multiline comment
*/
```

### **Data Types**

Has of now, the language supports the following data types:

- ```integer```, ```float```, ```filum```: These are the basic data types of the language;
- ```&integer```, ```&float```, ```&filum```: These are the pointer data types of the language;
- vec```<integer>```, vec```<float>```, vec```<filum>```: These are the vector data types of the language;

### **Arithmetics**

Basic arithmetics are supported by the language. These include:

- the ```+```, ```-```, ```*```, ```/``` operators;
- the ```==```, ```!=```, ```<```, ```>```, ```<=```, ```>=``` operators;
- the ```et```, ```aut``` operators;
- the ```non``` operator;

Latinium also supports pointer arithmetics. The following operations are supported:

- ```+``` adds an integer to a pointer;
- ```-``` subtracts an integer from a pointer and returns the difference between two pointers;
- ```>```, ```<```, ```>=```, ```<=``` compares two pointers;

### **Variables**

To declare a variable, simply type the variable name followed by ```:``` and the variable type. For example:

```rust
a: integer
```

Variables declared in this way are initialized with the value ```0```. To declare a variable and initialize it with a value, simply type the variable name followed by ```:``` and the variable type followed by ```=``` and the value. For example:

```rust
a: integer = 10
```

To modify the value of a variable, simply type the variable name followed by ```=``` and the value. For example:

```rust
a = 20
```

### **Arrays**

In Latinium arrays are declared in 3 different ways:

- Declaring an array of a specific size. This will initialize the array with the value ```0```;

```rust
a: vec<integer>[10]
```

- Declaring an array through a list of values;

```rust
a: vec<integer> = [10, 20, 30, 40, 50]
```

- Declaring an array with the ```...``` operator;

```rust
a: vec<integer> = [1 ... 10]
```

This will initialize the array with the values ```1, 2, 3, 4, 5, 6, 7, 8, 9, 10```.

To access an array element, simply type the array name followed by ```[``` and the index of the element followed by ```]```. For example:

```rust
a[0]
```


### **Control Flow**

The control flow of the language is similar to the control flow of C. These include:

- ```si```, ```si aliter``` and ```si aliter si``` statements;

```rust
si expression {
    // code
}

// or

si expression {
    // code
} aliter {
    // code
}

// or

si expression {
    // code
} aliter si expression {
    // code
} aliter {
    // code
}
```

- ```par``` statements;

```rust
par expression {
    expression -> {
        // code
    }
    ...
    default -> {
        // code
    }
}
```

- ```dum``` statements;

```rust
dum expression {
    // code
}
```

- ```facio dum``` statements;

```rust
facio {
    // code
} dum(expression)
```

- ```enim``` statements;

```rust
enim(i: integer = 0; i < 10; i = i + 1) {
    // code
}
```


### **Functions**

To declare a function start with the key word ```munus``` followed by the function name, the function parameters and the function return type. For example:

```rust
munus sum(a: integer, b: integer) -> integer {
    reditus a + b
}
```

To call a function, simply type the function name followed by the function parameters. For example:

```rust
sum(10, 20)
```
