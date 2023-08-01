# CythonPEG
Description of Cython syntax in pyparsings PEG syntax.  
Allows for the auto generation of cython -> python STUB files.  

There are a few assumptions that need to be made when converting from cython to python.  
-How to handle types that don't exist in python?  
&emsp;-by default type are pulled verbatim, even if they don't exist in python  
&emsp;-type handling can be customized with provided setter functions  
-How to handle syntax that does not exist in python?  
&emsp;-structs are translated to classes

# Why generate stub files?
Most langauge servers don't understand cython code.  

By including STUB files with your cython compiled module you maintain:  
-module, function, class, method auto completion  
-argument names/number and type hinting  
-doc strings  

# Colab notebook to test code
https://colab.research.google.com/drive/1KvSUznOoeJ_F8GxzA9IafbMXA6mTR_Nj?usp=sharing

# Customize you type conversions
Customizable conversions between cython and python types.  
Use the setter function provided to change the type conversion function.  
An example is given inside "usage/examples.ipynb"

# How do I use this repo?
All the parsing code is contained inside the file "cython_peg.py".  
Copy that file into your project and create a simple python script for creating the stub files.  
Add the stub generation script into your cython setup.py file.

```python
from pathlib import Path
import cython_peg as cp

# set indent used in stub file
cp.set_indent("  ")

for file in Path(r"module_directory").glob("*.pyx"):

    with open(file, mode='r') as f:
        cython_tokens = f.read()

    print(f"Parsing File: {file}")
    stub_file, unparsed_tokens = cp.cython_string_2_stub(cython_tokens)
    print(f"Percentage Parsed: {1 - len(unparsed_tokens)/len(cython_tokens)}")

    with open(file.with_suffix(".pyi"), mode='w') as f:
        f.write(stub_file)
```

# Issues
The entirety of the cython syntax is not captured in cython_peg.py.  
If the cython syntax is unknown/invalid the syntax will not be parsed and will appear in the "unparsed tokens" return.  
The percentage of parsing can be calculated and used as an indication of parsing issues.  

If the parser fails, post an issue with the code that caused an issue.  
Learn pyparsing syntax at: https://pyparsing-docs.readthedocs.io/en/latest/index.html  
