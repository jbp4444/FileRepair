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

# program to dump the bits or bytes of a file to the screen
# (similar to hexdump)

import argparse
import string

import filerepair.utils as utils

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def ParseCommandLineArguments():
	parser = argparse.ArgumentParser(description='show a file as a sequence of bits')
	parser.add_argument( '-c', nargs=1, type=int, help='set number of chars per display row' )
	parser.add_argument( '-D', action='count', help='decimal output' )
	parser.add_argument( '-H', action='count', help='hexadecimal output' )
	parser.add_argument( '-B', action='count', help='binary output' )
	parser.add_argument( '-v', action='count', help='verbose output' )
	parser.add_argument( 'filename', nargs=1, help='file to show' )

	#
	# parse the command-line arguments
	params = vars( parser.parse_args() )

	return params

def toBin( x ):
	bit_mask = 0x80
	txt = ''
	for j in range(8,0,-1):
		if( (x&bit_mask) > 0 ):
			txt = txt + '1'
		else:
			txt = txt + '0'
		bit_mask >>= 1
	return txt

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def main():
	# parse the command-line arguments
	opts = ParseCommandLineArguments()

	if( opts['c'] != None ):
		num_cols = opts['c'][0]
	else:
		num_cols = 80

	if( (opts['H']==None) and (opts['D']==None) ):
		opts['B'] = 1

	#
	# read the input file
	data = utils.read_bytearray_file( opts['filename'][0] )
	if( data == None ):
		print( '* Error: could not process input file' )
		return 1

	filesize = len(data)

	print( 'Found ' + str(filesize) + ' bytes in file' )

	#
	# show all the bits
	c = 0
	out = ''
	for orig in data:

		txt = ''
		if( opts['D'] != None ):
			txt += '%03d' % orig + ' '
		if( opts['H'] != None ):
			txt += '%02X' % orig + ' '
		if( opts['B'] != None ):
			txt += toBin( orig ) + ' '

		if( c == 0 ):
			out = txt
			c += len(txt)
		elif( (c+len(txt)+2) <= num_cols ):
			out += '- '+txt
			c += len(txt) + 2
		else:
			print( out )
			out = txt
			c = len(txt)

	if( c > 0 ):
		print( out )

	return 0

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if( __name__ == "__main__" ):
	err = main()
	exit( err )
