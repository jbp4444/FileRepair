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

import os
import binascii

import repairObj
import utils
import logger

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def repair_file( infile, chkfile, repfile, opts=None ):
	if( opts == None ):
		opts = utils.DefaultOpts()

	verbose = int(opts['verbose'])

	if( verbose ):
		logger.printLog( "repairing raid+cksum data for file="+infile+" ("+chkfile+")" )

	try:
		file_size = os.path.getsize( infile )
	except:
		logger.printLog( "* Error: cannot open file="+infile )
		return -1

	parity_obj = repairObj.RepairObj( file_size, opts )
	err = parity_obj.read_parityfile( chkfile )
	if( err ):
		logger.printLog( "* Error: cannot read raid/cksum file="+chkfile )
		return -3

	# NOTE: we'll assume that the cksum file has not been
	#       corrupted, or at least that the opts below
	#       are still intact
	opts['num_parity_disks'] = parity_obj.num_parity_disks
	opts['block_size']       = parity_obj.block_size
	opts['cksum_algo']       = parity_obj.cksum_algo
	opts['parity_type']      = parity_obj.parity_type

	# check if file-size has changed
	if( file_size != parity_obj.file_size ):
		logger.printLog( '* Error: file-size has changed (%d,%d)'%(file_size,parity_obj.file_size) )
		# TODO: is this the best (or only) choice to make for file-size?
		file_size = parity_obj.file_size

	data_obj = repairObj.RepairObj( file_size, opts )
	err = data_obj.read_file( infile )
	if( err ):
		logger.printLog( "* Error: cannot read file contents" )
		return -2

	# re-calculate the raid/cksum stuff for the file itself
	data_obj.calc_parity()
	data_obj.calc_cksums()

	# TODO: should include cksum comparison for parity disks too

	# do the repair in-place
	err = data_obj.calc_repair( parity_obj )
	if( err ):
		logger.printLog( "* Error: problem with file reconstruction" )
		return -3

	# TODO: double-check that the correction worked!

	# TODO: this may make a copy of the file's data
	err = data_obj.write_file( repfile )
	if( err > 0 ):
		logger.printLog( "* Error: could not write repaired file" )
		return err

	return 0


def verify_file( infile, chkfile, opts=None ):
	if( opts == None ):
		opts = utils.DefaultOpts()

	verbose = int(opts['verbose'])

	if( verbose ):
		logger.printLog( "verifying raid+cksum data for file="+infile+" ("+chkfile+")" )

	try:
		file_size = os.path.getsize( infile )
	except:
		logger.printLog( "* Error: cannot open file="+infile )
		return -1

	parity_obj = repairObj.RepairObj( file_size, opts )
	err = parity_obj.read_parityfile( chkfile )
	if( err ):
		logger.printLog( "* Error: cannot read raid/cksum file="+chkfile )
		return -2

	# overwrite raid opts with what we found in the parity-file
	opts['num_parity_disks'] = parity_obj.num_parity_disks
	opts['block_size']       = parity_obj.block_size
	opts['cksum_algo']       = parity_obj.cksum_algo
	opts['parity_type']      = parity_obj.parity_type

	# check if file-size has changed
	if( file_size != parity_obj.file_size ):
		logger.printLog( '* Error: file-size has changed (%d,%d)'%(file_size,parity_obj.file_size) )

	# now we can read the original file
	data_obj = repairObj.RepairObj( file_size, opts )
	err = data_obj.read_file( infile )
	if( err ):
		logger.printLog( "* Error: cannot read file contents" )
		return -3

	# re-calculate the raid/cksum stuff for the file itself
	data_obj.calc_parity()
	data_obj.calc_cksums()

	# go through each disk and compare cksums
	for d in range(data_obj.num_data_disks):
		if( verbose > 9 ):
			logger.printLog( "digests for d=%d are %s and %s"%(d,data_obj.disk_cksums[d],parity_obj.disk_cksums[d]) )

		if( data_obj.disk_cksums[d] != parity_obj.disk_cksums[d] ):
			if( verbose ):
				logger.printLog( "* Error: cksum on disk %d does not match"%(d) )
			err += 1

	# now check parity
	for p in range(data_obj.num_parity_disks):
		for i in range(data_obj.block_size):
			if( data_obj.parity_data[p][i] != parity_obj.parity_data[p][i] ):
				if( verbose ):
					pvalue1 = data_obj.parity_data[p][i]
					pvalue2 = parity_obj.parity_data[p][i]
					logger.printLog( "* Error: parity error at pos=%d:%d %s:%s"%(p,i,hex(pvalue1),hex(pvalue2)) )
				err += 1

	if( err == 0 ):
		if( verbose ):
			logger.printLog( "No errors detected in file" )
		return 0
	#else:

	logger.printLog( "Found %d errors in file"%(err) )
	return -1

def create_from_file( infile, chkfile, opts=None ):
	if( opts == None ):
		opts = utils.DefaultOpts()

	verbose = int(opts['verbose'])

	if( verbose > 0 ):
		logger.printLog( "creating raid+cksum data for file="+infile )

	try:
		file_size = os.path.getsize( infile )
	except:
		logger.printLog( "* Error: cannot open file="+infile )
		return -1

	repair_obj = repairObj.RepairObj( file_size, opts )

	err = repair_obj.read_file( infile )
	if( err ):
		logger.printLog( "* Error: cannot read file contents" )
		return -2

	if( verbose > 2 ):
		logger.printLog( "found %d bytes of data"%(repair_obj.file_size) )
		logger.printLog( "parity type = %s"%(repair_obj.parity_type) )
		logger.printLog( "num parity disks = %d"%(repair_obj.num_parity_disks) )
		logger.printLog( "block size = %d"%(repair_obj.block_size) )
		logger.printLog( "cksum algorithm = %s"%(repair_obj.cksum_algo) )
		logger.printLog( "estim memory used = %d"%(repair_obj.memory_used) )

	repair_obj.calc_parity()
	repair_obj.calc_cksums()

	if( chkfile is not None ):
		err = repair_obj.write_parityfile( chkfile )
		if( err ):
			logger.printLog( "* Error: cannot write output cksum file="+chkfile )
			return -3
	else:
		# ugly hack to return the raw data (not create a file)
		rtn = {
			'parity_type': repair_obj.parity_type,
			'num_data_disks': repair_obj.num_data_disks,
			'num_parity_disks': repair_obj.num_parity_disks,
			'block_size': repair_obj.block_size,
			'file_size': repair_obj.file_size,
			'cksum_algo': repair_obj.cksum_algo,
			'disk_cksums': [],
			'parity_data': []
		}

		for dat in repair_obj.disk_cksums:
			rtn['disk_cksums'].append( dat )

		for p in range(repair_obj.num_parity_disks):
			dat = binascii.hexlify( repair_obj.parity_data[p] )
			rtn['parity_data'].append( dat.decode(encoding='utf-8',errors='strict') )
		
		return rtn

	return 0
