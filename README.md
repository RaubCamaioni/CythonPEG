# CythonPEG

Description of Cython syntax in pyparsings PEG syntax.  
Allows for the auto generation of cython->python STUB files.  

There are a few assumptions that need to be made when converting from cython to python.  
-How to handle the types that don't exist in python  
-How to hangle syntax that does not exist in python  

Stub files and python type hints can be forgiving.  
Currently types are pulled over verbatim.  
Type hints for function arguments might not work properly depending on the cython type used.  
You will still get function name auto complete, docs, and types that translate.  

I have tested agains my own cython files.  It works to an acceptable level.  
Imports, and other small type changes can be modified manually.  