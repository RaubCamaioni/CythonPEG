import argparse
from pathlib import Path
from cythonpeg.tree2string import cython_string_2_stub
import logging
import glob
from typing import List

logger = logging.getLogger(__name__)


def stub_from_path(path: Path):
    with open(path, "r") as file:
        input_string = file.read()

    stub_file, unparsed_characters = cython_string_2_stub(input_string)

    if len(unparsed_characters):
        logger.warning(f"{path}: {len(unparsed_characters)} unparsed charaters")

    with open(path.with_suffix(".pyi"), "w") as file:
        file.write(stub_file)


def stubs_from_files(arguments: List[str]):
    for argument in arguments:
        paths = glob.glob(argument)
        for path in paths:
            path = Path(path)

            if path.is_file():
                stub_from_path(path)


def entrypoint():
    parser = argparse.ArgumentParser(description="Generate stubs from cython files")
    parser.add_argument("paths", nargs="+", help="File or Directory (wildcards supported)")
    args = parser.parse_args()
    stubs_from_files(args.paths)
