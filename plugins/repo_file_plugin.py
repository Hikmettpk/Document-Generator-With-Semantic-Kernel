# Copyright (c) Microsoft. All rights reserved.

import os
from typing import Annotated
from semantic_kernel.functions import kernel_function

class RepoFilePlugin:
    """A plugin that reads files from this repository."""

    def __init__(self):
        # Projenin kök dizinini belirle
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    @kernel_function(description="Read a file given a relative path to the root of the repository.")
    def read_file_by_path(
        self, path: Annotated[str, "The relative path to the file."]
    ) -> Annotated[str, "Returns the file content."]:
        full_path = os.path.join(self.root_dir, path)

        try:
            with open(full_path) as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File {full_path} not found in repository.")

    @kernel_function(
        description="Read a file given the name of the file. Function will search for the file in the repository."
    )
    def read_file_by_name(
        self, file_name: Annotated[str, "The name of the file."]
    ) -> Annotated[str, "Returns the file content."]:
        for root, dirs, files in os.walk(self.root_dir):
            if file_name in files:
                print(f"Found file {file_name} in {root}.")
                with open(os.path.join(root, file_name)) as file:
                    return file.read()
        raise FileNotFoundError(f"File {file_name} not found in repository.")

    @kernel_function(description="List all files or subdirectories in a directory.")
    def list_directory(
        self, path: Annotated[str, "Path of a directory relative to the root of the repository."]
    ) -> Annotated[str, "Returns a list of files and subdirectories as a string."]:
        full_path = os.path.join(self.root_dir, path)
        try:
            files = os.listdir(full_path)
            return "\n".join(files)
        except FileNotFoundError:
            raise FileNotFoundError(f"Directory {full_path} not found in repository.")