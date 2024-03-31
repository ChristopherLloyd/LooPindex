import snappy #gives annoying deprecation warning every time
import sys

link = sys.argv[1]
if '[' in link:
    link = eval( link )
LE = snappy.Link( link ).view()
code = LE.PD_code()

f = open( sys.argv[2], 'w' )

f.write( str( code ) )
f.close()
#print( "hi" )
LE.done()

