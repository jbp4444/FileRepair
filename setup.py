#!/usr/bin/python
#
# (C) 2015-2020, John Pormann, Duke University, jbp1@duke.edu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#	The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from setuptools import setup

def readme():
	with open('README.md') as f:
		return f.read()

setup(name='filerepair',
	version='0.4.2',
	description='Suite of tools for repairing bit-damaged files',
	long_description=readme(),
	url='https://github.com/jbp4444/FileRepair',
	author='John Pormann',
	author_email='jbp1@duke.edu',
	license='MIT',
	packages=['filerepair'],
	scripts=[ 'bin/showbits.py', 'bin/maketest.py', 'bin/makemockup.py' ],
	entry_points = {
		'console_scripts': ['filerepair=filerepair.cmd_filerepair:main',
			'adderror=filerepair.cmd_adderror:main',
			'basicrepair=filerepair.cmd_basicrepair:main' ],
	},
	test_suite="filerepair.tests",
	include_package_data=True,
	zip_safe=False )
