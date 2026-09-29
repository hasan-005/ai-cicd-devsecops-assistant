import ast
from pathlib import Path


class ComplexityAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.current_loop_depth = 0
        self.max_loop_depth = 0

        self.has_sorting = False
        self.has_log_loop = False

        self.dynamic_memory = False

    # ========================================================
    # LOOP DETECTION
    # ========================================================

    def visit_For(self, node):
        self.current_loop_depth += 1

        self.max_loop_depth = max(
            self.max_loop_depth,
            self.current_loop_depth,
        )

        self.generic_visit(node)

        self.current_loop_depth -= 1

    def visit_AsyncFor(self, node):
        self.current_loop_depth += 1

        self.max_loop_depth = max(
            self.max_loop_depth,
            self.current_loop_depth,
        )

        self.generic_visit(node)

        self.current_loop_depth -= 1

    def visit_While(self, node):
        self.current_loop_depth += 1

        self.max_loop_depth = max(
            self.max_loop_depth,
            self.current_loop_depth,
        )

        # Detect common logarithmic patterns such as:
        # n //= 2
        # n /= 2
        # n *= 2
        for child in ast.walk(node):

            if isinstance(child, ast.AugAssign):

                if isinstance(
                    child.op,
                    (
                        ast.FloorDiv,
                        ast.Div,
                        ast.Mult,
                    ),
                ):
                    self.has_log_loop = True

        self.generic_visit(node)

        self.current_loop_depth -= 1

    # ========================================================
    # SORTING
    # ========================================================

    def visit_Call(self, node):

        # sorted(...)
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "sorted"
        ):
            self.has_sorting = True

        # something.sort()
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "sort"
        ):
            self.has_sorting = True

        # Dynamic structures such as:
        # list.append(...)
        # list.extend(...)
        # set.add(...)
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr
            in {
                "append",
                "extend",
                "insert",
                "add",
                "update",
            }
        ):
            self.dynamic_memory = True

        self.generic_visit(node)

    # ========================================================
    # MEMORY DETECTION
    # ========================================================

    def visit_ListComp(self, node):
        self.dynamic_memory = True
        self.generic_visit(node)

    def visit_SetComp(self, node):
        self.dynamic_memory = True
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self.dynamic_memory = True
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        self.generic_visit(node)

    # ========================================================
    # RESULT
    # ========================================================

    def get_time_complexity(self):

        # Three or more nested loops
        if self.max_loop_depth >= 3:
            return f"O(n^{self.max_loop_depth})"

        # Two nested loops
        if self.max_loop_depth == 2:
            return "O(n^2)"

        # Loop + sorting
        if (
            self.max_loop_depth == 1
            and self.has_sorting
        ):
            return "O(n log n)"

        # Sorting only
        if self.has_sorting:
            return "O(n log n)"

        # Logarithmic loop
        if (
            self.has_log_loop
            and self.max_loop_depth <= 1
        ):
            return "O(log n)"

        # Single loop
        if self.max_loop_depth == 1:
            return "O(n)"

        return "O(1)"

    def get_space_complexity(self):

        if self.dynamic_memory:
            return "O(n)"

        return "O(1)"


def analyze_complexity(file_path):
    """
    Heuristic static complexity analyzer.

    It estimates common Big-O patterns using Python AST.
    It does not mathematically prove exact complexity.
    """

    path = Path(file_path)

    source = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(source)

    analyzer = ComplexityAnalyzer()

    analyzer.visit(tree)

    return {
        "time_complexity":
            analyzer.get_time_complexity(),

        "space_complexity":
            analyzer.get_space_complexity(),
    }