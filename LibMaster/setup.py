# -*- coding: utf-8 -*-

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
	Executable('LibMaster.py', base=base)
]

setup(name='LibMaster',
		version='0.3',
		description='A Tool to Combine DPU database and libraries',
		options=options,
		executables=executables
		)