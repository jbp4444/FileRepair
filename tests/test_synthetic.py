#!/usr/bin/python
#
# (C) 2015-2016, John Pormann, Duke University, jbp1@duke.edu
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

#
# synthetic tests for filerepair tools
#

import os
import glob
import unittest
import subprocess

import filerepair.filerepair as filerepair
import filerepair.utils as utils

# get list of files from subdir
test_path = os.path.dirname(os.path.abspath(__file__)) + "/syn_files"
#print test_path
files_to_test = glob.glob( test_path + "/*.dat" )
#print files_to_test

class SyntheticTests( unittest.TestCase ):

	#
	# prep'ing for when we have real-world examples
	# : these files should fail
	def test_syn_shouldfail(self):
		#print
		rtn = 0

		for infile in files_to_test:
			#print( "verify known failure ["+os.path.basename(infile)+"]" )
			chkfile = infile + ".fr"
			badfile = infile + ".bad"
			repfile = badfile + ".rep"

			opts = utils.DefaultOpts()

			err = filerepair.verify_file( badfile, chkfile, opts )
			if( err == 0 ):
				rtn = rtn + 1

		self.assertEqual( rtn, 0 )

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == '__main__':
	unittest.main()
