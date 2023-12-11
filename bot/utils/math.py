from __future__ import annotations

import re
import ast
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

from typing import Optional, Callable


class CartesianGraph:
    """CartesianGraph

    This code defines a CartesianGraph class for plotting 2D graphs on a cartesian coordinate system. It initializes
    a matplotlib figure and axes, defines default ranges and ticks, and provides methods to configure the axes and
    plot functions.
    """
    X_MIN = -5
    X_MAX = 5
    Y_MIN = -5
    Y_MAX = 5

    TICKS = 1

    def __init__(self):
        self._fig, self._ax = plt.subplots(figsize=(10, 10))
        self.fig.patch.set_facecolor('#ffffff')

    @staticmethod
    def create_function_from_string(function: str):
        """Convert string to function

        Takes in a str (e.g. x**2) and return a function

        Args:
            function: The inputted string function

        Returns:
            The function used for CartesianGraph.plot
        """

        def dynamic_function(x): #TODO: Fix this vunerablitiy
            local_vars = {'x': x}
            exec(f"result = {function}", globals(), local_vars)
            return local_vars['result']
        return dynamic_function

    @property
    def fig(self):
        return self._fig

    @property
    def ax(self):
        return self._ax

    def axes(self, x_min: Optional[int] = X_MIN, x_max: Optional[int] = X_MAX, y_min: Optional[int] = Y_MIN,
             y_max: Optional[int] = Y_MAX,
             ticks: Optional[int] = TICKS):
        """Configures the plot axes.

        Sets the x and y axis limits, removes spines, adds gridlines,
        labels, and ticks based on the provided optional parameters.

        Default values are used for any parameters not provided.

        Args:
           x_min: Optional minimum x value.
           x_max: Optional maximum x value.
           y_min: Optional minimum y value.
           y_max: Optional maximum y value.
           ticks: Optional tick interval.

        Returns:
           None. Modifies the axes of the plot in place.
        """

        self.ax.set(xlim=(x_min - 1, x_max + 1), ylim=(y_min - 1, y_max + 1), aspect='equal')

        self.ax.spines['bottom'].set_position('zero')
        self.ax.spines['left'].set_position('zero')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        self.ax.set_xlabel('$x$', size=14, labelpad=-24, x=1.02)
        self.ax.set_ylabel('$y$', size=14, labelpad=-21, y=1.02, rotation=0)

        x_ticks = np.arange(x_min, x_max + 1, ticks)
        y_ticks = np.arange(y_min, y_max + 1, ticks)
        self.ax.set_xticks(x_ticks[x_ticks != 0])
        self.ax.set_yticks(y_ticks[y_ticks != 0])
        self.ax.set_xticks(np.arange(x_min, x_max + 1), minor=True)
        self.ax.set_yticks(np.arange(y_min, y_max + 1), minor=True)

        self.ax.grid(which='both', color='blue', linewidth=1, linestyle='-', alpha=0.2)

    @staticmethod
    def plot(y: Callable, filename: Optional[str] = "graph.png", domain_start: int = -10, domain_end: int = 10):
        """Plots a function and saves the plot to a file.

        Args:
            y: The function to plot.
            filename: The name of the file to save the plot to.

        Returns:
            True if the plot was successfully saved, otherwise raises the error.

        """

        x = np.linspace(domain_start, domain_end, 100)
        plt.plot(x, y(x), 'b', linewidth=2)
        try:
            plt.savefig(f"./bot/ext/images/{filename}")

            plt.close()
            return True
        except Exception as e:
            raise e


class EquationSolver:
    """Provides methods for solving equations.

    The EquationSolver initializes symbols for variables x, y, z.

    It contains methods to solve polynomial equations and matrix equations.

    The solve_polynomial method solves a single polynomial equation for a
    specified variable.

    The solve_matrix_equation method solves a system of linear equations
    given the coefficients and constants matrices.

    """

    def __init__(self):
        self.variables = sp.symbols('x y')
        self.x, self.y = self.variables

    @staticmethod
    def equations_to_lists(equations):
        coefficients = []
        constants = []

        for equation in equations:
            # Split the equation into left and right sides
            sides = equation.split('=')

            equation_coeffs = []
            equation_consts = 0

            for side in sides:
                terms = side.split('+')
                for term in terms:
                    if term := term.strip():
                        if match := re.match(r'([-+]?\d*)[ ]*([a-zA-Z]*)', term):
                            coeff_str, var = match.groups()
                            coeff = int(coeff_str) if coeff_str else 1
                            if var:
                                equation_coeffs.append(coeff)
                            else:
                                equation_consts += coeff

            coefficients.append(equation_coeffs)
            constants.append(equation_consts)

        return coefficients, constants

    @staticmethod
    def polynomial_to_string(expression):
        terms = expression.split('+')
        result = ''
        for term in terms:
            term = term.strip() if '-' in term else term.strip('+')
            result += f'{term} * solver.x '
        return result

    @staticmethod
    def solve_polynomial(equation, variable_to_solve_for):
        """Solves a polynomial equation for a specified variable.

        Args:
            equation: The polynomial equation to solve.
            variable_to_solve_for: The variable to solve the equation for.

        Returns:
            The value(s) of the variable that satisfy the equation.
        """
        parsed_equation = sp.parse_expr(equation)
        return sp.solve(parsed_equation, variable_to_solve_for)

    @staticmethod
    def system(coefficients: list, constants: list):
        A = np.array(coefficients)
        B = np.array(constants)
        return np.linalg.solve(A, B)


def fibonacci(n: int):
    """Generates the Fibonacci sequence up to n terms.

    The Fibonacci sequence starts with 0 and 1, and each subsequent number is the
    sum of the previous two. This function generates the sequence up to the nth term.

    Args:
        n: The number of terms to generate.

    Returns:
        A list containing the Fibonacci sequence up to the nth term.

    """

    fib_sequence = [0, 1]
    while len(fib_sequence) < n:
        next_number = fib_sequence[-1] + fib_sequence[-2]
        fib_sequence.append(next_number)
    return fib_sequence


