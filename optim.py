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

import math

import raidObj
import utils


# try to calculate (BRUTE FORCE) the best RAID config to use
# : you MUST specify a RAID-level in opts!
def CalcOptimOpts( file_size, opts ):
	# scan a range of num_disks and block sizes
	# looking for least-overhead config

	# make sure we don't malloc the memory over and over again
	opts['SKIP_MALLOC'] = True

	# TODO: check all required opts components
	if( 'fac_num_disks' in opts ):
		fac_num_disks = float(opts['fac_num_disks'])
	else:
		fac_num_disks = 2.0

	min_config = (-1,-1)
	min_overhead = 10000*file_size

	# ensure that we check value at max_num_disks
	max_num_disks = opts['max_num_disks'] * fac_num_disks

	print( 'fac_num_disks='+str(fac_num_disks) )

	num_disks = opts['min_num_disks']
	while( num_disks < max_num_disks ):
		if( num_disks <= opts['max_num_disks'] ):
			inum_disks = int(num_disks)
		else:
			inum_disks = opts['max_num_disks']
		opts['num_disks'] = inum_disks

		block_size = opts['min_block_size']
		while( block_size <= opts['max_block_size'] ):
			opts['block_size'] = block_size

			print( "ndisks="+str(inum_disks)+"  bksize="+str(block_size) )

			try:
				raid_obj = raidObj.RaidObj( file_size, opts )
				total_overhead = raid_obj.raid_overhead()
			except:
				total_overhead = 10000*file_size

			if( total_overhead < min_overhead ):
				min_overhead = total_overhead
				min_config = (inum_disks,block_size)
			elif( total_overhead == min_overhead ):
				# we prefer larger block-sizes since they protect more data
				(x,y) = min_config
				if( block_size > y ):
					min_config = (inum_disks,block_size)

			# TODO: get more creative on scanning the range of num-disks
			block_size *= 2

		# TODO: get more creative on scanning the range of num-disks
		#num_disks = num_disks + disk_incr
		num_disks *= fac_num_disks

	opts['SKIP_MALLOC'] = False

	#print "Min config =",min_config,"  Min overhead =",min_overhead

	return (min_config,min_overhead)
