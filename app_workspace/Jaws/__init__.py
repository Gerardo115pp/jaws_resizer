from .agents.optimizers import JawsShrinkerParams, JawsShrinker, agent_manager
from .helpers.human_readable import humanSizeToByteSize, humanTime
from .agents.optimizers import JawsOptimizer
from time import time
import traceback
import click

"""
    for development install do: pip install -e .
"""

@click.group()
def cli():
    pass
    
    
@cli.command("jdir", help="Runs in a single directory, finding all image files within it and creates several versions of different sizes prefixed in webp format")
@click.argument("path")
def jdir(path):
    traverser = JawsOptimizer(path)
    traverser.traverse()
    print("Done")

@cli.command("chew_dir", help="scans a directory for subdirectories larger than --min-dir-size and down scales the images found inside")
@click.argument("path")
@click.option("--min-dir-size", "-s", default="1GB", help="The minimum size of the directory to scan.(default 1GB)")
@click.option("--dry-run", "-d", is_flag=True, help="Do not perform any operations, just print what would be done")
@click.option("--keep-original", "-k", is_flag=True, help="Keep the original image after resizing.")
@click.option("--resize-width", "-w", default=980, help="The width of the resized image. Aspect ratio is maintained")
@click.option("--image-format", "-c", default="webp", help="The encoding format for resized images.(default webp)")
@click.option("--limit", "-l", default=-1, help="The maximum number of directories to scan. if not set, all directories will be scanned")
@click.option("--verbose", "-v", is_flag=True, help="Prints more information")
@click.option("--threads", "-t", default=2, help="The number of threads to process directories")
def chew_dir(path, min_dir_size, dry_run, keep_original, resize_width, image_format, limit, verbose, threads):
    print(f"Chewing {path} with min-dir-size {min_dir_size}")
    min_size = 0;

    try: 
        min_size = humanSizeToByteSize(min_dir_size)
    except ValueError as e:
        print(f"Invalid size '{min_dir_size}' passed on --min-dir-size")
        return
    
    jaws_shrinker_options = JawsShrinkerParams(
        resize_width=resize_width,
        directory_min_size=min_size,
        keep_original=keep_original,
        dry_run=dry_run,
        image_format=image_format,
        directory_limit=limit,
        thread_count=threads,
        verbose=verbose,
        processed_files=agent_manager.Value('i', 0),
        processed_directories=agent_manager.Value('i', 0),
    )

    jaws_agent = JawsShrinker(path, jaws_shrinker_options)

    profiling_time = time()
    
    try: 
        jaws_agent.scan()
        jaws_agent.traverse()
    except Exception as e:
        traceback.print_exc()
        print(f"Jaws encountered an error from which it could not recover: {e}")
        return
    
    profiling_time = time() - profiling_time
    
    print(f"Chewing took {humanTime(profiling_time)}")
    
    
    