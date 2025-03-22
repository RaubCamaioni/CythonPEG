from Cython.Build import cythonize
from pathlib import Path
import cythonpeg
import pytest
import ast


def partial_type(type_str: str) -> str:
    if "float" in type_str:
        return "float"
    elif "int" in type_str:
        return "int"
    elif "bint" in type_str:
        return "bool"
    else:
        return type_str


def complete_type(type_str: str) -> str:
    if ":" in type_str:
        return "np.ndarray"
    else:
        return type_str


cythonpeg.set_type_converter_partial(partial_type)
cythonpeg.set_type_converter_complete(complete_type)


def _glob(extention: str):
    return (Path(__file__).parent / "cython").glob(extention)


@pytest.mark.parametrize("file", _glob("*.pyx"))
def test_compile(file: Path):
    try:
        cythonize(
            str(file),
            compiler_directives={"language_level": 3},
        )
    except Exception:
        pytest.fail(f"compilation failed: {file}")


@pytest.mark.parametrize("file", _glob("*.pyx"))
def test_generate_stubs(file: Path):
    with open(file, mode="r") as f:
        input_string = f.read()

    stub_file, unparsed_characters = cythonpeg.cython_string_2_stub(input_string)

    if len(unparsed_characters) == 0:
        with open(file.with_suffix(".pyi"), "w") as f:
            f.write(stub_file)
    else:
        pytest.fail(f"Unparsed Characters: {len(unparsed_characters)}")


@pytest.mark.parametrize("file", _glob("*.pyi"))
def test_python_valid(file: Path):
    try:
        with open(file, "r", encoding="utf-8") as f:
            ast.parse(f.read())
    except SyntaxError as e:
        pytest.fail(f"SyntaxError in {file}: {e}")
    except Exception as e:
        pytest.fail(f"Exception in {file}: {e}")


if __name__ == "__main__":
    # runs until first failed assert
    for file in (Path(__file__).parent / "cython").glob("*.pyi"):
        test_python_valid(file)
