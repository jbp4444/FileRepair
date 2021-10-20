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

import time

logToFile = False
logFilename = "default.log"
logFilePointer = 0

def openLog( opts ):
	global logToFile, logFilename, logFilePointer
	if( 'log_file' in opts ):
		if( opts['log_file'] == 'stdout' ):
			logToFile = False
			logFilename = 'stdout'
		else:
			logToFile = True
			logFilename = opts['log_file']

	if( logToFile ):
		try:
			logFilePointer = open( logFilename, "a" )
		except:
			# TODO: throw a real error message here
			print( "** ERROR: cannot open file [%s]"%(logFilename) )

	printLog( "starting fileraid logger" )

def closeLog():
	printLog( "closing fileraid logger" )
	if( logToFile ):
		logFilePointer.close()

def printLog( message ):
	tstamp = time.strftime( "%Y-%m-%d %H:%M:%S | " )
	if( logToFile ):
		logFilePointer.write( tstamp+message+"\n" )
	else:
		print( tstamp+message )

