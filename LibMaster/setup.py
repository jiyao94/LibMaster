# -*- coding: utf-8 -*-

# A simple setup script to create an executable using PyQt5. This also
# demonstrates the method for creating a Windows executable that does not have
# an associated console.
#
# PyQt5app.py is a very simple type of PyQt5 application
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
	base = 'Win32GUI'

options = {
	'build_exe': {
		'includes': ['pyforms.settings', 'pyforms.gui.settings', 'numpy.lib.format',
					'numpy.core._methods', 'pyreadline.release']
	}
}

executables = [
	Executable('OptimumS.py', base=base)
]

setup(name='OptimumS',
		version='0.1',
		description='A Tool to Combine DPU database and libraries',
		options=options,
		executables=executables
		)