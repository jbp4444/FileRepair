#!/usr/bin/python
#
# (C) 2015-2016, John Pormann, Duke University, jbp1@duke.edu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of tshe Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
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
# overhead calculations for fileraid tools
#

import argparse
import string

import filerepair.repairObj as repairObj
import filerepair.utils as utils

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def exp_range(start, end, mul):
	while start < end:
		yield start
		start *= mul

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def main():
	opts = utils.DefaultOpts()

	for fsize in exp_range(1024,1+1024*1024*1024,4):
		for bsize in exp_range(1024,65536,4):
			for nparity in range(1,4):

				opts['num_parity_disks'] = nparity
				opts['block_size'] = bsize

				ro = repairObj.RepairObj( fsize, opts )

				# base overhead for text/header line
				overhead = 100
				# cksum overhead
				overhead += ro.num_data_disks * ro.bytes_per_cksum
				# parity overhead
				# NOTE: it doesn't matter if RS or XOR/interleaved, just num_parity_disks
				overhead += ro.num_parity_disks * ro.block_size

				frac = float(overhead)/fsize
				kmgt = utils.convert_to_kmgt( fsize )

				print( '%d, %s, %d, %d, %f, %f' % (fsize,kmgt,bsize,nparity,frac,overhead) )

	return 0

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if( __name__ == "__main__" ):
	err = main()
	exit( err )
