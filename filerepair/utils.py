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


import string
import fnmatch
import os

def DefaultOpts():
	opts = {
		# basic config options:
		'num_parity_disks': 1,
		'block_size': 4096,
		'cksum_algo': 'SHA1',
		'parity_type': 'i',

		# assume no options-file
		'opts_file': None,

		# one master location, per-directory, or per-file?
		'output_master': False,
		'output_master_dir': '~',
		'output_perdir': False,
		'output_perdir_dir': '.fr',

		# what to include/exclude?
		'files_default': 'include',
		# .. exclude all except these .. (comma-sep list)
		'files_incl': '*',
		# .. include all except these .. (comma-sep list)
		'files_excl': '*.fr',
		'dirs_default': 'exclude',
		'dirs_incl': '*',
		'dirs_excl': '.fr',

		# prepend/append something for the output/cksum filename
		'output_pre': '',
		'output_app': '.fr',

		# prepend/append something for the repaired filename
		'repair_pre': '',
		'repair_app': '.rep',

		# send output to a log file?
		'log_file': 'stdout',

		# nice-level for '*all' commands?
		'nice': 0,

		# verbosity of output
		'verbose': 0
	}
	return opts

def go_nice( opts ):
	if( int(opts['verbose']) > 10 ):
		print( "running in 'nice' mode .." + opts['nice'] )
	# for Unix, this is easy:
	os.nice( int(opts['nice']) )
	# TODO: will want something similar for Windows
	# e.g. http://stackoverflow.com/questions/13937199/nicing-a-running-python-process

def read_config_file( file, opts ):
	try:
		f = open( file, 'rb' )
		for line in f:
			txt = string.strip(line)
			if( txt[0] == '#' ):
				continue
			flds = string.split( txt, '=' )
			if( opts[flds[0]] != None ):
				if( type(opts[flds[0]]) is bool ):
					opts[flds[0]] = convert_from_tfyn( flds[1] )
				elif( type(opts[flds[0]]) is int ):
					opts[flds[0]] = int(flds[1])
				elif( type(opts[flds[0]]) is str ):
					opts[flds[0]] = flds[1]
		f.close()
	except Exception as e:
		print( "Exception caught: "+str(e) )
		return None
	return opts

def file_exists( file ):
	# TODO: does this work on Windows?
	rtn = os.path.isfile( file )
	return rtn

def is_filename_match( filename, config ):
	if( config['files_default'] == 'include' ):
		should_process = True
		list = string.split( config['files_excl'], ',' )
		for pattern in list:
			if( fnmatch.fnmatch(filename,pattern) ):
				should_process = False
				break
	else:
		should_process = False
		list = string.split( config['files_incl'], ',' )
		for pattern in list:
			if( fnmatch.fnmatch(filename,pattern) ):
				should_process = True
				break

	return should_process

def is_directory_match( dirname, config ):
	if( config['dirs_default'] == 'include' ):
		should_process = True
		list = string.split( config['dirs_excl'], ',' )
		for pattern in list:
			if( fnmatch.fnmatch(dirname,pattern) ):
				should_process = False
				break
	else:
		should_process = False
		list = string.split( config['dirs_incl'], ',' )
		for pattern in list:
			if( fnmatch.fnmatch(dirname,pattern) ):
				should_process = True
				break

	return should_process

def walk_directory_tree( inpath, opts, command ):
	err_count = 0

	for curdir, subdirs, files in os.walk(inpath):
		#print( "walking directory ["+curdir+"]")
		if( is_directory_match(curdir,opts) ):
			for infile in files:
				#print( "checking file ["+infile+"]" )
				infile_full = os.path.join( curdir, infile )
				if( is_filename_match(infile_full,opts) ):
					#print( "  processing" )
					err = command( infile_full, opts )
					# TODO: verify this is an error, only count errors
					#       (not sum error-return codes)
					err_count = err_count + err

		tmplist = [ d for d in subdirs ]
		for d in tmplist:
			testdir = os.path.join( curdir, d )
			#print( "checking dir ["+d+"]  ["+testdir+"]" )
			if( is_directory_match(testdir,opts) == False ):
				# remove this from the list, we don't want to recurse here
				#print( "  removing dir ["+d+"]" )
				subdirs.remove( d )

	return err_count

