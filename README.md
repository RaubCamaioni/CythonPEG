## CythonPEG
Description of Cython syntax in pyparsings PEG syntax.  
Allows for the auto generation of cython -> python STUB files.  

There are a few assumptions that need to be made when converting from cython to python.  
-How to handle types that don't exist in python?  
&emsp;-by default type are pulled verbatim, even if they don't exist in python  
&emsp;-type handling can be customized with provided setter functions  
-How to handle syntax that does not exist in python?  
&emsp;-structs are translated to classes

## Why generate stub files?
Most langauge servers don't understand cython code.  

By including STUB files with your cython compiled module you maintain:  
-module, function, class, method auto completion  
-argument names/number and type hinting  
-doc strings  

## Customize your type conversions
Customizable conversions between cython and python types.  
Use the setter function provided to change the type conversion function.  
An example is given inside "usage/examples.ipynb"

## How do I use this repo?

The cythonpeg package installs a cli utility for generting stub files.  
It will create a .pyi file for each .pyx file, overwriting older .pyi files.  

```bash
pip install https://github.com/RaubCamaioni/CythonPEG.git
cythonpeg ./my_cython_files/*.pyx
```

## Issues
The entirety of the cython syntax is not captured in cythonpeg.py.  
If the cython syntax is unknown/invalid the syntax will not be parsed and will appear in the "unparsed tokens" return.  
The percentage of parsing can be calculated and used as an indication of parsing issues.  

If the parser fails, post an issue with code that reproduces the error.  
Learn pyparsing syntax at: https://pyparsing-docs.readthedocs.io/en/latest/index.html  
