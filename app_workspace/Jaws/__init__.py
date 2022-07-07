import click
import os
import subprocess
import pathlib
import re 
from PIL import Image
"""
    for development install do: pip install -e .
"""

class JawsTraverser:
    def __init__(self, path):
        self.path = path
        assert os.path.exists(path), "Path does not exist"
        
        self.files = []
        self.__current_depth = 0
        self.candiates_regex = re.compile(r".+\.(png|jpg|jpeg)$")
        assert self.candiates_regex.match("test.png"), "Regex does not match"
        assert not self.candiates_regex.match(".png"), "Regex is too broad"
        
        self.sizes = {
            "XL": 2300,
            "L": 1300,
            "M": 600,
            "S": 400
        }
        
        
    def optimize(self, file_name: str):
        image_obj = Image.open(file_name)
        image_width = image_obj.width
        image_obj.close()
        
        file_name_without_extension = os.path.splitext(file_name)[0]
        subprocess.run(["convert", file_name, f"{file_name_without_extension}-original.webp"])

        for size, size_width in self.sizes.items():
            if image_width > size_width:
                convertion_process = ["convert", file_name, "-resize", f"{size_width}x", f"{file_name_without_extension}-{size}.webp"]
                complete = subprocess.run(convertion_process)
                print(f"{file_name} resized to {size_width}x: {'Success' if complete.returncode == 0 else 'Failed'}")
        
        os.remove(file_name)
        return

    
    def traverse(self, current_path:str = None):
        current_path = current_path or self.path
        for file in os.scandir(current_path):
            file_path = os.path.join(current_path, file.name)
            if file.is_dir():
                
                self.__current_depth += 1
                self.traverse(file_path)
                self.__current_depth -= 1
                
            elif self.candiates_regex.match(file.name):
                print(f"{(self.__current_depth+1)*' '}Optimizing {file_path}")
                assert os.path.exists(file_path), f"'{file_path}' does not exist"
                self.optimize(file_path)
                pass
            else:
                print(f"{(self.__current_depth+1)*' '}Ignoring {file_path}")

    @property
    def Files(self):
        return self.files


@click.group()
def cli():
    pass
    
    
@cli.command("jdir")
@click.argument("path")
def jdir(path):
    traverser = JawsTraverser(path)
    traverser.traverse()
    print("Done")