import click
from .agents.traversers import JawsOptimizer

"""
    for development install do: pip install -e .
"""

@click.group()
def cli():
    pass
    
    
@cli.command("jdir")
@click.argument("path")
def jdir(path):
    traverser = JawsOptimizer(path)
    traverser.traverse()
    print("Done")