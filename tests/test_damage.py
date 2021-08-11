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

# some simple constants
KB = 1024
MB = 1024*1024
GB = 1024*1024*1024

class DamageTests( unittest.TestCase ):

	#
	# testing that we can recover from two bytes of damage on same v-disk
	def test_twobytes_samedisk(self):
		#print "test_twobytes_samedisk"
		rtn = 0
		sz = 1*MB

		infile = "testfile_" + str(sz)
		chkfile = infile + ".fr"
		badfile = infile + "_bad"
		badchkfile = badfile + ".fr"
		repfile = badfile + ".rep"

		opts = utils.DefaultOpts()

		subprocess.call( [ "bin/maketest.py", "-r", "-n", str(sz), infile ] )

		for nparity in [ 1,2,4 ]:
			opts['num_parity_disks'] = nparity

			for bsize in [ 1*KB, 4*KB ]:
				#print "bsize=",bsize
				opts['block_size'] = bsize

				# simple "error script" to create 2 contiguous bytes of damage
				# : note the damage always starts at byte-index=0
				ecode = 'by 0-1 x 255'
				subprocess.call( [ "filerepair/cmd_adderror.py", "-S", ecode, infile, badfile ] )

				#print( "2" ),
				err = filerepair.create_from_file( infile, chkfile, opts )
				#print( err ),
				if( err < 0 ):
					rtn = rtn + 1

				err = filerepair.repair_file( badfile, chkfile, repfile, opts )
				if( err < 0 ):
					rtn = rtn + 1

		subprocess.call( [ "rm", infile, chkfile, badfile ] )

		self.assertEqual( rtn, 0 )

	#
	# testing that we can recover from two bytes of damage on two disks
	def test_twobytes_diffdisks(self):
		#print "test_twobytes_diffdisks"
		rtn = 0
		sz = 1*MB

		infile = "testfile_" + str(sz)
		chkfile = infile + ".fr"
		badfile = infile + "_bad"
		badchkfile = badfile + ".fr"
		repfile = badfile + ".rep"

		opts = utils.DefaultOpts()

		subprocess.call( [ "bin/maketest.py", "-r", "-n", str(sz), infile ] )

		for nparity in [ 2,4 ]:
			opts['num_parity_disks'] = nparity

			for bsize in [ 1*KB, 4*KB ]:
				#print "bsize=",bsize
				opts['block_size'] = bsize

				# simple "error script" to create 2 contiguous damage areas
				# : note the damage always starts at byte-index=0
				ecode = 'by 0 x 255,by ' + str(bsize) + ' x 255'
				subprocess.call( [ "filerepair/cmd_adderror.py", "-S", ecode, infile, badfile ] )

				#print( "2" ),
				err = filerepair.create_from_file( infile, chkfile, opts )
				#print( err ),
				if( err < 0 ):
					rtn = rtn + 1

				err = filerepair.repair_file( badfile, chkfile, repfile, opts )
				if( err < 0 ):
					rtn = rtn + 1

		subprocess.call( [ "rm", infile, chkfile, badfile ] )

		self.assertEqual( rtn, 0 )

	#
	# testing that we can recover from whole-sector damage-events
	def test_sectordamage(self):
		#print "test_sectordamage"
		rtn = 0
		sz = 1*MB

		infile = "testfile_" + str(sz)
		chkfile = infile + ".fr"
		badfile = infile + "_bad"
		badchkfile = badfile + ".fr"
		repfile = badfile + ".rep"

		opts = utils.DefaultOpts()

		subprocess.call( [ "bin/maketest.py", "-r", "-n", str(sz), infile ] )

		for nparity in [ 1,2,4 ]:
			opts['num_parity_disks'] = nparity

			for bsize in [ 1*KB, 4*KB ]:
				#print "bsize=",bsize
				opts['block_size'] = bsize

				# simple "error script" to create 1 sectors-worth of damage
				# : note the damage always starts at byte-index=0
				ecode = 'by 0-' + str(bsize-1) + ' x 255'
				subprocess.call( [ "filerepair/cmd_adderror.py", "-S", ecode, infile, badfile ] )

				#print( "2" ),
				err = filerepair.create_from_file( infile, chkfile, opts )
				#print( err ),
				if( err < 0 ):
					rtn = rtn + 1

				err = filerepair.repair_file( badfile, chkfile, repfile, opts )
				if( err < 0 ):
					rtn = rtn + 1

		subprocess.call( [ "rm", infile, chkfile, badfile ] )

		self.assertEqual( rtn, 0 )

	#
	# testing that we can recover from four bytes of damage on four disks
	def test_fourbytes_diffdisks(self):
		#print "test_fourbytes_diffdisks"
		rtn = 0
		sz = 1*MB

		infile = "testfile_" + str(sz)
		chkfile = infile + ".fr"
		badfile = infile + "_bad"
		badchkfile = badfile + ".fr"
		repfile = badfile + ".rep"

		opts = utils.DefaultOpts()

		subprocess.call( [ "bin/maketest.py", "-r", "-n", str(sz), infile ] )

		for nparity in [ 4 ]:
			opts['num_parity_disks'] = nparity

			for bsize in [ 1*KB ]:
				#print "bsize=",bsize
				opts['block_size'] = bsize

				# simple "error script" to create 4 regions of damage
				# : note the damage always starts at byte-index=0 in each block
				ecode = 'by 0 x 255,by ' + str(bsize) + ' x 255,by '+str(2*bsize)+' x 255,by '+str(3*bsize)+' x 255'
				subprocess.call( [ "filerepair/cmd_adderror.py", "-S", ecode, infile, badfile ] )

				#print( "2" ),
				err = filerepair.create_from_file( infile, chkfile, opts )
				#print( err ),
				if( err < 0 ):
					rtn = rtn + 1

				err = filerepair.repair_file( badfile, chkfile, repfile, opts )
				if( err < 0 ):
					rtn = rtn + 1

		subprocess.call( [ "rm", infile, chkfile, badfile ] )

		self.assertEqual( rtn, 0 )

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == '__main__':
	unittest.main()
