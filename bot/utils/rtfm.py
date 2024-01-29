import json
import re
from typing import Optional
from io import BytesIO
from os import path
from zlib import decompressobj


TARGETS = {
    "aiohttp": "https://docs.aiohttp.org/en/stable",
    "aiosqlite": "https://aiosqlite.omnilib.dev/en/latest",
    "apraw": "https://apraw.readthedocs.io/en/latest",
    "asyncpg": "https://magicstack.github.io/asyncpg/current",
    "discord.py": "https://discordpy.readthedocs.io/en/latest",
    "django": "https://django.readthedocs.io/en/stable",
    "flask": "https://flask.palletsprojects.com/en/3.0.x",
    "imageio": "https://imageio.readthedocs.io/en/stable",
    "matplotlib": "https://matplotlib.org/stable",
    "numpy": "https://numpy.readthedocs.io/en/latest",
    "pandas": "https://pandas.pydata.org/docs",
    "pillow": "https://pillow.readthedocs.io/en/stable",
    "praw": "https://praw.readthedocs.io/en/latest",
    "pygame": "https://www.pygame.org/docs",
    "python": "https://docs.python.org/3",
    "requests": "https://requests.readthedocs.io/en/master",
    "seaborn": "https://seaborn.pydata.org",
    "simplejson": "https://simplejson.readthedocs.io/en/latest",
    "sqlalchemy": "https://docs.sqlalchemy.org/en/20",
    "tensorflow": "https://www.tensorflow.org/api_docs/python",
    "wikipedia": "https://wikipedia.readthedocs.io/en/latest",
}


TARGETS_ALIASES = {
    ("py", "py3", "python3", "python"): "python",
    ("dpy", "discord.py", "discordpy"): "discord.py",
    ("np", "numpy", "num"): "numpy",
    ("pd", "pandas", "panda"): "pandas",
    ("pillow", "pil"): "pillow",
    ("imageio", "imgio", "img"): "imageio",
    ("requests", "req"): "requests",
    ("aiohttp", "http"): "aiohttp",
    ("django", "dj"): "django",
    ("flask", "fl"): "flask",
    ("reddit", "praw", "pr"): "praw",
    ("asyncpraw", "apraw", "apr"): "apraw",
    ("asyncpg", "pg"): "asyncpg",
    ("aiosqlite", "sqlite", "sqlite3", "sqli"): "aiosqlite",
    ("sqlalchemy", "sql", "alchemy", "alchem"): "sqlalchemy",
    ("tensorflow", "tf"): "tensorflow",
    ("matplotlib", "mpl", "plt"): "matplotlib",
    ("seaborn", "sea"): "seaborn",
    ("pygame", "pyg", "game"): "pygame",
    ("simplejson", "sjson", "json"): "simplejson",
    ("wiki", "wikipedia"): "wikipedia",
}

