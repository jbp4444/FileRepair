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
# tests of cmdline options for filerepair tools
#

import unittest
import subprocess

# import filerepair.filerepair as filerepair
import filerepair
# import filerepair.utils as utils
# import filerepair.adderror as adderror

# some simple constants
KB = 1024
MB = 1024*1024
GB = 1024*1024*1024

class basicTests( unittest.TestCase ):

	def test_basics(self):
		rtn = 0
		sz = 1*MB

		infile = "testfile_" + str(sz)
		chkfile = infile + ".fr"
		badfile = infile + "_bad"
		badchkfile = badfile + ".fr"
		repfile = badfile + ".rep"

		subprocess.call( [ "bin/maketest.py", "-r", "-n", str(sz), infile ] )
		err = adderror.add_errors_to_file( infile, badfile )

		opts = filerepair.utils.DefaultOpts()

		for nparity in [ 1,2,4 ]:
			opts['num_parity_disks'] = nparity

			for bsize in [ 1*KB,2*KB,4*KB ]:
				opts['block_size'] = bsize

				err = filerepair.create_from_file( infile, chkfile, opts )
				if( err < 0 ):
					rtn = rtn + 1

				err = filerepair.verify_file( infile, chkfile, opts )
				if( err < 0 ):
					rtn = rtn + 1

				err = filerepair.create_from_file( badfile, badchkfile, opts )
				if( err < 0 ):
					rtn = rtn + 1

				err = filerepair.verify_file( infile, badchkfile, opts )
				# this should return an error
				if( err == 0 ):
					rtn = rtn + 1

				err = filerepair.verify_file( badfile, chkfile, opts )
				# this should return an error
				if( err == 0 ):
					rtn = rtn + 1

				err = filerepair.repair_file( badfile, chkfile, repfile, opts )
				if( err < 0 ):
					rtn = rtn + 1

		subprocess.call( [ "rm", infile, chkfile ] )

		self.assertEqual( rtn, 0 )

	def test_cksum_algo(self):
		#print
		rtn = 0
		sz = 1*MB

		infile = "testfile_" + str(sz)
		chkfile = infile + ".fr"

		opts = filerepair.utils.DefaultOpts()

		subprocess.call( [ "bin/maketest.py", "-r", "-n", str(sz), infile ] )

		# from python docs, the following should alwyas be present in hashlib
		# (plus a few more)
		for ckalgo in [ 'MD5', 'SHA1', 'SHA256', 'SHA512' ]:
			opts['cksum_algo'] = ckalgo

			err = filerepair.create_from_file( infile, chkfile, opts )
			if( err < 0 ):
				rtn = rtn + 1

			err = filerepair.verify_file( infile, chkfile, opts )
			if( err < 0 ):
				rtn = rtn + 1

		subprocess.call( [ "rm", infile, chkfile ] )

		self.assertEqual( rtn, 0 )


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == '__main__':
	unittest.main()
