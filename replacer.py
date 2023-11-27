import jinja2 as jj
import toml
import sys

proj = toml.load("pyproject.toml")
t = jj.Environment(loader=jj.FileSystemLoader(".")).from_string(sys.stdin.read())
print(t.render(**proj))
