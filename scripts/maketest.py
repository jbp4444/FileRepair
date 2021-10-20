#!/usr/bin/python
#
# (C) June 2015, John Pormann, Duke University, jbp1@duke.edu
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

# program to create simple data files for testing of the file-raid programs

import argparse
import string
import random

import filerepair.utils as utils

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def ParseCommandLineArguments():
	rtn = {}

	parser = argparse.ArgumentParser(description='create a simple file for testing')
	parser.add_argument( '-n', nargs=1, type=str, help='number of bytes in file' )
	parser.add_argument( '-f', nargs=1, type=str, help='fixed byte-value(s) at each position (default=0)' )
	parser.add_argument( '-r', action='count', help='use random byte-values' )
	parser.add_argument( '-i', action='count', help='use incrementing byte-values 0,1,2,...' )
	parser.add_argument( '-b', type=str, action='append', help='force error at given byte-position' )
	parser.add_argument( '-v', action='count', help='verbose output' )
	parser.add_argument( 'filename', nargs='?', help='output filename (default=outfile)' )

	#
	# parse the command-line arguments
	params = vars( parser.parse_args() )

	# only 1 file can be processed at a time
	if( params['filename'] != None ):
		rtn['filename'] = params['filename']
	else:
		rtn['filename'] = 'outfile'

	# pass-thru parameters
	rtn['n'] = params['n']
	rtn['f'] = params['f']
	rtn['r'] = params['r']
	rtn['i'] = params['i']

	# make the code a bit more readable
	if( params['v'] != None ):
		rtn['verbose'] = params['v']
	else:
		rtn['verbose'] = 0

	#
	# normalize the -B and -c options
	if( params['b'] != None ):
		blist = []
		for x in params['b']:
			if( string.find(x,',') >= 0 ):
				flds = string.split(x,',')
				for f in flds:
					blist.append( f )
				else:
					blist.append( x )
		rtn['b'] = blist
	else:
		rtn['b'] = None

	return rtn

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def main():
	# parse the command-line arguments
	opts = ParseCommandLineArguments()

	if( opts == None ):
		opts = {
			'filename': 'outfile',
			'n': 1,
			'f': None,
			'r': None,
			'i': None,
			'b': None,
			'verbose': 0
		}
	else:
		# TODO: check that all input args are defined
		pass

	# how big should the file be?
	file_size = 1
	if( opts['n'] != None ):
		file_size = utils.convert_from_kmgt( opts['n'][0] )

	# "background values" (fixed or random numbers)
	fixed_vals = [ 0 ]
	if( opts['f'] != None ):
		l = string.split( opts['f'][0], ',' )
		fixed_vals = []
		for n in l:
			fixed_vals.append( int(n) )
	elif( opts['i'] != None ):
		fixed_vals = range(0,256)
	num_vals = len(fixed_vals)

	# allocate some memory
	data = bytearray( file_size )
	if( opts['verbose'] > 0 ):
		print( 'Creating ' + str(file_size) + ' bytes in file "'+opts['filename']+'"' )

	# TODO: allow a seed to be given on cmd-line (for repeatability)?
	random.seed()

	# go through each byte for the "background value"
	for i in range(0,file_size):
		if( opts['r'] != None ):
			val = random.randint(0,255)
		else:
			val = fixed_vals[ i%num_vals ]
		data[i] = val

	# now see if we should doctor this up any further
	# i.e. overwrite the "background value" with a user-defined value
	if( opts['b'] != None ):
		for bb in opts['b']:
			# try to split each entry on '='
			iv = string.split( bb, '=' )
			idx = string.atoi( iv[0] )
			if( len(iv) > 1 ):
				# entry has "index=value"
				if( string.find(iv[1],'0x') >= 0 ):
					val = string.atoi( iv[1], 16 )
				else:
					val = string.atoi( iv[1] )
			else:
				# entry is just a number
				val = None

			# change the data
			orig = data[idx]
			if( val == None ):
				data[idx] ^= 255
			else:
				data[idx] = val

			if( opts['verbose'] > 0 ):
				print( "change at n="+str(idx) \
					+" from "+hex(orig)+" to " \
					+hex(data[idx]) )

	# write the output file
	err = utils.write_bytearray_file( opts['filename'], data )
	if( err ):
		print( '* Error: could not process output file' )
		err = 1

	return err

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if( __name__ == "__main__" ):
	err = main()
	exit( err )