# Assumes infile is a "full" relative path (from top of local tree)
def calc_chk_filename( infile, config ):
	chkfile = infile
	if( convert_from_tfyn(config['output_master']) == True ):
		chkfile = config['output_master_dir'] + config['output_pre'] + infile + config['output_app']
		(dname,fname) = os.path.split( chkfile )
		try:
			os.makedirs( dname )
		except:
			# TODO: verify that this is an ignore-able error
			pass
	elif( convert_from_tfyn(config['output_perdir']) == True ):
		(dname,fname) = os.path.split( infile )
		chkfile = dname + "/" + config['output_perdir_dir'] + config['output_pre'] + fname + config['output_app']
		try:
			os.makedirs( dname + "/" + config['output_perdir_dir'] )
		except:
			# TODO: verify that this is an ignore-able error
			pass
		pass
	else:
		chkfile = config['output_pre'] + infile + config['output_app']
	#print( "infile ["+infile+"]  chkfile ["+chkfile+"]" )
	return chkfile

def calc_rep_filename( infile, config ):
	repfile = config['repair_pre'] + infile + config['repair_app']
	return repfile

def convert_from_tfyn( text ):
	rtn = None
	if( type(text) is bool ):
		rtn = text
	elif( type(text) is str ):
		txt = string.lower(text)
		txt = txt[0]
		if( (txt=='y') or (txt=='t') ):
			rtn = True
		elif( (txt=='n') or (txt=='f') ):
			rtn = False
		else:
			#assert True, 'Cannot parse input text'
			rtn = None
	return rtn

def convert_from_kmgt( intxt ):
	rtn = -1
	txt = string.lower( intxt )
	ik = string.find( txt, 'k' )
	im = string.find( txt, 'm' )
	ig = string.find( txt, 'g' )
	it = string.find( txt, 't' )
	if( (ik<0) and (im<0) and (ig<0) and (it<0) ):
		rtn = int( txt )
	elif( ik >= 0 ):
		rtn = int( txt[0:ik] ) * 1024
	elif( im >= 0 ):
		rtn = int( txt[0:im] ) * 1024*1024
	elif( ig >= 0 ):
		rtn = int( txt[0:ig] ) * 1024*1024*1024
	elif( it >= 0 ):
		rtn = int( txt[0:it] ) * 1024*1024*1024*1024
	return rtn

def convert_to_kmgt( inval ):
	rtn = ''
	if( inval >= (1024*1024*1024*1024) ):
		rtn = str(inval/(1024*1024*1024*1024)) + "TB"
	elif( inval >= (1024*1024*1024) ):
		rtn = str(inval/(1024*1024*1024)) + "GB"
	elif( inval >= (1024*1024) ):
		rtn = str(inval/(1024*1024)) + "MB"
	elif( inval >= (1024) ):
		rtn = str(inval/(1024)) + "KB"
	else:
		rtn = str(inval) + "B"
	return rtn

def read_bytearray_file( file ):
	try:
		f = open( file, 'rb' )
		data = bytearray( f.read() )
		f.close()
	except:
		return None
	return data

def write_bytearray_file( file, data ):
	try:
		f = open( file, 'wb' )
		f.write( data )
		f.close()
	except Exception as e:
		print( "** ERROR: cannot write file: "+str(e) )
		return 1
	return 0

def bitnum_to_byte( idx ):
	byte_num  = int( idx / 8 )
	bit_num   = 7 - (idx % 8)
	byte_mask = 1 << bit_num
	return (byte_num,bit_num,byte_mask)

def showbits( n ):
	txt = ''
	mask = 0x80
	for i in range(0,8):
		#print i,mask,n,n&mask,txt
		if( (n&mask) > 0 ):
			txt = txt + '1'
		else:
			txt = txt + '0'
		mask >>= 1
	return txt

def to_binarray( n, nplaces=64 ):
	fmt = '0'+str(nplaces)+'b'
	rtn = [ int(i) for i in format(n,fmt) ]
	return rtn

# found on stackoverflow
def count_ones_bits( n ):
	return bin(n).count("1")

# from: http://stackoverflow.com/questions/15285534/isprime-function-for-python-language
def is_prime(n):
  if n == 2 or n == 3: return True
  if n < 2 or n%2 == 0: return False
  if n < 9: return True
  if n%3 == 0: return False
  r = int(n**0.5)
  f = 5
  while f <= r:
    #print '\t',f
    if n%f == 0: return False
    if n%(f+2) == 0: return False
    f +=6
  return True

# http://code.activestate.com/recipes/577514-chek-if-a-number-is-a-power-of-two/
#Author: A.Polino
def is_power2(num):
	return num!=0 and ((num & (num - 1)) == 0)

def intRoundDown( num, denom ):
	return int( (num + denom - 1)/denom )
