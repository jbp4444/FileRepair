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

# program to add bit or byte errors to a file (for synthetic testing of
# the file-raid code)

import string
import random

import utils


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def DefaultOpts():
	opts = {
		'num_errors': 1,
		'burst_size': 1,
		'bit_mask' : 0xFF,
		'verbose': 0
	}
	return opts

def add_byte_errors( data, inopts=None ):

	data_size = len(data)

	opts = DefaultOpts()
	if( inopts != None ):
		for key,val in inopts.iteritems():
			opts[key] = val

	if( opts['verbose'] > 0 ):
		print 'Found',data_size,'bytes'

	# add in the errors
	for i in range( opts['num_errors'] ):
		n_start = random.randint(0,data_size-1)
		for j in range(0,opts['burst_size']):
			orig = data[n_start+j]
			data[n_start+j] ^= opts['bit_mask']

			if( opts['verbose'] > 0 ):
				print "change at n="+str(n_start+j) \
					+" from "+hex(orig)+" to " \
					+hex(data[n_start+j])
	return

#
# convenience function for testing
def add_errors_to_file( infile, outfile, opts=None ):
	file_data = utils.read_bytearray_file( infile )
	if( file_data == None ):
		print "* Error: cannot open input file"
		return -100

	# just add some basic errors
	add_byte_errors( file_data, opts )

	err = utils.write_bytearray_file( outfile, file_data )

	return err

# adderror script looks like:
#    (bit_or_byte) (range) (operation) (value)
def process_error_script( script, data ):

	num_sloc = len( script )
	#print 'Found',num_sloc,'lines of code in script'

	data_size = len(data)
	#print 'Found',data_size,'bytes'

	for l in range(0,num_sloc):
		#print 'line',l,'[',script[l],']'
		flds = string.split( script[l], ' ' )

		if( string.find(flds[1],'-') >= 0 ):
			tmp = string.split( flds[1], '-' )
			idx_start = int(tmp[0])
			idx_end   = int(tmp[1])
		else:
			idx_start = int(flds[1])
			idx_end   = idx_start+1

		op = flds[2][0]
		if( len(flds) < 4 ):
			# no value given, have to assume it from operation being performed
			if( op == 's' ):
				val = 0
			elif( op == 'x' ):
				val = 255
		else:
			txt = flds[3]
			if( txt[0:2] == '0x' ):
				val = int( txt, 16 )
			elif( flds[1][0:2] == '0o' ):
				val = int( txt, 8 )
			elif( flds[1][0:2] == '0b' ):
				val = int( txt, 2 )
			else:
				val = int( txt )

		if( flds[0][0:2] == 'bi' ):
			# bit indexing
			for idx in range(idx_start,idx_end):
				(byte_idx,bit_idx,byte_mask) = bitnum_to_byte(idx)
				alt_mask = 0xFF ^ byte_mask
				orig = data[byte_idx]
				inside_bit = data[byte_idx] & byte_mask
				other_bits = data[byte_idx] & alt_mask
				#print "idx=",idx,byte_idx,bit_idx
				#print showbits(byte_mask),hex(byte_mask),byte_mask,'byte_mask'
				#print showbits(alt_mask),hex(alt_mask),alt_mask,'alt_mask'
				#print showbits(orig),hex(orig),orig,'orig'
				#print showbits(val),hex(val),val,'val'
				#print showbits(inside_bit),hex(inside_bit),inside_bit
				#print showbits(other_bits),hex(other_bits),other_bits
				#print showbits(inside_bit^val),hex(inside_bit^val),inside_bit^val,'inside_bit^val'
				if( op == 'r' ):
					new_bit = random.randint(0,1) * byte_mask
				elif( op == 's' ):
					new_bit = ( inside_bit | val ) & byte_mask
				elif( op == 'x' ):
					new_bit = ( inside_bit ^ val ) & byte_mask
				#print showbits(new_bit),hex(new_bit),new_bit,'new_bit'
				data[byte_idx] = other_bits | new_bit
				#print showbits(data[byte_idx])

				#print "change at bit="+str(idx) \
				#		+" from 0b"+showbits(orig)+" to 0b" \
				#		+showbits(data[byte_idx])

		else:
			# byte indexing
			for idx in range(idx_start,idx_end):
				orig = data[idx]
				if( op == 'r' ):
					data[idx] = random.randint(0,255)
				elif( op == 's' ):
					data[idx] = val
				elif( op == 'x' ):
					data[idx] ^= val

				#print "change at byte="+str(idx) \
				#		+" from "+hex(orig)+" to " \
				#		+hex(data[idx])

	return
