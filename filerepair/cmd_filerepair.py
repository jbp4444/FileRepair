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

# command-line driver for the file-raid tools

import argparse
import string

import utils
import filerepair
import logger

def ParseCommandLineArguments():
	rtn = utils.DefaultOpts()

	parser = argparse.ArgumentParser(description='construct a "RAID" file for the given input-file')
	parser.add_argument( '-C', nargs=1, type=str, help='read opts file' )
	parser.add_argument( '-L', nargs=1, type=str, help='send output to log file' )
	parser.add_argument( '-b', nargs=1, type=str, help='set the block size (default='+
		str(rtn['block_size'])+')' )
	parser.add_argument( '-c', nargs=1, type=str, help='set the cksum algorithm (default='+
		rtn['cksum_algo']+')' )
	parser.add_argument( '-p', nargs=1, type=str, help='set the number of parity disks (default='+
		str(rtn['num_parity_disks'])+')' )
	parser.add_argument( '-i', action='count', help='use interleaved parity' )
	parser.add_argument( '-r', action='count', help='use Reed-Solomon parity' )
	parser.add_argument( '-X', action='count', help='use hypercube-raid system' )
	parser.add_argument( '-v', action='count', help='verbose output' )
	parser.add_argument( '-V', action='count', help='really verbose output' )
	parser.add_argument( 'command', nargs=1, help='command to execute (create, verify, repair)' )
	parser.add_argument( 'filelist', nargs='+', help='file(s) to work with' )

	#
	# parse the command-line arguments
	params = vars( parser.parse_args() )

	# set a new opts file
	if( params['C'] != None ):
		#rtn['opts_file'] = params['C'][0]
		# parse the opts file
		rtn = utils.read_config_file( params['C'][0], rtn )

	# set the number of stripes
	if( params['p'] != None ):
		rtn['num_parity_disks'] = int( params['p'][0] )

	if( params['b'] != None ):
		rtn['block_size'] = utils.convert_from_kmgt( params['b'][0] )

	# XOR/RAID-4/5 parity or Reed-Solomon
	if( params['i'] != None ):
		rtn['parity_type'] = 'i'
	elif( params['r'] != None ):
		rtn['parity_type'] = 'r'
	elif( params['X'] != None ):
		rtn['parity_type'] = 'x'

	# set cksum algorithm (if needed)
	if( params['c'] != None ):
		rtn['cksum_algo'] = string.upper(params['c'][0])

	# make the code a bit more readable
	if( params['v'] != None ):
		rtn['verbose'] = params['v']
	if( params['V'] != None ):
		rtn['verbose'] += 10*params['V']

	# log to file?
	if( params['L'] != None ):
		rtn['log_file'] = params['L'][0]

	# pass the command through
	rtn['command'] = params['command'][0]

	# pass any filenames through
	rtn['file_list'] = params['filelist']

	return rtn


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def main():
	# parse the command-line arguments (starts with DefaultOpts() )
	opts = ParseCommandLineArguments()

	# open the log (to either stdout or file)
	logger.openLog( opts )

	# parse the opts file
	#if( opts['opts_file'] != None ):
	#	opts = read_config_file( opts['opts_file'], opts )

	err = -200
	command = opts['command']

	if( command == 'create' ):
		# create cksum-data for a file
		infile = opts['file_list'][0]
		chkfile = utils.calc_chk_filename( infile, opts )
		err = filerepair.create_from_file( infile, chkfile, opts )

	elif( command == 'verify' ):
		# to verify a file, we need a cksum-file to compare to
		infile = opts['file_list'][0]
		if( len(opts['file_list']) >= 2 ):
			chkfile = opts['file_list'][1]
		else:
			chkfile = utils.calc_chk_filename( infile, opts )
		err = filerepair.verify_file( infile, chkfile, opts )

	elif( command == 'repair' ):
		# to repair a file, we need a cksum-file to compare to
		infile = opts['file_list'][0]
		if( len(opts['file_list']) >= 2 ):
			chkfile = opts['file_list'][1]
		else:
			chkfile = utils.calc_chk_filename( infile, opts )
		if( len(opts['file_list']) >= 3 ):
			repfile = opts['file_list'][2]
		else:
			repfile = utils.calc_rep_filename( infile, opts )
		err = filerepair.repair_file( infile, chkfile, repfile, opts )

	elif( command == 'createall' ):
		# create cksum-data for all files in dir (per opts file)
		utils.go_nice( opts )
		inpath = opts['file_list'][0]
		def cmd_create( infile, _opts ):
			chkfile = utils.calc_chk_filename( infile, _opts )
			err = filerepair.create_from_file( infile, chkfile, _opts )
			return err

		err = utils.walk_directory_tree( inpath, opts, cmd_create )

	elif( command == 'verifyall' ):
		# verify all files in a dir (per opts file)
		utils.go_nice( opts )
		inpath = opts['file_list'][0]
		def cmd_verify( infile, _opts ):
			chkfile = utils.calc_chk_filename( infile, _opts )
			err = filerepair.verify_file( infile, chkfile, _opts )
			return err

		err = utils.walk_directory_tree( inpath, opts, cmd_verify )

	elif( command == 'repairall' ):
		# repair all files in a dir (per opts file)
		utils.go_nice( opts )
		inpath = opts['file_list'][0]
		def cmd_repair( infile, _opts ):
			chkfile = utils.calc_chk_filename( infile, _opts )
			repfile = utils.calc_rep_filename( infile, _opts )
			err = filerepair.repair_file( infile, chkfile, repfile, _opts )
			return err

		err = utils.walk_directory_tree( inpath, opts, cmd_repair )

	elif( command == 'updateall' ):
		# create or verify all files in a dir (per opts file)
		utils.go_nice( opts )
		inpath = opts['file_list'][0]
		def cmd_update( infile, _opts ):
			chkfile = utils.calc_chk_filename( infile, _opts )
			# if cksum file exists, then verify it
			if( file_exists(chkfile) ):
				err = filerepair.verify_file( infile, chkfile, _opts )
			# else create it
			else:
				err = filerepair.create_from_file( infile, chkfile, _opts )
			return err

		err = utils.walk_directory_tree( inpath, opts, cmd_update )

	else:
		# shouldn't be able to get here!
		print( "* Error: unknown command" )
		err = -100

	# close/clean-up the log file
	logger.closeLog()

	exit( err )

if __name__ == '__main__':
	main()
