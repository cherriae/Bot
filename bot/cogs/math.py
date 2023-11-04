from __future__ import annotations

import discord
import re
from discord.ext import commands

from ..utils import Bot, EquationSolver, CartesianGraph, fibonacci


class MathCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self._solver = EquationSolver()
        self.pattern = r'(-?\d+)x[+](-?\d+)y[=](-?\d+)'

    @property
    def solver(self):
        return self._solver

    @commands.command(name='fibonacci', aliases=['fib', 'fibon'],
                      description="Returns the value for fibonacci sequences")
    async def _fibonacci(self, ctx, n: int):
        result = fibonacci(n)
        if len(str(result)) > 3990:
            return await ctx.send("Too much can't show all of it here sorry")
        await ctx.send(f"```py\n{result}\n```")

    @commands.command(name="graph", aliases=["graphing"],
                      description="Returns a cartesian graph for the inputted graph")
    async def _graph(self, ctx, equation: str, x_min: int = -10, x_max: int = 10,
                     y_min: int = -10, y_max: int = 10, ticks: int = 1):
        graph = CartesianGraph()
        graph.axes(x_min, x_max, y_min, y_max, ticks)

        eq = graph.create_function_from_string(equation)

        graph.plot(eq)

        await ctx.send(file=discord.File('./bot/ext/images/graph.png'))

    @commands.group(name="solve", aliases=['s'], description="Solve an algebraic equation", invoke_without_command=True)
    async def _solve(self, ctx: commands.Context, *, equation: str):
        equation = equation.replace('^', '**')
        answer = self.solver.solve_polynomial(equation, self.solver.x)
        await ctx.send(answer)

    @_solve.command(name="system", aliases=['sys', 'matrix', 'matrices'])
    async def _system(self, ctx, equation1: str, equation2: str):
        equations = [equation1, equation2]

        coefficents, constants = self.solver.equations_to_lists(equations)
        solutions = self.solver.system(coefficents, constants)
        await ctx.send(f"X: {solutions[0]}\nY: {solutions[1]}")


async def setup(bot: Bot):
    await bot.add_cog(MathCog(bot))
