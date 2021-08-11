#!/usr/bin/python
#
# (C) 2015-2016, John Pormann, Duke University, jbp1@duke.edu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of tshe Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
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

#
# overhead calculations for fileraid tools
#

import argparse
import string

import filerepair.repairObj as repairObj
import filerepair.utils as utils

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def ParseCommandLineArguments():
	rtn = utils.DefaultOpts()
	rtn['fsize_start'] = '1K'
	rtn['fsize_finish'] = '100K'

	parser = argparse.ArgumentParser(description='calculate overhead for File Repair process')
	parser.add_argument( '-s', nargs=1, type=str, help='file size to start with (default='+
		str(rtn['fsize_start'])+')' )
	parser.add_argument( '-f', nargs=1, type=str, help='file size to finish with (default='+
		str(rtn['fsize_finish'])+')' )
	parser.add_argument( '-p', nargs=1, type=str, help='set the number of parity disks (default='+
		str(rtn['num_parity_disks'])+')' )
	parser.add_argument( '-b', nargs=1, type=str, help='set the block size (default='+
		str(rtn['block_size'])+')' )
	parser.add_argument( '-c', nargs=1, type=str, help='set the cksum algorithm (default='+
		rtn['cksum_algo']+')' )
	parser.add_argument( '-v', action='count', help='verbose output' )
	parser.add_argument( '-V', action='count', help='really verbose output' )

	#
	# parse the command-line arguments
	params = vars( parser.parse_args() )

	# set the number of stripes
	if( params['p'] != None ):
		rtn['num_parity_disks'] = int( params['p'][0] )

	if( params['b'] != None ):
		rtn['block_size'] = utils.convert_from_kmgt( params['b'][0] )

	# make the code a bit more readable
	if( params['v'] != None ):
		rtn['verbose'] = params['v']
	if( params['V'] != None ):
		rtn['verbose'] += 10*params['V']

	# set cksum algorithm (if needed)
	if( params['c'] != None ):
		rtn['cksum_algo'] = params['c'][0]

	# where to start/finish?
	if( params['s'] > 0 ):
		rtn['fsize_start'] = params['s'][0]
	if( params['f'] > 0 ):
		rtn['fsize_finish'] = params['f'][0]

	return rtn


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def main():
	# parse the command-line arguments
	opts = ParseCommandLineArguments()

	fsz = utils.convert_from_kmgt( opts['fsize_start'] )
	fsz_finish = utils.convert_from_kmgt( opts['fsize_finish'] )

	while( fsz <= fsz_finish ):
		ro = repairObj.RepairObj( fsz, opts )

		# base overhead for text/header line
		overhead = 100
		# cksum overhead
		overhead += ro.num_data_disks * ro.bytes_per_cksum
		# parity overhead
		# NOTE: it doesn't matter if RS or XOR/interleaved, just num_parity_disks
		overhead += ro.num_parity_disks * ro.block_size

		frac = float(overhead)/fsz
		kmgt = utils.convert_to_kmgt( fsz )

		print( string.join( [kmgt,str(fsz),str(ro.block_size),str(frac),str(overhead)], ',' ) )

		fsz = fsz * 2

	return 0

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if( __name__ == "__main__" ):
	err = main()
	exit( err )