class WpilibRFTM:
    API_REFERENCE = "https://github.wpilib.org/allwpilib/docs/release/java/edu/wpi/first"
    CLASS_ENDING = "package-summary"
    ENDING = ".html"

    def __init__(self, json_file_path: str):
        with open(json_file_path, 'r') as file:
            self.wpi_first = json.load(file)

    @staticmethod
    def parse(subclass: str) -> str:
        if '.' in subclass:
            subclass = subclass.replace('.', '/')
        return subclass

    def build(self, classes: Optional[str] = None, subclass: Optional[str] = None, term: Optional[str] = None) -> str:
        if classes is None:
            return "https://github.wpilib.org/allwpilib/docs/release/java/"

        base_url = f"{self.API_REFERENCE}/{classes.lower()}"

        if subclass:
            subclass = self.parse(subclass.lower())
            base_url += f"/{subclass}/{term or self.CLASS_ENDING}"
        else:
            base_url += f"/{term or self.CLASS_ENDING}"

        return f"{base_url}{self.ENDING}"
    
    @staticmethod
    def format_query(query: dict):
        return "".join(f"[`{x}`]({y})\n" for x,y in query.items())
    

    def search_terms(self, term: str) -> str:
        def search_recursive(subdict: dict, current_path: list, term: str):
            results = {}
            stack = [(subdict, [])]

            for key, value in subdict.items():
                if term.lower() == str(key).lower():
                    results[f"edu.wpi.first.{key}"] = self.build(key)
                if isinstance(value, dict):
                    for x, _ in value.items():
                        if term.lower() in str(x).lower() and x != "classes":
                            results[f"edu.wpi.first.{key}.{x}"] = self.build(key, x)

            while stack:
                current_subdict, current_path = stack.pop()

                if isinstance(current_subdict, dict):
                    for key, value in current_subdict.items():
                        new_path = current_path + [key]
                        stack.append((value, new_path))
                elif isinstance(current_subdict, list):
                    for index, item in enumerate(current_subdict):
                        new_path = current_path + [index]
                        stack.append((item, new_path))
                elif term.lower() in str(current_subdict).lower():
                    current_path.remove("classes")
                    if len(current_path) == 3:
                        results[
                            f"edu.wpi.first.{current_path[0]}.{current_path[1]}.{str(subdict[current_path[0]][current_path[1]]["classes"][current_path[2]])}"
                        ] = self.build(
                                classes=current_path[0], 
                                subclass=current_path[1],
                                term=subdict[current_path[0]][current_path[1]]["classes"][current_path[2]]
                            )
                    elif len(current_path) == 2:
                        results[
                            f"edu.wpi.first.{current_path[0]}.{str(subdict[current_path[0]]['classes'][current_path[1]])}"
                        ] = self.build(
                            classes=current_path[0],
                            term=subdict[current_path[0]]['classes'][current_path[1]]
                        )
                    elif len(current_path) == 1:
                        results[f"edu.wpi.first.{current_path[0]}"] = self.build(classes=current_path[0])

            return results

        return self.format_query(search_recursive(self.wpi_first, [], term))

# Directly taken from Rapptz/RoboDanny
# https://github.com/Rapptz/RoboDanny/blob/715a5cf8545b94d61823f62db484be4fac1c95b1/cogs/api.py
# This code is under the Mozilla Public License 2.0

class SphinxObjectFileReader:
    # Inspired by Sphinx's InventoryFileReader
    BUFSIZE = 16 * 1024

    def __init__(self, buffer):
        self.stream = BytesIO(buffer)

    def readline(self):
        return self.stream.readline().decode("utf-8")

    def skipline(self):
        self.stream.readline()

    def read_compressed_chunks(self):
        decompressor = decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self):
        buf = b""
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b"\n")
            while pos != -1:
                yield buf[:pos].decode("utf-8")
                buf = buf[pos + 1 :]
                pos = buf.find(b"\n")

    def parse_object_inv(self, url):
        # key: URL
        # n.b.: key doesn't have `discord` or `discord.ext.commands` namespaces
        result = {}

        # first line is version info
        inv_version = self.readline().rstrip()

        if inv_version != "# Sphinx inventory version 2":
            raise RuntimeError("Invalid objects.inv file version.")

        # next line is "# Project: <name>"
        # then after that is "# Version: <version>"
        projname = self.readline().rstrip()[11:]
        version = self.readline().rstrip()[11:]

        # next line says if it's a zlib header
        line = self.readline()
        if "zlib" not in line:
            raise RuntimeError("Invalid objects.inv file, not z-lib compatible.")

        # This code mostly comes from the Sphinx repository.
        entry_regex = re.compile(r"(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)")
        for line in self.read_compressed_lines():
            match = entry_regex.match(line.rstrip())
            if not match:
                continue

            name, directive, prio, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(":")
            if directive == "py:module" and name in result:
                # From the Sphinx Repository:
                # due to a bug in 1.1 and below,
                # two inventory entries are created
                # for Python modules, and the first
                # one is correct
                continue

            # Most documentation pages have a label
            if directive == "std:doc":
                subdirective = "label"

            if location.endswith("$"):
                location = location[:-1] + name

            key = name if dispname == "-" else dispname
            prefix = f"{subdirective}:" if domain == "std" else ""

            if projname == "discord.py":
                key = key.replace("discord.ext.commands.", "").replace("discord.", "")

            result[f"{prefix}{key}"] = path.join(url, location)

        return result