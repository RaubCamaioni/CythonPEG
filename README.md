# CythonPEG

Description of Cython syntax in pyparsings PEG syntax.  
Allows for the auto generation of cython->python STUB files.  

There are a few assumptions that need to be made when converting from cython to python.  
-How to handle the types that don't exist in python  
    -types are currently pulled verbatim, even if they dont exist in python (pylance handles bad typing pretty well)
-How to hangle syntax that does not exist in python
    -structs are translated to classes (maybe will change to dataclass in the future)

90% of cython files and desired capability from a stub file are present.  
-function and method function name completion   
-doc string stransfer (only tribble quote supported)  

I have tested against my own cython files.  It works to an acceptable level.  
Imports, and other small type changes can be modified manually.  