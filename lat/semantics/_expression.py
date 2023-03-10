import sys

from lat import compiler_error, compiler_note, std_message


class Primary:
    """
    Class that handles the basic building blocks of an expression.
    """

    def __init__(self):
        self.productions = {  #   Maps production names to their respective functions
            "integer": self._int,
            "float": self._float,
            "filum": self._string,
            "id": self._id,
            "ref": self._ref,
            "indexing": self._indexing,
            "array_indexing_depth": self._array_indexing_depth,
            "new": self._new,
        }

    def handle(self, p, production) -> str:  # Calls the function corresponding to the production
        return self.productions[production](p)  # This is the function that is called by the parser

    def _int(self, p) -> str:  # Handles pushing an integer
        """
        primary : INTEGER
        """
        p.parser.type_checker.push("integer")
        return std_message([f"PUSHI {p[1]}"])  # Return the message

    def _float(self, p) -> str:  # Handles pushing an integer
        """
        primary : FLOAT
        """
        p.parser.type_checker.push("float")
        return std_message([f"PUSHF {p[1]}"])  # Return the message

    def _string(self, p) -> str:  # Handles pushing an integer
        """
        primary : FILUM
        """
        p.parser.type_checker.push("filum")
        return std_message([f"PUSHS {p[1]}"])  # Return the message

    def _id(self, p) -> str:  # Handles pushing the value of a variable
        """
        primary : ID
        """
        id_meta, in_function, _ = p.parser.current_scope.get(p[1])  # Get the metadata of the variable
        if id_meta is None:  # If the variable is not declared, Throw an error
            compiler_error(p, 1, f"Variable {p[1]} not declared")
            compiler_note("Called from Primary.id")
            sys.exit(1)
        if not id_meta.p_init:
            compiler_error(p, 1, f"Using non initialized pointer '{p[1]}'")
            compiler_note("Called from Primary.id")
            sys.exit(1)

        push_op = "PUSHGP" if not in_function else "PUSHFP"  # If the variable is in a function, push the frame pointer else push the global pointer
        if id_meta.type.startswith("vec"):
            p.parser.type_checker.push(f"&{id_meta.type[4:-1]}")
            return std_message([push_op, f"PUSHI {id_meta.stack_position[0]}", "PADD"])
        else:
            p.parser.type_checker.push(id_meta.type)
            return std_message([push_op, f"LOAD {id_meta.stack_position[0]}"])  # Return the message

    def _ref(self, p) -> str:  # Handles getting the address of a variable
        """
        primary : '&' ID
        """
        id_meta, in_function, _ = p.parser.current_scope.get(p[2])
        if id_meta is None:  # If the variable is not declared, Throw an error
            compiler_error(p, 2, f"Variable {p[2]} not declared")
            compiler_note("Called from Primary._ref")
            sys.exit(1)
        if id_meta.type.startswith("&") or id_meta.type.startswith("vec"):
            compiler_error(p, 1, f"Pointer to pointer not supported")
            compiler_note("Called from Primary._ref")
            sys.exit(1)
        p.parser.type_checker.push(f"&{id_meta.type}")

        push_op = "PUSHGP" if not in_function else "PUSHFP"  # If the variable is in a function, push the frame pointer else push the global pointer
        return std_message([push_op, f"PUSHI {id_meta.stack_position[0]}", "PADD"])  # Return the message

    def _indexing(self, p) -> str:  # Handles indexing into an array
        """
        primary : ID ndepth
        """
        id_meta, in_function, _ = p.parser.current_scope.get(p[1])  # Get the metadata of the variable
        if id_meta is None:  # If the variable is not declared, Throw an error
            compiler_error(p, 1, f"Variable {p[1]} not declared")
            compiler_note("Called from Primary._indexing")
            sys.exit(1)
        if not id_meta.type.startswith("vec") and not id_meta.type.startswith("&"):
            compiler_error(p, 1, f"Can't index into variable of type '{id_meta.type}'")
            compiler_note("Called from Assignment._array_index")
            sys.exit(1)
        if not id_meta.p_init:
            compiler_error(p, 1, f"Indexing into non initialized pointer '{p[1]}'")
            compiler_note("Called from Primary._indexing")
            sys.exit(1)
        if len(p.parser.indexing_depth[-1]) > 1 and id_meta.type.startswith("&"):
            compiler_error(p, 1, f"Can't index pointer with more than one dimension")
            compiler_note("Called from Primary._indexing")
            sys.exit(1)
        if id_meta.array_shape and len(p.parser.indexing_depth[-1]) > len(id_meta.array_shape):
            compiler_error(p, 1, f"Indexing into dimension {len(p.parser.indexing_depth[-1])} of array {p[1]} of dimension {len(id_meta.array_shape)}")
            compiler_note("Called from Primary._indexing")
            sys.exit(1)

        push_op = "PUSHGP" if not in_function else "PUSHFP"  # If the variable is in a function, push the frame pointer else push the global pointer
        if id_meta.type.startswith("vec"): # If the variable is an array
            op = [push_op, f"PUSHI {id_meta.stack_position[0]}", "PADD"] # Push the array base address
            for i, expr in enumerate(p.parser.indexing_depth[-1]): # For each index
                factor = ["PUSHI 1"]                        #
                for dim in id_meta.array_shape[i + 1 :]:    # Calculate the factor for indexing
                    factor += [f"PUSHI {dim}", "MUL"]       #
                op += [expr] + factor + ["MUL", "PADD"]     # Add the offset to the base address
            if len(p.parser.indexing_depth[-1]) < len(id_meta.array_shape): # If the indexing is not complete
                p.parser.indexing_depth.pop()              # Pop the indexing depth
                p.parser.type_checker.push("&" + id_meta.type[4:-1]) # Push a pointer to the correct type
                return std_message(op)                   # Push the op pointer
            else:                                       # If the indexing is complete
                p.parser.indexing_depth.pop()           # Pop the indexing depth
                p.parser.type_checker.push(id_meta.type[4:-1]) # Push the correct type
                return std_message(op + ["LOAD 0"])    # Push the op pointer and load the value
        elif id_meta.type.startswith("&"):  # If the variable is a pointer
            p.parser.type_checker.push(id_meta.type[1:])    # Push the correct type
            expr = p.parser.indexing_depth.pop()        # Pop the indexing depth
            return std_message([push_op, f"LOAD {id_meta.stack_position[0]}", f"{expr[0]}PADD", "LOAD 0"])  # Push the pointer and load the value

    def _array_indexing_depth(self, p):
        """
        ndepth: ndepth '[' expression ']'
            | '[' expression ']'
        """
        idx = p.parser.type_checker.pop()
        if idx != "integer":
            compiler_error(p, 1, f"Index must be an integer, not {idx}")
            compiler_note("Called from Primary._array_indexing_depth")
            sys.exit(1)

        if len(p) == 5:
            p.parser.indexing_depth[-1].append(p[3])
        else:
            p.parser.indexing_depth.append([p[2]])

    def _new(self, p) -> str:  # Handles a grouped expression
        """
        primary : '(' expression ')'
        """
        return p[2]  # Return the message


