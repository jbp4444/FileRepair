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

# command-line driver for the file-raid tools

import argparse
import random
import string
import os

import utils
import adderror

def ParseCommandLineArguments():
	rtn = adderror.DefaultOpts()

	# get extended help text
	module_path = os.path.dirname(adderror.__file__)
	extended_help = ''
	with open(module_path+'/docs/adderror.md') as f:
		extended_help = extended_help + f.read()

	parser = argparse.ArgumentParser(description='add bit- and byte-errors to a file',
		epilog=extended_help,
		formatter_class=argparse.RawDescriptionHelpFormatter )
	parser.add_argument( '-n', nargs=1, type=str, help='number of errors (default=1)' )
	parser.add_argument( '-b', nargs=1, type=str, help='burst size (default=1)' )
	parser.add_argument( '-m', nargs=1, type=str, help='set bit-mask (default=0xFF)' )
	parser.add_argument( '-s', nargs=1, type=str, help='read byte-errors script from file' )
	parser.add_argument( '-S', nargs=1, action='append', type=str, help='read byte-errors script as cmd-line args' )
	parser.add_argument( '-v', action='count', help='verbose output' )
	parser.add_argument( 'filename', nargs=1, help='input file' )
	parser.add_argument( 'out_file', nargs='?', help='output filename (default=badfile)' )

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
		rtn['out_file'] = rtn['filename'] + '.bad'

	# make the code a bit more readable
	if( params['v'] != None ):
		rtn['verbose'] = params['v']
	else:
		rtn['verbose'] = 0

	# bits to twiddle
	if( params['m'] != None ):
		txt = params['m'][0]
		val = 0xFF
		if( txt[:2] == '0b' ):
			val = int( txt, 2 )
		elif( txt[:2] == '0x' ):
			val = int( txt, 16 )
		else:
			val = int( txt )
		rtn['bit_mask'] = val
	else:
		rtn['bit_mask'] = 0xFF

	# s (burst-size) should be a scalar
	if( params['b'] != None ):
		rtn['burst_size'] = int( params['b'][0] )
	else:
		rtn['burst_size'] = 1

	# error-list as a script
	if( params['s'] != None ):
		rtn['prog_file'] = params['s'][0]
	else:
		rtn['prog_file'] = None
	# error-list as a cmd-line arg
	if( params['S'] != None ):
		rtn['prog_code'] = params['S']
	else:
		rtn['prog_code'] = None

	# make sure opt-n is set correctly
	if( params['n'] != None ):
		rtn['num_errors'] = int( params['n'][0] )
	else:
		rtn['num_errors'] = 1

	return rtn

def read_error_script( file ):
	try:
		f = open( file, 'r' )
		script = f.readlines()
		f.close()
	except:
		return 1
	return 0


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def main():
	# parse the command-line arguments
	opts = ParseCommandLineArguments()

	if( opts['prog_file'] != None ):
		script = adderror.read_error_script( opts['prog_file'] )
		if( script == None ):
			print( "* Error: cannot open script file" )
			exit( -2 )
		opts['script'] = script
	elif( opts['prog_code'] != None ):
		#print opts['prog_code']
		script = []
		for s in opts['prog_code']:
			tmp = string.split( s[0], ',' )
			for t in tmp:
				script.append( t )
		opts['script'] = script
	else:
		opts['script'] = None

	# TODO: allow a seed to be given on cmd-line (for repeatability)?
	random.seed()

	file = opts['filename']
	file_data = utils.read_bytearray_file( file )
	if( file_data == None ):
		print( "* Error: cannot open input file" )
		exit( -1 )

	if( opts['script'] == None ):
		# just add some basic errors
		adderror.add_byte_errors( file_data, opts )
	else:
		# run the script
		adderror.process_error_script( opts['script'], file_data )

	if( opts['out_file'] == None ):
		out_file = file + '.bad'
	else:
		out_file = opts['out_file']
	err = utils.write_bytearray_file( out_file, file_data )
	if( err ):
		print( "* Error: cannot write output file" )
		exit( -2 )

	exit( 0 )

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == '__main__':
	main()
