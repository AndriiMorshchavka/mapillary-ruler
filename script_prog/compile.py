# This program compiles Python script to allow processing by MATLAB

import py_compile
import os
directory = os.path.abspath (__file__)
py_file = os.path.join (directory, r"..//python_script.py")
py_compile.compile (py_file)
print ("Succesfully compiled Python script")