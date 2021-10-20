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

import utils
import basicrepair

def ParseCommandLineArguments():
	rtn = basicrepair.DefaultOpts()

	# get extended help text
	module_path = os.path.dirname(basicrepair.__file__)
	extended_help = ''
	with open(module_path+'/docs/basicrepair.md') as f:
		extended_help = extended_help + f.read()

	parser = argparse.ArgumentParser(description='attempt to repair a file from a single checksum',
		epilog=extended_help,
		formatter_class=argparse.RawDescriptionHelpFormatter )
	parser.add_argument( '-n', nargs=1, type=str, help='number of processors to use (default='+
		str(rtn['num_procs'])+')' )
	parser.add_argument( '-c', nargs=1, type=str, help='set the cksum algorithm (default='+
		rtn['cksum_algo']+')' )
	parser.add_argument( '-C', nargs=1, type=str, help='the known-good cksum value' )
	parser.add_argument( '-v', action='count', help='verbose output' )
	parser.add_argument( 'filename', nargs=1, help='input file' )
	parser.add_argument( 'out_file', nargs='?', help='output filename (default=inputfile.rep)' )

	#
	# parse the command-line arguments
	params = vars( parser.parse_args() )

	# only 1 file can be processed at a time
	rtn['filename'] = params['filename'][0]
	if( params['out_file'] != None ):
		rtn['out_file'] = params['out_file'][0]

	# assign an output-filename
	if( params['out_file'] != None ):
		rtn['out_file'] = params['out_file']
	else:
		rtn['out_file'] = rtn['filename'] + '.rep'

	# make the code a bit more readable
	if( params['v'] != None ):
		rtn['verbose'] = params['v']

	# make sure opt-n is set correctly
	if( params['n'] != None ):
		rtn['num_procs'] = int( params['n'][0] )

	# set cksum algorithm (if needed)
	if( params['c'] != None ):
		rtn['cksum_algo'] = params['c'][0]

	# set cksum value
	if( params['C'] != None ):
		rtn['cksum_value'] = params['C'][0]

	return rtn


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def main():
	# parse the command-line arguments
	opts = ParseCommandLineArguments()

	print "running with",opts['num_procs'],"procs"

	data = utils.read_bytearray_file( opts['filename'] )
	if( data == None ):
		print "* Error: could not open file for reading"
		return -2
	data_size = len(data)

	# are there any errors?
	recheck_cksum = basicrepair.calc_one_cksum( opts['cksum_algo'], data )
	if( recheck_cksum == opts['cksum_value'] ):
		print "File has no errors .. exitting"
		return 0

	# set up the partitioning of the tasks
	# : make sure to account for non-multiples of num_procs
	np = opts['num_procs']
	start_pos = [ 0 for i in range(np+1) ]
	b_div = int( data_size/np )
	b_mod = data_size % np
	for i in range(np):
		if( i < b_mod ):
			# this task gets an extra bit of work to do
			start_pos[i+1] = start_pos[i] + b_div + 1
		else:
			start_pos[i+1] = start_pos[i] + b_div
	inargs = {
		'data':       data,
		'data_size':  data_size,
		'cksum_algo': opts['cksum_algo'],
		'good_cksum': opts['cksum_value'],
		'num_procs':  opts['num_procs'],
		'start_pos':  start_pos
	}
	outputq = mp.Queue()

	# launch the procs and wait for them to finish
	pids = []
	for p in range(np):
		pid = mp.Process( target=basicrepair.do_work, args=(p,inargs,outputq) )
		pid.start()
		#print "pid",p,pid,"started"
		pids.append( pid )
	# wait for them all to finish
	# TODO: make this async so we can exit early if we find a fix
	for p in pids:
		p.join()
	#print "all procs exitted"

	found_flag = 0
	found_info = (-1,-1)
	while( 1 ):
		try:
			v = outputq.get( block=False )
			if( v != None ):
				found_flag = 1
				found_info = v
				print 'Found solution',found_info
				#break
		except:
			# TODO: make sure this is Queue.Empty
			break

	# double-check that we found the fix for this plane
	if( found_flag == 1 ):
		# save the corrected data back to params
		byte_loc = found_info[0]
		byte_val = found_info[1]
		data[byte_loc] = byte_val

		err = utils.write_bytearray_file( opts['out_file'], data )
		if( err ):
			print "* Error: could not write repaired file"
			return -10
	else:
		print "* Error: no solution was found"
		return -11

	return 0