class Unary:
    """
    Class that handles unary operations.
    """

    def __init__(self):
        self.productions = {"not": self._not, "neg": self._neg, "primary": self._primary}  #   Maps production names to their respective functions

    def handle(self, p, production) -> str:  # Calls the function corresponding to the production
        return self.productions[production](p)  # This is the function that is called by the parser

    def _not(self, p) -> str:  # Handles a not operation
        """
        unary : '!' unary
        """
        return p.parser.type_checker.handle(p, "not")

    def _neg(self, p) -> str:  # Handles a negation operation
        """
        unary : '-' unary
        """
        return p.parser.type_checker.handle(p, "neg")

    def _primary(self, p) -> str:  # Handles a primary expression
        """
        unary : primary
        """
        return p[1]  # Return the message


class Factor:
    """
    Class that handles factor operations.
    """

    def __init__(self):
        self.productions = {"mul": self._mul, "div": self._div, "mod": self._mod, "unary": self._unary}  #   Maps production names to their respective functions

    def handle(self, p, production) -> str:  # Calls the function corresponding to the production
        return self.productions[production](p)  # This is the function that is called by the parser

    def _mul(self, p) -> str:  # Handles a multiplication operation
        """
        factor : factor '*' unary
        """
        return p.parser.type_checker.handle(p, "mul")

    def _div(self, p) -> str:  # Handles a division operation
        """
        factor : factor '/' unary
        """
        return p.parser.type_checker.handle(p, "div")

    def _mod(self, p) -> str:  # Handles a modulo operation
        """
        factor : factor '%' unary
        """
        return p.parser.type_checker.handle(p, "mod")

    def _unary(self, p) -> str:  # Handles a unary expression
        """
        factor : unary
        """
        return p[1]  # Return the message


