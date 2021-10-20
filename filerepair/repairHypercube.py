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

# this code is an attempt at using XOR/RAID-4/-5 techniques on a file, to
# provide better repair-ability in the event of unrecoverable hardware errors

import utils

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


# calculate parity "drives" based on hypercube-coords for each block
def calc_parity( obj ):
	num_parity_disks = obj.num_parity_disks
	block_size = obj.block_size
	file_size  = obj.file_size

	# ref to data matrices
	data = obj.data
	parity = obj.parity_data

	# how many blocks?
	num_blocks = math.ceil( file_size / block_size )
	num_bits = math.ceil( math.log2(num_blocks) )

	# TODO: this may already have been zero'd out
	for p in range(num_parity_disks):
		parity[p] = bytearray( block_size )

	# go through each block
	for b in range(num_blocks):
		# calculate block coords
		coords = utils.to_binarray( b, num_bits )

		# st/fn are the start/finish points for this block of data
		st = b * block_size

		# for each bit in the block-coord, add it in to that parity-disk's calculations
		ofs = 0
		for j in range(num_bits-1,-1,-1):
			p = ofs + coords[j]
			for i in range(block_size):
				parity[p][i] ^= data[st+i]
			ofs = ofs + 2

	return 0

def repair_errors( data_obj, disk_errors, parity_obj ):
	# some heavily used values
	num_data_disks = data_obj.num_data_disks
	num_parity_disks = data_obj.num_parity_disks
	block_size = data_obj.block_size
	data = data_obj.data
	parity_data = parity_obj.parity_data

	n = len(disk_errors)
	if( n == 0 ):
		# no errors found .. shouldn't really occur
		return 0
	if( n > num_parity_disks ):
		#print "* Error: more than 2 disk errors with RAID-4I .. cannot repair file"
		return -1

	for ctr in range(n):
		# : what disk is in error?
		d1 = disk_errors[ ctr ]
		# : which parity-interleave-group is in error?
		pgrp1 = d1 % num_parity_disks

		#print "repairing virtual disk",d1,"from parity data ( disk",p_disk,")"

		# first, we'll fold in the parity data
		st1 = d1 * block_size
		for i in range(block_size):
			data[st1+i] = parity_data[pgrp1][i]

		# now, go thru the rest of the virtual-disks
		for d2 in range(num_data_disks):
			pgrp2 = d2 % num_parity_disks
			if( (d1!=d2) and (pgrp1==pgrp2) ):
				#print( "  folding in d="+str(d2)+" ("+str(pgrp2)+")" )
				st2 = d2 * block_size
				for i in range(block_size):
					data[st1+i] ^= data[st2+i]

		#ctr += 1
		#if( ctr == len(disk_errors) ):
		#	break

	return 0
