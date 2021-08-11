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

# command-line driver for repairing a file with only a single cklsum


import os
import sys
import argparse
import itertools
import hashlib
import multiprocessing as mp

def DefaultOpts():
	opts = {
		# what cksum algo was used
		'cksum_algo': 'SHA1',

		# how many CPUs to use to speed-up calcs
		'num_procs': 1,

		# verbosity of output
		'verbose': 0
	}
	return opts

def calc_one_cksum( cksum_algo, data ):
	algo = hashlib.new( cksum_algo )
	algo.update( data )
	return algo.hexdigest()

def do_work( pid, inargs, outq ):
	#print "pid",pid,"starting"

	start_pos  = inargs['start_pos']
	cksum_algo = inargs['cksum_algo']
	good_cksum = inargs['good_cksum']
	data       = inargs['data']

	for byte_loc in range(start_pos[pid],start_pos[pid+1]):
		#if( (byte_loc%100) == 0 ):
		#	print "pid",pid,byte_loc
		for byte_val in range(256):
			orig = data[byte_loc]
			data[byte_loc] = byte_val
			new_cksum = calc_one_cksum( cksum_algo, data )
			data[byte_loc] = orig
			if( new_cksum == good_cksum ):
				outq.put( (byte_loc,byte_val) )

	#print "pid",pid,"exitting"
	outq.close()
	return
