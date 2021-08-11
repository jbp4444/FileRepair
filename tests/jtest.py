
import sys

import filerepair

if __name__ == '__main__':
	fname = sys.argv[1]

	opts = filerepair.utils.DefaultOpts()

	rtn = filerepair.create_from_file( fname, None, opts )

	if( rtn is None ):
		print( "* Error: cannot create cksum/parity info" )
	else:
		print( str(rtn) )
