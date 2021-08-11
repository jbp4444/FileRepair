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


import unittest

import filerepair.repairObj as repairObj
import filerepair.utils as utils

class repairObjTests( unittest.TestCase ):

	def test_nparity(self):
		#print
		err = 0

		opts = utils.DefaultOpts()

		for nparity in [ 1 ]:
			opts['num_parity_disks'] = nparity
			num_data_disks = 8 * nparity

			for bsize in [ 1024 ]:
				opts['block_size'] = bsize

				# make a big enough "file" to have multiple virtual-data-disks
				file_size = num_data_disks * bsize

				repair_obj = repairObj.RepairObj( file_size, opts )
				repair_obj.create_dummy_data()

				data  = repair_obj.data
				#print( " len(data)="+str(len(data))+","+str(file_size) )
				pdata = repair_obj.parity_data

				# fill in known bytes, disk0=1, disk1=2, disk2=4, etc.
				val = 1
				val_xor = 0
				for d in range(num_data_disks):
					st = d * bsize
					#print( "st="+str(st)+" fn="+str(st+bsize)+" val="+hex(val)+","+hex(val_xor) )
					for i in range(bsize):
						data[st+i] = val

					if( (d%nparity) == (nparity-1) ):
						val_xor = val_xor ^ val
						val = val * 2

				#print( "val_xor="+hex(val_xor) )
				repair_obj.calc_parity()

				# check the calcs
				for p in range(nparity):
					for i in range(bsize):
						if( pdata[p][i] != val_xor ):
							#print( "p="+str(p)+" i="+str(i)+" "+hex(pdata[p][i])+","+hex(val_xor) )
							err = err + 1

		self.assertEqual( err, 0 )

	def test_reedsolo(self):
		#print
		err = 0

		# for RS with 8 data-disks and 4 parity-disks:
		#    a='ABCDEFGH'=[ 0x41, 0x42, ... 0x48 ]
		#    b=encode(a)=[ a, 0xb6, 0x4d, 0xcc, 0x3f ]
		#ndisks = 8
		#bsize = 1024
		#nparity = 4
		known_good = [ 0xb6, 0x4d, 0xcc, 0x3f ]

		opts = utils.DefaultOpts()
		opts['parity_type'] = 'r'

		for nparity in [ 4 ]:
			opts['num_parity_disks'] = nparity
			num_data_disks = 8

			for bsize in [ 1024 ]:
				opts['block_size'] = bsize

				# make a big enough "file" to have multiple virtual-data-disks
				file_size = num_data_disks * bsize

				repair_obj = repairObj.RepairObj( file_size, opts )
				repair_obj.create_dummy_data()

				data  = repair_obj.data
				#print( " len(data)="+str(len(data))+","+str(file_size) )
				pdata = repair_obj.parity_data

				# fill in known bytes, disk0=1, disk1=2, disk2=4, etc.
				val = 0x41
				for d in range(num_data_disks):
					st = d * bsize
					#print( "st="+str(st)+" fn="+str(st+bsize)+" val="+hex(val)+","+hex(val_xor) )
					for i in range(bsize):
						data[st+i] = val + d

				repair_obj.calc_parity()

				# check the calcs
				for p in range(nparity):
					val = known_good[p]
					flag = 1
					for i in range(bsize):
						if( pdata[p][i] != val ):
							if( flag == 1 ):
								print( "at "+str(p)+","+str(i)+" expected "+hex(val)+" got "+hex(pdata[p][i]) )
								flag = 0
							err = err + 1

		self.assertEqual( err, 0 )

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == '__main__':
	unittest.main()