class Term:
    """
    Class that handles term operations.
    """

    def __init__(self):
        self.productions = {"add": self._add, "sub": self._sub, "factor": self._factor}  #   Maps production names to their respective functions

    def handle(self, p, production) -> str:  # Calls the function corresponding to the production
        return self.productions[production](p)  # This is the function that is called by the parser

    def _add(self, p) -> str:  # Handles an addition operation
        """
        term : term '+' factor
        """
        return p.parser.type_checker.handle(p, "add")

    def _sub(self, p) -> str:  # Handles a subtraction operation
        """
        term : term '-' factor
        """
        return p.parser.type_checker.handle(p, "sub")

    def _factor(self, p) -> str:  # Handles a factor expression
        """
        term : factor
        """
        return p[1]  # Return the message


class Comparison:
    """
    Class that handles comparison operations.
    """

    def __init__(self):
        self.productions = {"lt": self._lt, "gt": self._gt, "lte": self._lte, "gte": self._gte, "term": self._term}  #   Maps production names to their respective functions

    def handle(self, p, production) -> str:  # Calls the function corresponding to the production
        return self.productions[production](p)  # This is the function that is called by the parser

    def _lt(self, p) -> str:  # Handles a less than operation
        """
        comparison : comparison '<' term
        """
        return p.parser.type_checker.handle(p, "lt")

    def _gt(self, p) -> str:  # Handles a greater than operation
        """
        comparison : comparison '>' term
        """
        return p.parser.type_checker.handle(p, "gt")

    def _lte(self, p) -> str:  # Handles a less than or equal to operation
        """
        comparison : comparison '<=' term
        """
        return p.parser.type_checker.handle(p, "lte")

    def _gte(self, p) -> str:  # Handles a greater than or equal to operation
        """
        comparison : comparison '>=' term
        """
        return p.parser.type_checker.handle(p, "gte")

    def _term(self, p) -> str:  # Handles a term expression
        """
        comparison : term
        """
        return p[1]  # Return the message


class Condition:
    """
    Class that handles conditions.
    """

    def __init__(self):
        self.productions = {"eq": self._eq, "neq": self._neq, "comparison": self._comparison}  #   Maps production names to their respective functions

    def handle(self, p, production) -> str:  # Calls the function corresponding to the production
        return self.productions[production](p)  # This is the function that is called by the parser

    def _eq(self, p) -> str:  # Handles an equal to operation
        """
        condition : condition EQ comparison
        """
        return p.parser.type_checker.handle(p, "eq")

    def _neq(self, p) -> str:  # Handles a not equal to operation
        """
        condition : condition NEQ comparison
        """
        return p.parser.type_checker.handle(p, "neq")

    def _comparison(self, p) -> str:  # Handles a comparison expression
        """
        condition : comparison
        """
        return p[1]  # Return the message


class SubExpression:
    """
    Class that handles subexpressions.
    """

    def __init__(self):
        self.productions = {"and": self._and, "condition": self._condition}  #   Maps production names to their respective functions

    def handle(self, p, production) -> str:  # Calls the function corresponding to the production
        return self.productions[production](p)  # This is the function that is called by the parser

    def _and(self, p) -> str:  # Handles an and operation
        """
        subexpression : subexpression AND condition
        """
        return p.parser.type_checker.handle(p, "and")

    def _condition(self, p) -> str:  # Handles a condition expression
        """
        subexpression : condition
        """
        return p[1]  # Return the message


class Expression:
    """
    Class that handles expressions.
    """

    def __init__(self):
        self.productions = {"or": self._or, "subexpression": self._subexpression}  #   Maps production names to their respective functions

    def handle(self, p, production) -> str:  # Calls the function corresponding to the production
        return self.productions[production](p)  # This is the function that is called by the parser

    def _or(self, p) -> str:  # Handles an or operation
        """
        expression : expression OR subexpression
        """
        return p.parser.type_checker.handle(p, "or")

    def _subexpression(self, p) -> str:  # Handles a subexpression expression
        """
        expression : subexpression
        """
        return p[1]  # Return the message
