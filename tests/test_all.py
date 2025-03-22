from Cython.Build import cythonize
from pathlib import Path
import cythonpeg
import pytest

files = list((Path(__file__).parent / "cython").glob("*.pyx"))


@pytest.mark.parametrize("file", files)
def test_compile(file):
    """Compiles a Cython file."""
    try:
        cythonize(
            str(file),
            compiler_directives={"language_level": 3},
        )
        print(f"Compile Success: {file}")
        assert True
    except Exception:
        print(f"Compile Failed: {file}")
        assert False


@pytest.mark.parametrize("file", files)
def test_generate_stubs(file):
    """parse all valid cython files: all lines must be parsed"""

    with open(file, mode="r") as f:
        input_string = f.read()

    stub_file, unparsed_characters = cythonpeg.cython_string_2_stub(input_string)

    if len(unparsed_characters) == 0:
        print(f"Parsing Success: {file}")
        assert True
    else:
        print(f"Parsing Failed: {file}\n")
        unparsed_lines = unparsed_characters.split("\n")
        print(f"Unparsed Characters: {len(unparsed_characters)}")
        print(f"Unparsed Lines: {len(unparsed_lines)}\n")
        print(unparsed_characters, end="\n\n")
        assert False


if __name__ == "__main__":
    # runs until first failed assert
    for file in files:
        test_generate_stubs(file)
