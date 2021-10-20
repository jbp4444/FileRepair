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

# program to capture the changed "pieces" of a file that has undergone some
# kind of damage.  Somewhat assumes a digital repository/archive environment
# where multiple (good) copies are also available.

import argparse
import string

import filerepair

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def ParseCommandLineArguments():
	parser = argparse.ArgumentParser(description='create a simple file for testing')
	parser.add_argument( '-v', action='count', help='verbose output' )
	parser.add_argument( '-x', action='count', help='output an xor-based script')
	parser.add_argument( 'filename1', nargs=1, help='known-good file)' )
	parser.add_argument( 'filename2', nargs=1, help='known-bad file' )
	
	# parse the command-line arguments
	params = vars( parser.parse_args() )

	return params

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def main():
	# parse the command-line arguments
	opts = ParseCommandLineArguments()

	#
	# read the two files
	data1 = filerepair.read_bytearray_file( opts['filename1'][0] )
	data2 = filerepair.read_bytearray_file( opts['filename2'][0] )
	if( (data1==None) or (data2==None) ):
		print( '* Error: could not process input files' )
		return -1
	
	#
	# basic tests
	file_size = len(data1)
	if( len(data2) > file_size ):
		data1.extend( 0 for i in range(len(data2)-file_size) ) 
		file_size = len(data2)
		print( "* Warning: file-2 i bigger than file-1, assuming file_size =",file_size )
	elif( len(data2) < file_size ):
		print( "* Warning: file-2 i smaller than file-1, assuming file_size =",file_size )
		data2.extend( 0 for i in range(file_size-len(data2)) ) 
	
	#
	# now find byte-errors
	# : right now, this is extremely simple-minded; no range-finding, etc.
	cmd = []
	for i in range(0,file_size):
		b1 = data1[i]
		b2 = data2[i]
		if( b1 != b2 ):
			if( opts['x'] != None ):
				cmd.append( 'by '+str(i)+' x '+hex(b1^b2) )
			else:
				cmd.append( 'by '+str(i)+' s '+hex(b1) )
	
	if( len(cmd) == 0 ):
		print( "no differences found" )
	else:
		#print( 'mktest.py goodfile -b',string.join(mk_cmd,',')
		print( 'adderror.py badfile -S',string.join(cmd,',') )
	
	return 0

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if( __name__ == "__main__" ):
	err = main()
	exit( err )

