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

# this code is an attempt at Reed-Solomon techniques on a file, to
# provide better repair-ability in the event of unrecoverable hardware errors

import string

import utils
import reedsolo

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# this performs the RS encoding, storing the extra bits to parity drives
# NOTE: we do this on a block-by-block basis so that we can recover from
#       whole-sector damage equivalents
def calc_parity( obj ):
	num_data_disks = obj.num_data_disks
	num_parity_disks = obj.num_parity_disks
	total_msg_size = num_data_disks + num_parity_disks
	block_size = obj.block_size

	# ref to data matrices
	data = obj.data
	parity = obj.parity_data

	# create the encoder/decoder
	#print( "RS codec nsym="+str(num_parity_disks)+" nsize="+str(num_data_disks+num_parity_disks) )
	rs = reedsolo.RSCodec( nsym=num_parity_disks, nsize=total_msg_size )

	# TODO: this may already have been zero'd out
	for p in range(num_parity_disks):
		parity[p] = bytearray( block_size )

	for i in range(block_size):
		msg = bytearray( num_data_disks )
		for d in range(num_data_disks):
			st = d * block_size
			msg[d] = data[st+i]
		enc = rs.encode( msg )
		for p in range(num_parity_disks):
			parity[p][i] = enc[p+num_data_disks]

	return 0

def repair_errors( data_obj, disk_errors, parity_obj ):
	# some heavily used values
	num_data_disks = data_obj.num_data_disks
	num_parity_disks = data_obj.num_parity_disks
	total_msg_size = num_data_disks + num_parity_disks
	block_size = data_obj.block_size
	data = data_obj.data
	parity_data = parity_obj.parity_data

	n = len(disk_errors)
	if( n == 0 ):
		# no errors found .. shouldn't really occur
		return 0
	if( n > (num_parity_disks/2) ):
		# TODO: this is not 100% accurate, but is a good first approx
		return -1

	# TODO: catch errors thrown by RS library

	# create the encoder/decoder
	#print( "RS codec nsym="+str(num_parity_disks)+" nsize="+str(num_data_disks+num_parity_disks) )
	rs = reedsolo.RSCodec( nsym=num_parity_disks, nsize=total_msg_size )

	for i in range(block_size):
		msg = bytearray( total_msg_size )
		for d in range(num_data_disks):
			st = d * block_size
			msg[d] = data[st+i]
		for p in range(num_parity_disks):
			msg[p+num_data_disks] = parity_data[p][i]
		dec = rs.decode( msg )
		for d in range(num_data_disks):
			st = d * block_size
			data[st+i] = dec[d]

	return 0
