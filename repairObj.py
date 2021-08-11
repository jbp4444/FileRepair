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

# this code is an attempt at using RAID-4/-5 (and eventually -6) techniques on a file, to
# provide better repair-ability in the event of unrecoverable hardware errors

import string
import hashlib
import binascii
import time
import os
import math

# from . import utils
# from . import repairInterleaved
# from . import repairReedsolo
import utils
import repairInterleaved
import repairReedsolo
import repairHypercube

# the mathematical algorithm/papers suggest rdp_p must be prime and greater than 2
# known_primes = [ 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
# 	101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199 ]

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class RepairObj:
	def __init__( self, file_size, opts=None ):
		if( opts == None ):
			opts = utils.DefaultOpts()

		self.parity_type = str(opts['parity_type'])
		self.num_parity_disks = int(opts['num_parity_disks'])
		self.block_size = int(opts['block_size'])
		if( 'cksum_algo' in opts ):
			self.cksum_algo = opts['cksum_algo']
		else:
			self.cksum_algo = "SHA1"

		self.file_size = file_size

		# how many virtual-data-disks are there?
		self.num_data_disks = utils.intRoundDown( self.file_size, self.block_size )

		# for hypercube parity system, the num parity disks = num bits in block-coords
		if( self.parity_type == 'x' ):
			n_blks = math.ceil( self.file_size / self.block_size )
			if( n_blks < 2 ):
				n_blks = 2
			self.num_parity_disks = 2 * math.ceil( math.log2(n_blks) )
			self.num_data_disks = 1

		# temp data area
		self.data = []
		self.parity_data = [ [] for p in range(self.num_parity_disks) ]

		# temp cksum area
		self.disk_cksums = [ 0 for d in range(self.num_data_disks) ]

		# just so we have it handy .. size of a cksum
		h = hashlib.new( self.cksum_algo )
		self.bytes_per_cksum = h.digest_size

		self.memory_used = (self.num_data_disks+self.num_parity_disks)*self.block_size
		self.memory_used += self.num_data_disks*self.bytes_per_cksum

		return

	def create_dummy_data( self ):
		self.data = bytearray( self.num_data_disks*self.block_size )
		for p in range(self.num_parity_disks):
			self.parity_data[p] = bytearray( self.block_size )
		return 0

	def read_file( self, file ):
		self.data = utils.read_bytearray_file( file )
		if( self.data == None ):
			return 1
		nblks = utils.intRoundDown( len(self.data), self.block_size )
		if( (nblks*self.block_size) != self.file_size ):
			# print( "len(data)="+str(len(self.data)) )
			xtra = abs(self.file_size - nblks*self.block_size)
			# print( "  adding="+str(xtra) )
			self.data.extend( [0 for y in range(xtra)] )
			# print( "  now len(data)="+str(len(self.data)) )
		return 0

	def write_file( self, file ):
		err = utils.write_bytearray_file( file, self.data[:self.file_size] )
		if( err != 0 ):
			return 1
		return 0

	# TODO: could/should write cksum of parity-disk to the file
	def read_parityfile( self, file ):
		try:
			f = open( file, 'r' )
			txt = f.readline()
			txt = txt.strip()
			flds = txt.split( ',' )
			self.parity_type = flds[0]
			self.num_data_disks = int( flds[1] )
			self.num_parity_disks = int( flds[2] )
			self.block_size = int( flds[3] )
			self.file_size = int( flds[4] )

			txt = f.readline()
			txt = txt.strip()
			self.cksum_algo = txt

			# temp memory areas
			self.disk_cksums = [ 0 for d in range(self.num_data_disks) ]
			self.data = []
			self.parity_data = [ [] for p in range(self.num_parity_disks) ]

			# just so we have it handy .. size of a cksum
			h = hashlib.new( self.cksum_algo )
			self.bytes_per_cksum = h.digest_size

			self.memory_used = (self.num_data_disks+self.num_parity_disks)*self.block_size
			self.memory_used += self.num_data_disks*self.bytes_per_cksum

			for d in range(self.num_data_disks):
				txt = f.readline()
				txt = txt.strip()
				self.disk_cksums[d] = txt

			# now let the parity-disk information
			for p in range(self.num_parity_disks):
				txt = f.readline()
				txt = txt.strip()
				self.parity_data[p] = bytearray( binascii.unhexlify( txt ) )

			f.close()
		except Exception as e:
			print( "Exception caught: "+str(e) )
			return 1
		return 0

	def write_parityfile( self, file ):
		try:
			f = open( file, 'w' )
			f.write( self.parity_type+','+str(self.num_data_disks)+","+str(self.num_parity_disks)+","+str(self.block_size)+','+str(self.file_size)+"\n" )
			f.write( self.cksum_algo+"\n" )
			for dat in self.disk_cksums:
				f.write( dat + "\n" )

			# now write the parity-disk info
			for p in range(self.num_parity_disks):
				dat = binascii.hexlify( self.parity_data[p])
				f.write( dat.decode(encoding='utf-8',errors='strict') )
				f.write( '\n' )

			f.close()
		except Exception as e:
			print( "** ERROR: cannot write repair file: "+str(e) )
			return 1
		return 0

	def calc_cksums( self ):
		# hypercube approach doesn't need cksums at all
		# : but with num-data-disks=1, this still works (for whole-file cksum)
		st = 0
		fn = self.block_size
		for d in range(self.num_data_disks):
			algo = hashlib.new( self.cksum_algo )
			algo.update( self.data[st:fn] )
			self.disk_cksums[d] = algo.hexdigest()

			st += self.block_size
			fn += self.block_size

		return 0

	def calc_parity( self ):
		if( self.parity_type == 'i' ):
			repairInterleaved.calc_parity( self )
		elif( self.parity_type == 'r' ):
			repairReedsolo.calc_parity( self )
		elif( self.parity_type == 'x' ):
			repairHypercube.calc_parity( self )
		else:
			# TODO: throw an error?
			return 1
		return 0

	def calc_repair( self, parity_obj ):
		# NOTE: assumes that self-object has the file's data and raid_objCK
		#       has the cksum info (but no data)

		# go through each cksum
		disk_errors = []
		for d in range(self.num_data_disks):
			if( self.disk_cksums[d] != parity_obj.disk_cksums[d] ):
				#print "* Warning: cksum on disk",d,"does not match",self.disk_cksums[d],parity_obj.disk_cksums[d]
				disk_errors.append( d )

		if( len(disk_errors) == 0 ):
			# no errors found
			return 0

		if( self.parity_type == 'i' ):
			err = repairInterleaved.repair_errors( self, disk_errors, parity_obj )
		elif( self.parity_type == 'r' ):
			err = repairReedsolo.repair_errors( self, disk_errors, parity_obj )
		elif( self.parity_type == 'x' ):
			err = repairHypercube.repair_errors( self, disk_errors, parity_obj )
		else:
			# TODO: throw an error?
			err = 1

		return err
