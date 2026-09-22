import ast


class MemoryAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.uses_dynamic_memory = False

    def visit_ListComp(self, node):
        self.uses_dynamic_memory = True
        self.generic_visit(node)

    def visit_SetComp(self, node):
        self.uses_dynamic_memory = True
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self.uses_dynamic_memory = True
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in [
                "append",
                "extend",
                "add",
                "update"
            ]:
                self.uses_dynamic_memory = True

        self.generic_visit(node)


def is_number_greater_than_one(node):
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, (int, float))
        and node.value > 1
    )


def is_logarithmic_while(node):
    """
    Detect simple logarithmic loops such as:

    while n > 1:
        n //= 2

    or:

    while x < n:
        x *= 2
    """

    for child in ast.walk(node):

        if isinstance(child, ast.AugAssign):
            if isinstance(
                child.op,
                (ast.Div, ast.FloorDiv, ast.Mult)
            ):
                if is_number_greater_than_one(child.value):
                    return True

        if isinstance(child, ast.Assign):
            if len(child.targets) != 1:
                continue

            target = child.targets[0]

            if not isinstance(target, ast.Name):
                continue

            value = child.value

            if isinstance(value, ast.BinOp):
                if isinstance(
                    value.op,
                    (ast.Div, ast.FloorDiv, ast.Mult)
                ):
                    if (
                        isinstance(value.left, ast.Name)
                        and value.left.id == target.id
                        and is_number_greater_than_one(value.right)
                    ):
                        return True

    return False


def max_complexity(first, second):
    """
    Complexity is represented as:

    (power_of_n, power_of_log)

    Examples:
    O(1)       -> (0, 0)
    O(log n)   -> (0, 1)
    O(n)       -> (1, 0)
    O(n log n) -> (1, 1)
    O(n^2)     -> (2, 0)
    """

    if first[0] > second[0]:
        return first

    if second[0] > first[0]:
        return second

    if first[1] >= second[1]:
        return first

    return second


def analyze_statements(statements):
    complexity = (0, 0)

    for statement in statements:
        statement_complexity = analyze_node(statement)

        complexity = max_complexity(
            complexity,
            statement_complexity
        )

    return complexity


def analyze_node(node):

    # Normal for-loop: O(n)
    if isinstance(node, ast.For):

        body_complexity = analyze_statements(node.body)

        return (
            body_complexity[0] + 1,
            body_complexity[1]
        )

    # While loop
    if isinstance(node, ast.While):

        body_complexity = analyze_statements(node.body)

        if is_logarithmic_while(node):
            return (
                body_complexity[0],
                body_complexity[1] + 1
            )

        return (
            body_complexity[0] + 1,
            body_complexity[1]
        )

    # If statement
    if isinstance(node, ast.If):

        body_complexity = analyze_statements(node.body)
        else_complexity = analyze_statements(node.orelse)

        return max_complexity(
            body_complexity,
            else_complexity
        )

    # Function
    if isinstance(
        node,
        (ast.FunctionDef, ast.AsyncFunctionDef)
    ):
        return analyze_statements(node.body)

    # List/set/dictionary comprehensions
    if isinstance(
        node,
        (ast.ListComp, ast.SetComp, ast.DictComp)
    ):
        number_of_loops = len(node.generators)

        return (number_of_loops, 0)

    return (0, 0)


def complexity_to_string(complexity):
    n_power, log_power = complexity

    if n_power == 0 and log_power == 0:
        return "O(1)"

    if n_power == 0 and log_power == 1:
        return "O(log n)"

    if n_power == 1 and log_power == 0:
        return "O(n)"

    if n_power == 1 and log_power == 1:
        return "O(n log n)"

    if n_power > 1 and log_power == 0:
        return f"O(n^{n_power})"

    if n_power > 0 and log_power > 0:
        return f"O(n^{n_power} log n)"

    return "O(1)"


def analyze_complexity(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        source_code = file.read()

    tree = ast.parse(source_code)

    time_complexity = analyze_statements(tree.body)

    memory_analyzer = MemoryAnalyzer()
    memory_analyzer.visit(tree)

    if memory_analyzer.uses_dynamic_memory:
        space_complexity = "O(n)"
    else:
        space_complexity = "O(1)"

    return {
        "time_complexity":
            complexity_to_string(time_complexity),

        "space_complexity":
            space_complexity
    }