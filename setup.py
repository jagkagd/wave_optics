# -*- coding:utf-8 -*-

import sys
from cx_Freeze import setup, Executable

build_exe_options = {'includes': ['jinja2.ext'], 'include_files': [], 
                    'excludes': ['scipy', 'matplotlib', 'tkinter', 'sympy', 'PySide', 'IPython', 'PyQt4']}


setup(  name = "wave_opt",
        version = "0.2",
        description = "try",
        options = {"build_exe": build_exe_options},
        executables = [Executable("main.py")])
