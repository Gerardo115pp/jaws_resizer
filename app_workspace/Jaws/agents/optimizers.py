from Jaws.helpers.fs_utils import IsDirectory, DirectorySize, GetUniqueFilename, ReplaceFileExtension
from Jaws.helpers import isFileSupported
from Jaws.helpers.human_readable import sizeToHumanReadable
from Jaws.helpers.image_utils import getImageWidth
from dataclasses import dataclass
from PIL import Image, UnidentifiedImageError
import multiprocessing
from multiprocessing.managers import ValueProxy
from io import BytesIO
import traceback
import subprocess
import pathlib
import os
import re 

agent_manager = multiprocessing.Manager()
agent_manager.Value

class JawsOptimizer:
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

@dataclass    
class JawsShrinkerParams:
    resize_width: int 
    processed_files: ValueProxy[int]
    processed_directories: ValueProxy[int]
    directory_min_size: int = 1024**3 # 1GB
    keep_original: bool = False
    dry_run: bool = False
    image_format: str = "webp"
    directory_limit: int = -1
    thread_count: int = 2
    verbose: bool = False

class JawsShrinker:
    """From a given directory, finds all directries that have a total content size larger than options.directory_min_size and
    scans those directories for images. Then resizes the images to the width specified in options.resize_width. If options.keep_original
    is  false, then it destroys any processed image after generating the resized version. call .scan() to fill the matching directories and
    .traverse() to start the shrinking process.
    """
    
    def __init__(self, root_path: str, options: JawsShrinkerParams) -> None:
        self.root_directory_path:str = root_path
        self.options: JawsShrinkerParams = options 
        self.matching_directories: list[str] = []
        
        self.processed_files = options.processed_files
        self.processed_directories = options.processed_directories

        if not IsDirectory(root_path):
            raise NotADirectoryError(f"'{root_path}' does not exist or is not a directory")

    @property
    def DirectoryPath(self) -> str:
        """The path from where the directory scanning will start. 

        Returns:
            str: the path
        """
        return self.root_directory_path

    @property
    def DirectoryMinSize(self) -> int:
        """The minimum size in bytes a directorie's content must met to be subjected to the shrinking process. 

        Returns:
            int: the byte size
        """
        return self.options.directory_min_size

    @property
    def DryRun(self) -> bool:
        """If true, no operations that alter the file system will be performed.

        Returns:
            bool: true if dry run
        """

        return self.options.dry_run

    def composeSingleFileMagickCommand(self, file_path: str) -> list[str]:
        """Generates an magick command suited to resize a single image into the target format.

        Args:
            file_path (str): the path to the image file. The output file will be based on

        Returns:
            list[str]: _description_
        """

        output_file: str = ReplaceFileExtension(file_path, self.TargetFormat)
        output_file = GetUniqueFilename(output_file) # If it doesn't exist, return immediately.

        resize_str: str = f"{self.ResizeWidth}x"
        
        command: list[str] = [
            "magick", "convert",
            file_path,
            "-resize", resize_str,
            "-quality", "75",
            "-strip",
        ]

        if self.TargetFormat == "webp":
            webp_optimizations: list[str] = [
                "-define", "webp:method=4",
                "-define", "webp:thread-level=1",
            ]

            command.extend(webp_optimizations)
            
        command.append(output_file)
        
        return command

    def handlePathWalkErrors(self, error: OSError):
        """Handles errors generated by pathlib.Path.walk by printing them
        if VerboseExecution is true.

        Args:
            error (OSError): the error produced
        """
        if self.VerboseExecution:
            print(f"Error walking path: {error.strerror}")

    @property
    def KeepOriginal(self) -> bool:
        """If not true, the original images will be destroyed after resizing.
        """
        
        return self.options.keep_original

    @KeepOriginal.setter
    def KeepOriginal(self, value: bool):
        self.options.keep_original = value

    @property
    def Limit(self) -> int:
        """The maximum number of directories to scan. If not set, all directories will be scanned.

        Returns:
            int: the limit
        """
        return self.options.directory_limit

    @property
    def MatchingDirectories(self) -> list:
        """The matching directories that met the size criteria. It containes a list of paths relative to the passed root directory.

        Returns:
            list: a list of relative paths
        """
        return self.matching_directories

    def processImageFile(self, file_path: str):
        """Resizes the image file to the width specified in the options.

        Args:
            file_path (str): the path to the image file
        """
        try: 
            image_width = getImageWidth(file_path)
        except UnidentifiedImageError as e:
            print(f"Could not identify image '{file_path}'")
            return
        
        if image_width <= (self.ResizeWidth * 1.3):
            print(f"Skipping '{file_path}' as it's width is less than {self.ResizeWidth}px")
            return
        
        command: list[str] = self.composeSingleFileMagickCommand(file_path)
        if not self.DryRun:
            try:
                stderr_readable, stderr_writable = os.pipe()
                subprocess.run(command, cwd=self.root_directory_path, stderr=stderr_writable, check=True)
                print(f"Executed: {' '.join(command)}")
                
                if not self.KeepOriginal:
                    os.remove(file_path)
                
                os.close(stderr_writable)
                os.close(stderr_readable)
            except subprocess.CalledProcessError as e:
                
                os.close(stderr_writable)
                with os.fdopen(stderr_readable) as stderr:
                    stderr_output: str = stderr.read()
                    
                traceback.print_exc()
                print(f"{stderr_output}\nError resizing image '{file_path}'")
                return

        if self.DryRun:
            print(f"Would execute: {' '.join(command)}")
            if not self.KeepOriginal:
                print(f"Would remove '{file_path}'")
        
    def scan(self):
        """Scans the directory and fills the MatchingDirectories list with the directories that met the size criteria.
        """
        if self.Limit == 0:
            return

        self.matching_directories.clear()

        directories_matched: int = 0
        directories_scanned: int = 0
        
        for directory in os.scandir(self.root_directory_path):
            if not directory.is_dir():
                continue
            
            directories_scanned += 1
            
            directory_size: int = DirectorySize(directory.path)
            if self.VerboseExecution:
                print(f"Scanning directory '{directory.path}' {sizeToHumanReadable(directory_size)}")

            if directory_size > self.DirectoryMinSize:
                self.matching_directories.append(directory.path)
                hr_size: str = sizeToHumanReadable(directory_size)
                directories_matched += 1
                print(f"Directory '{directory.path}' matches the size<{hr_size}> criteria")
            
            if directories_matched >= self.Limit and self.Limit > 0:
                break

        if self.VerboseExecution:
            print(f"Scanned {directories_scanned} directories.\nMatched {directories_matched} directories")
        
        return

    @property
    def ResizeWidth(self) -> int:
        """The size images found within the directory will be resized to. this just represents the width as aspect ratio will 
        always be preserved.

        Returns:
            int: the width in pixels
        """
        return self.options.resize_width

    def workerProcess(self, directory: str):
        """A worker handler for the multiprocessing pool. to distribute the work of processing directories.

        Args:
            directory (str): the directory to process
        """
        total_matches: int = len(self.MatchingDirectories)
        
        print(f"\n\n{'='*20}Processing directory '{directory}' ({self.processed_directories.value+1}/{total_matches}){'='*20}\n")

        self.walkDirectory(directory)
        self.processed_directories.value += 1

    def traverse(self):
        """Traverses the matching directories applying the shrinking process to the images found within.
        On a dry run, no operations are performed just logged.
        """

        total_matches: int = len(self.MatchingDirectories)

        print(f"Processing {total_matches} directories")

        with multiprocessing.Pool(self.ThreadCount) as pool:
            pool.map(self.workerProcess, self.MatchingDirectories)

        return

    @property
    def TargetFormat(self) -> str:
        """The format the resized images will be saved in.

        Returns:
            str: the format
        """
        return self.options.image_format

    @property
    def ThreadCount(self) -> int:
        """The number of threads to use when processing directories.

        Returns:
            int: the thread count
        """
        return self.options.thread_count
    
    @property
    def VerboseExecution(self) -> bool:
        """If true, the agent will log more information about it's execution.

        Returns:
            bool: true if verbose
        """
        return self.options.verbose

    def walkDirectory(self, directory_path: str):
        """Uses pathlib.Path.walk to traverse the directory and it's subdirectories.
        Processing any supported files it finds.
        """
        
        current_path: pathlib.Path = pathlib.Path(directory_path)

        
        for root, dirs, files in current_path.walk(on_error=self.handlePathWalkErrors):

            iter_processed_files: int = 0

            try:
                for file in files:
                    
                    file_path: str = os.path.join(root, file)
                    
                    if not isFileSupported(file_path):
                        if self.VerboseExecution:
                            print(f"Ignoring unsupported file '{file_path}'")
                        continue
                    print(f"{iter_processed_files} -- {self.processed_files.value} Processing '{file_path}'\n")
                    self.processImageFile(file_path)
                    
                    iter_processed_files += 1
                    self.processed_files.value += 1
                    
            except FileNotFoundError as e:
                self.handlePathWalkErrors(e)
                continue
            
            if self.VerboseExecution:
                print(f"Processed {iter_processed_files} files on '{root}'\n\n{'-'*20}")
        return