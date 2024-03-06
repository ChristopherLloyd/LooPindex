#import lightrdf
#import gzip
#import rdflib
from random import *
import traceback
import warnings
#import re
#from math import sqrt
import snappy
from itertools import chain, combinations

ALPHABET = "abcdefghijklmnopqrstuvwxyz"*5 # generator alphabet, used for readable output only. Inverses are upper case
    
def main():
    print( "small change" )
    print( "small change from windows" )
    print( "another small change from windows" )
    
    #pd = drawLoop()
    #print( pd )
    test9()

def test10():
    """Another function to compute pinning sets of drawn loops"""


    #link = 'K14a4'
    #mona lisa loop:
    link = [(24, 6, 1, 5), (3, 10, 4, 11), (1, 13, 2, 12), \
            (6, 14, 7, 13), (2, 17, 3, 18), (8, 15, 9, 16), \
            (11, 19, 12, 18), (4, 20, 5, 19), (7, 23, 8, 22),\
            (9, 20, 10, 21), (14, 24, 15, 23), (16, 21, 17, 22)]
    # 8 crossing loop with no embedded monorbigons
    #link = [(1, 7, 2, 6), (3, 8, 4, 9), (5, 11, 6, 10), (16, 12, 1, 11), \
    #        (2, 13, 3, 14), (4, 16, 5, 15), (7, 12, 8, 13), (9, 15, 10, 14)]
    # another equivalent one:
    #link = [(11,16,12,1),(13,3,14,2),(8,4,9,3),(15,4,16,5),(10,5,11,6),(1,7,2,6),(12,8,13,7),(9,15,10,14)]

    # a 9 crossing example; cycle 0, 1 and 4 times to see small discrepancy
    #link = [(1, 7, 2, 6), (4, 9, 5, 10), (2, 12, 3, 11),\
    #        (7, 13, 8, 12), (18, 13, 1, 14), (3, 17, 4, 16),\
    #        (5, 14, 6, 15), (8, 18, 9, 17), (10, 15, 11, 16)]
    
    drawnpd = plinkPD( link )
    
    # do this cycling to make sure pinset behavior is preserved for different PD codes
    offset = 0
    for i in range( offset ):
        link = drawnpd
        drawnpd = plinkPD( drawnpd )

    minOnly = True
    debug = True
    pinsets = pinSets( drawnpd, debug = debug, minOnly = minOnly )
    if minOnly:
        print( "Minimal pinning sets:" )
    minlen = len( pinsets[0] )
    for elt in pinsets[0]:
        if minOnly or debug:
            print( elt )
        if len( elt ) < minlen:
            minlen = len( elt )
    #print( "MinOnly:", minOnly )
    print()
    if minOnly:
        print( "Number of minimal pinning sets:", len( pinsets[0] ) )
    print( "Number of total pinning sets:", pinsets[1] )
    print( "Pinning number:", minlen )
    print()
    print( "Input PD:", link )
    print( "Drawn PD:", drawnpd )
    #plinkFromPD( link )

def test9():
    """Debugging the 9-crossing loop having different behavior for different spanning trees"""
    # a 9 crossing example; cycle 0, 1 and 4 times to see small discrepancy
    link = [(1, 7, 2, 6), (4, 9, 5, 10), (2, 12, 3, 11),\
            (7, 13, 8, 12), (18, 13, 1, 14), (3, 17, 4, 16),\
            (5, 14, 6, 15), (8, 18, 9, 17), (10, 15, 11, 16)]
    drawnpd = plinkPD( link )

    print( "Input PD:", link )
    print( "Drawn PD:", drawnpd )

    # For debugging 9-crossing monorbigon-free example with PD_offset 0
    # toggle between baseRegion = 16898 ( naivePinSets: 374, recursivePinsets: 347 )
    # and baseRegion = 270864 ( naivePinSets: 395, recursivePinsets: 395 )
    base1 = 16898
    base2 = 270864
    # base2 is the infinite region, so we always try to rewrite from there
    # however the answer should not depend on spanning tree (specified by treeBase)
    print( "All pinsets rel treeBase=", base1, ":" )
    allpinsets1, naive1 = pinSets( drawnpd, debug = True, minOnly = False, treeBase = base1, rewriteFrom = base2 )
    print()
    
    print( "All pinsets rel treeBase=", base2, ":" )
    allpinsets2, naive2 = pinSets( drawnpd, debug = True, minOnly = False, treeBase = base2, rewriteFrom = base2 )
    print()
    
    print( "Min pinsets rel treeBase=", base1, ":" )
    minpinsets1 = pinSets( drawnpd, debug = True, minOnly = True, treeBase = base1, rewriteFrom = base2 )[0]
    print()
    
    print( "Min pinsets rel treeBase=", base2, ":" )
    minpinsets2 = pinSets( drawnpd, debug = True, minOnly = True, treeBase = base2, rewriteFrom = base2 )[0]
    print()

    print( "Min1 is subset All1?", isSubset( minpinsets1, allpinsets1 ) )
    print( "Min2 is subset All2?", isSubset( minpinsets2, allpinsets2 ) )
    print( "All1 is subset Naive1?", isSubset( allpinsets1, naive1 ) )
    print( "All2 is subset Naive2?", isSubset( allpinsets2, naive2 ) )
    print( "All1 cap Min2 is a subset of Min1", isSubset( intersection( allpinsets1, minpinsets2), minpinsets1 ) )
    print( "#Naive1\\(Min2 cup All1)", len( difference( naive1, union( minpinsets2, allpinsets1 ) ) ) )
    print( "#All1\\Naive1", len( difference( allpinsets1, naive1 ) ) )
    print( "#Naive1\\All1", len( difference( naive1, allpinsets1 ) ) )
    print( "#Min1\\#Min2:", len( difference( minpinsets1, minpinsets2 ) ) )
    print( "#Min2\\#Min1:", len( difference( minpinsets2, minpinsets1 ) ) )
    print( "#Min2\\#All1:", len( difference( minpinsets2, allpinsets1 ) ) )
    print( "#Min2\\#Naive1:", len( difference( minpinsets2, naive1 ) ) ) 

    print( "Discrepancies follow..." )
    print()

    badcount = 0
    for elt in naive2:
        # base2 is the infinite region, so we always try to rewrite from there
        dataBase1 = testSi( drawnpd, elt, treeBase = base1, rewriteFrom = base2 )
        dataBase2 = testSi( drawnpd, elt, treeBase = base2, rewriteFrom = base2 )
        #return {"gamma.si( T.orderDict )":gamma.si( T.orderDict ), \
        #    "rep.si( T.orderDict )":rep.si( T.orderDict ), \
        #   "rep":rep, "newRewriteFrom":newRewriteFrom, \
        #    "gamma":gamma, "T.orderDict":T.orderDict, "T.order":T.order}
        if dataBase1["gamma.si( T.orderDict )"] != dataBase1["rep.si( T.orderDict )"]\
           or dataBase2["gamma.si( T.orderDict )"] != dataBase2["rep.si( T.orderDict )"]:
            testSi( drawnpd, elt, treeBase = base1, rewriteFrom = base2, verbose = True )
            testSi( drawnpd, elt, treeBase = base2, rewriteFrom = base2, verbose = True )

            
            print( "Considering pinset:", elt, "(size", len(elt), ")" )
            print()
            print( "  Relative to treeBase=", base1, " and rewriteFrom=", dataBase1["newRewriteFrom"], " we have:" )
            print( "  gamma=", dataBase1["gamma"] )
            print( "  gamma(pinset,rewriteFrom)=", dataBase1["rep"] )
            print( "  si(gamma,{},rewriteFrom)=", dataBase1["gamma.si( T.orderDict )"],\
                   ",\tsi(gamma,pinset,rewriteFrom)=", dataBase1["rep.si( T.orderDict )"] )
            print( "  T(treeBase).orderDict=", dataBase1["T.orderDict"] )
            print( "  T(treeBase).order=", Word(dataBase1["T.order"]) )
            
            if base2 != dataBase1["newRewriteFrom"]:
                print( "  rewriteFrom=", base2, "was to be filled, so it was modified as above." )
    
            print()
            print( "  Relative to treeBase=", base2, " and rewriteFrom=", dataBase2["newRewriteFrom"], " we have:" )
            print( "  gamma=", dataBase2["gamma"] )
            print( "  gamma(pinset,rewriteFrom)=", dataBase2["rep"] )
            print( "  si(gamma,{},rewriteFrom)=", dataBase2["gamma.si( T.orderDict )"],\
                   ",\tsi(gamma,pinset,rewriteFrom)=", dataBase2["rep.si( T.orderDict )"] )
            print( "  T(treeBase).orderDict=", dataBase2["T.orderDict"] )
            print( "  T(treeBase).order=", Word(dataBase2["T.order"]) )
            if base2 != dataBase2["newRewriteFrom"]:
                print( "  rewriteFrom=", base2, "was to be filled, so it was modified as above." )
            
            print()
            badcount += 1
       
        #if :
        #    print( "Considering pinset:", elt )
            
        #    print()
        #    badcount += 1
    print( "Total discrepancies:", badcount )
    #print( "\nPinning sets in second not in first:" )
    #for elt in difference( pinsets2, pinsets1 ):
    #    print( "Considering pinset:", elt )
    #    print( "Relative to", base1, "we have", testSi( drawnpd, elt, baseRegion = base1 ) )
    #    print( "Relative to", base2, "we have", testSi( drawnpd, elt, baseRegion = base2 ) )
    #    print()

    return
    
    print( "Pinning sets in first not in second:" )
    for elt in difference( pinsets1, pinsets2 ):
        print( "Considering pinset:", elt )
        print( "Relative to", base1, "we have", testSi( drawnpd, elt, baseRegion = base1 ) )
        print( "Relative to", base2, "we have", testSi( drawnpd, elt, baseRegion = base2 ) )
        print()
    print( "\nPinning sets in second not in first:" )
    for elt in difference( pinsets2, pinsets1 ):
        print( "Considering pinset:", elt )
        print( "Relative to", base1, "we have", testSi( drawnpd, elt, baseRegion = base1 ) )
        print( "Relative to", base2, "we have", testSi( drawnpd, elt, baseRegion = base2 ) )
        print()

    # grab the pinset of size 4 that pins loop 2 but not loop 1
    #special = difference( pinsets2, pinsets1 )[1]
    #print(  )

    # double check that it doesnt pin loop1

    

    

def test8():
    """Demonstrates PD code discrepancy with the Mona Lisa loop and 9 crossing loop.
    Also illustrates 'correct' use of which PD to feed to snappy
    vs our algorithm"""


    #link = 'K14a4'
    #mona lisa loop:
    link = [(24, 6, 1, 5), (3, 10, 4, 11), (1, 13, 2, 12), \
            (6, 14, 7, 13), (2, 17, 3, 18), (8, 15, 9, 16), \
            (11, 19, 12, 18), (4, 20, 5, 19), (7, 23, 8, 22),\
            (9, 20, 10, 21), (14, 24, 15, 23), (16, 21, 17, 22)]
    # 8 crossing loop with no embedded monorbigons
    link = [(1, 7, 2, 6), (3, 8, 4, 9), (5, 11, 6, 10), (16, 12, 1, 11), \
            (2, 13, 3, 14), (4, 16, 5, 15), (7, 12, 8, 13), (9, 15, 10, 14)]
    # another equivalent one:
    #link = [(11,16,12,1),(13,3,14,2),(8,4,9,3),(15,4,16,5),(10,5,11,6),(1,7,2,6),(12,8,13,7),(9,15,10,14)]
    # The algorithm is finding a consistent pinning poset for this loop
    #link= rawPDtoPlinkPD( link )

    # a 9 crossing example; cycle 0, 1 and 4 times to see small discrepancy
    link = [(1, 7, 2, 6), (4, 9, 5, 10), (2, 12, 3, 11),\
            (7, 13, 8, 12), (18, 13, 1, 14), (3, 17, 4, 16),\
            (5, 14, 6, 15), (8, 18, 9, 17), (10, 15, 11, 16)]
    drawnpd = plinkPD( link )
    #link.sort()
    #print( "original:", link )
    #print()

    #link1 = plinkPD( link )
    
    # do this cycling to make sure pinset behavior is preserved for different PD codes
    offset = 0
    for i in range( 5 ):
        link = drawnpd
        drawnpd = plinkPD( drawnpd )
        
        #link.sort()
        #print( i, ":", link )
    #   print()
       
    #return
    #print( rawPDtoPlinkPD( plinkPDtoRawPD( link ) ) )
    #print( plinkPDtoRawPD( rawPDtoPlinkPD( link ) ) )
    #print( plinkPDtoRawPD( plinkPDtoRawPD( rawPDtoPlinkPD( link ) ) ) )
    #print( rawPDtoPlinkPD( link ) )
    #print( rawPDtoPlinkPD( link ) )
    #plinkFromPD( link )
    #print( hackyPD( link ) )
    #plink( link1 )
    #return
    #link = '6_1'
    
    # the tests below all go faster than before
    #link = 'K14n1'
    #link = '10_24' # not showing minimal pinsets only? is computing ALL pinsets correctly by naive check
    #link = 'K11a340' #takes about 30 seconds to run
    #link = 'K11n100' #takes about a minute to run
    #pinSets( link, debug = True )

    # For debugging 9-crossing monorbigon-free example with PD_offset 0
    # toggle between baseRegion = 16898 ( naivePinSets: 374, recursivePinsets: 347 )
    # and baseRegion = 270864 ( naivePinSets: 395, recursivePinsets: 395 )
    
        pinsets = pinSets( drawnpd, debug = False )#, treeBase = 270864 )#, rewriteFrom = 270864 )
        #print( pinsets )
        minlen = len( pinsets[0] )
        for elt in pinsets:
            print( elt )
            if len( elt ) < minlen:
                minlen = len( elt )
        print()
        print( "Number of minimal pinning sets:", len( pinsets ) )
        print( "Pinning number:", minlen )
        print()
        print( "PD_code offset:", offset )
        print( "Input PD:", link )
        print( "Drawn PD:", drawnpd )

    #plinkFromPD( link )
    
####################### DATABASE FUNCTIONS ####################################

# These functions are failing to capture the general behavior of how snappy messes with PD codes
# I can't figure out the exact relationship between
def rawPDtoPlinkPD( link ):
    """Gets the PD code for a snappy link that is displayed when
    drawing the link using snappy.plink.
    Input can be a string or a list"""
    #assert( type( link ) == str )
    pd_in = snappy.Link( link ).PD_code()
    edgeLength = len(pd_in)*2
    pd_out = []
    for i in range( len( pd_in ) ):
        cycle = []
        for j in pd_in[i]:
            if j == 1:
                cycle.append( edgeLength )
            else:
                cycle.append( (j-1)%edgeLength )
        pd_out.append( cycle )
    return pd_out

def plinkPDtoRawPD( link ):
    """Gets the raw PD code associated to a plink PD (inverse of function above)"""
    #pd_in = snappy.Link( link ).PD_code()
    assert( type( link ) == list )
    edgeLength = len( link )*2
    pd_out = []
    for i in range( len( link ) ):
        cycle = []
        for j in link[i]:
            if j == edgeLength - 2:
                cycle.append( edgeLength )
            else:
                cycle.append( (j+2)%edgeLength )
        pd_out.append( cycle )
    return pd_out
    

def plinkPD( link ):
    LE = snappy.Link( link ).view()
    code = LE.PD_code()
    LE.done()
    return code

def plinkFromStr( link ):
    assert( type( link ) == str )
    snappy.Link( link ).view()

def plinkFromPD( link ):
    assert( type( link ) == list )
    snappy.Link( link ).view()    

def drawLoop():
    M = snappy.Manifold()
    #while str( M ) == "Empty Triangulation":
    input( "Draw loop and send to snappy. Press any key when finished." )
    return M.getPDcode()

def SurfaceGraphFromPD( pd ):
    sigma = pd
    coordsDict = {}
    for i in range( len( sigma ) ):
        for j in range( len( sigma[i] ) ):
            try:
                coordsDict[ sigma[i][j] ].append( [i,j] )
            except KeyError:
                coordsDict[ sigma[i][j] ] = []
                coordsDict[ sigma[i][j] ].append( [i,j] )

    def regionFromCoords( coords ):
        startEdge = sigma[coords[0]][coords[1]]
        reg = [startEdge]
        #print( sigma[coords[0]][coords[1]] )
        while True:
            # depending on PD code convention, may need to
            # subtract or add from index here
            # to match clockwise/counterclockwise convention
            nextEdge = sigma[coords[0]][(coords[1]-1)%4 ]
            if nextEdge == startEdge:
                break
            reg.append( nextEdge )
            for cordChoice in coordsDict[nextEdge]:
                if coords[0] != cordChoice[0]:
                    coords = cordChoice
                    break
        return reg   

    #create dual graph 
    edgeDict = {}

    #print( pd )
    #print() 
    #print( coordsDict )

    # define left and right relative to the first segment
    # you want to start at the cycle containing 1 but not containing 2

    if coordsDict[1][0][0] == coordsDict[2][0][0] or coordsDict[1][0][0] == coordsDict[2][1][0]:
        curLeftCoords = coordsDict[1][0] 
        curRightCoords = coordsDict[1][1]
    else:
        curLeftCoords = coordsDict[1][1] 
        curRightCoords = coordsDict[1][0]   
    
    regDict = {}
    indexDict = {}

    for i in range( 1, len( sigma )*2+1 ): # this is the number of segments in the loop
        # we must check whether regions on left and right of this edge exist yet
        # make a choice for left and right based on the previous

        curLeftRegion = regionFromCoords( curLeftCoords )
        curRightRegion = regionFromCoords( curRightCoords )

        leftkey = binHash( curLeftRegion )
        rightkey = binHash( curRightRegion )
        
        try:
            regDict[leftkey]
        except KeyError:
            eltToIndex = {}
            for j in range( len(curLeftRegion) ):
                eltToIndex[curLeftRegion[j]] = j
            regDict[leftkey] = curLeftRegion
            indexDict[leftkey] = eltToIndex

        try:
            regDict[rightkey][indexDict[rightkey][i]] *= -1 # right region sees this edge negative
        except KeyError:
            eltToIndex = {}
            for j in range( len(curRightRegion) ):
                eltToIndex[curRightRegion[j]] = j
            regDict[rightkey] = curRightRegion
            indexDict[rightkey] = eltToIndex
            regDict[rightkey][indexDict[rightkey][i]] *= -1
        edgeDict[i] = [ leftkey , rightkey ]

        if i == len( sigma )* 2:
            break
        
        if sigma[curLeftCoords[0]] == sigma[ coordsDict[i+1][1][0] ] or sigma[curRightCoords[0]] == sigma[ coordsDict[i+1][0][0] ]:
            curLeftCoords, curRightCoords = coordsDict[i+1][0], coordsDict[i+1][1]
        else:
            curLeftCoords, curRightCoords = coordsDict[i+1][1], coordsDict[i+1][0]

    return SurfaceGraph( regDict, adjDict = edgeDict )
    

def readPlanarDiagram( knot ):
    """returns the planar diagram presentation of a knot with
    at most 11 crossings from Rolfsen/Hoste/Thistlethwaite tables.
    Knots under eleven crossings should be of the form 'x_y' for integers x
    and y. Knots with eleven crossings should be of the form 'Kxay' or Kxny'
    where the n or a stands for alternating or non-alternating."""
    
    assert( type( knot ) == str )
    notfound = "Knot '"+knot+"' not found in database."
    if ( len( knot ) < 3 ): #could pattern match here to save more time
        warnings.warn( notfound )
        return None 
    try:
        firstLetter = int( knot[0] )
    except ValueError:
        firstLetter = knot[0]
        if firstLetter != 'K': #could pattern match here to save more time
            warnings.warn( notfound )
            return None

    if type( firstLetter ) == int:
        file = 'knotdata/Rolfsen.rdf'
    else:
        file = 'knotdata/Knots11.rdf'

    f = open( file, 'r' )
    key = "<knot:"+knot+">"
    for line in f.readlines():
        data = line.split()[:2]
        if data[0]==key and data[1] == "<invariant:PD_Presentation>":
            f.close()
            data = line.split( "\"")[1].split("sub")
            sigma = []
            for i in range( 1, len( data ), 2 ):
                data[i] = data[i][1:-2]
                if "," in data[i]:
                    toAdd = []
                    for elt in data[i].split( "," ): 
                        toAdd.append( int( elt ) )
                    assert( len( toAdd ) == 4 )
                    sigma.append( toAdd )
                else:
                    toAdd = []
                    for elt in data[i]:
                        toAdd.append( int( elt ) )
                    assert( len( toAdd ) == 4 )
                    sigma.append( toAdd )
            
            return sigma
    f.close()
    warnings.warn( notfound )
    return None

####################### OTHER GENERALLY USEFUL FUNCTIONS ####################################
def intersection( list1, list2 ):
    """Returns a list of all elements from list1 and list2"""
    toReturn = []
    for elt in list1:
        if elt in list2 and not elt in toReturn:
            toReturn.append( elt )
    return toReturn

def union( list1, list2 ):
    """Returns a list of elements from list1 or list2"""
    toReturn = []
    for elt in list1:
        if not elt in toReturn:
            toReturn.append( elt )
    for elt in list2:
        if not elt in toReturn:
            toReturn.append( elt )
    return toReturn
    

def difference( list1, list2 ):
    """Returns a list of all elements in list1 and not in list2"""
    toReturn = []
    for elt in list1:
        if not elt in list2 and not elt in toReturn:
            toReturn.append( elt )
    return toReturn

def isSubset( list1, list2 ):
    """Returns True if and only if every element of list1 is in list2"""
    return len( difference( list2, list1 ) ) == len( list2 ) - len( list1 )

def powerset(iterable):
    """
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    stolen from https://stackoverflow.com/questions/374626/how-can-i-find-all-the-subsets-of-a-set-with-exactly-n-elements
    for a 'naive check' of the pinset function
    """
    xs = list(iterable)
    # note we return an iterator rather than a list
    return chain.from_iterable(combinations(xs,n) for n in range(len(xs)+1))

def randomWord( n, m, s = None ):
    """Returns a random (unreduced) word of length n on m generators. s is random seed"""
    a = []
    if s is not None:
        seed( a=s )
    for i in range( n ):
        a.append( (randint( 0,1 )*2-1)*randint( 1, m ) )
    return Word( a )

def sign(i,j):
    """Returns 1 if i<j, 0 if i=j, -1 if i>j"""
    return int(i!=j)*(int(i<j)*2-1)

def cord(i,j,k):
    """returns 1, -1, or 0 according to the cyclic order of i,j, and k in (-inf,inf)
    e.g. cord(-1,2,3)=cord(3,1,2)=1, cord(2,1,3)=-1, cord(2,2,3)=cord(3,3,3)=0
    works for any data types with '=' and '<' operators"""
    return sign(i,j)*sign(j,k)*sign(i,k)

def binHash( distinctNatList ):
    """Given a list A of distinct nonnegative integers, computes a large integer
    which encodes the elements present and serves as a hash key for the
    corresponding set of naturals+0
    WILL NOT WORK PROPERLY IF GIVEN LISTS OF NONDISTINCT INTEGERS."""

    hashkey = 0
    for elt in distinctNatList:
        hashkey += 2**elt
    return hashkey

def binSet( num ):
    """Returns set of indices where a binary number is nonzero"""
    indexSet = set()
    i = 0
    while num != 0:
        if num%2 != 0:
            indexSet.add( i )
        i += 1
        num >>= 1
    return indexSet    

def listToDict( a ):
    """Converts list to dictionary"""
    toRet = {}
    for i in range( len( a ) ):
        toRet[i] = a[i]
    return toRet

def getKey( a ):
    """Returns some key from a dictionary/set, or None if the dict/set is empty"""
    for key in a:
        return key
    return None


####################### COMPUTING PINSETS ####################################
def testSi( link, pinSet, treeBase = 0, rewriteFrom = 0, verbose = False):
    """Returns si(gamma) relative to all pins, and si(gamma) relative to the pins in pinSet
    using a spanning tree from treeBase and rewriting rule from rewriteFrom"""
    if type( link ) == list:
        G = SurfaceGraphFromPD( link )
    else:
        G = SurfaceGraphFromPD( plinkPD( link ) )
    #print( set( G.wordDict.keys() ) )
    T = G.spanningTree( treeBase )
    T.createCyclicGenOrder()
    gamma = T.genProd()
    unPinSet = set( T.wordDict.copy().keys() ).difference( pinSet )
    rep, newRewriteFrom = T.reducedWordRep( gamma, unPinSet, source = rewriteFrom )
    return {"gamma.si( T.orderDict )":gamma.si( T.orderDict ), \
            "rep.si( T.orderDict )":rep.si( T.orderDict, verbose = verbose ), \
           "rep":rep, "newRewriteFrom":newRewriteFrom, \
            "gamma":gamma, "T.orderDict":T.orderDict, "T.order":T.order}

def pinSets( link, minOnly = True, debug = False, treeBase = None, rewriteFrom = 0 ):
    """Returns the minimal pinning sets of a link"""
    if type( link ) == list:
        G = SurfaceGraphFromPD( link )
    else:
        G = SurfaceGraphFromPD( plinkPD( link ) )       

    
    T = G.spanningTree( baseRegion = treeBase )
    T.createCyclicGenOrder()
    gamma = T.genProd()
    #print( gamma )
    n = gamma.si( T.orderDict )

    #print( n )
    if debug:
        print( T )
        print()
    #plink( link )
    #print( T.wordDict )

    fullRegList = list( T.wordDict.copy().keys() )
    #fullRegList.sort()
    #fullRegDict = {}
    monorBigonSet = set()
    for key in T.wordDict:
        if len( G.wordDict[key] ) <= 2:
            monorBigonSet.add( key )
    #print( monorBigonSet )
    #return
    #i=0
    #for key in T.wordDict:
    #    fullRegDict[key]=i
    #    i+=1
    fullRegSet = set( fullRegList )
    numRegions = len( fullRegSet )
        
    #print( fullRegList )
    #print( type( fullRegSet ) )  

    def isPinning( regSet ):
        nonlocal rewriteFrom
        rep = T.reducedWordRep( gamma, fullRegSet.difference( regSet ), source = rewriteFrom )[0]
        return rep.si( T.orderDict ) == n        

    pinSets = []
    numPinSets = 0
    falseMins = {"superset":0,"subset":0 }

    def getPinSetsWithin( regSet, minOnly = True, minIndex = 0):
        nonlocal pinSets
        nonlocal numPinSets
        #nonlocal baseRegion
        #print( regSet, minIndex )
        #print( fullRegSet )
        if regSet != fullRegSet and not isPinning( regSet ):
            return False
        else:
            minimal = True
            nextSet = regSet.copy()
            for i in range( minIndex, numRegions ):
                if fullRegList[i] in monorBigonSet:
                    continue
                nextSet.remove( fullRegList[i] )
                if getPinSetsWithin( nextSet, minOnly = minOnly, minIndex = i+1 ):
                    minimal = False
                nextSet.add( fullRegList[i] )
            if minimal or not minOnly:
                superset = False
                #subsetIndices = set()
                newPinsets = []
                for i in range( len( pinSets ) ):
                    if pinSets[i].issubset( nextSet ):
                        superset = True
                        falseMins["superset"] += 1 #just for benchmarking purposes
                        break
                    #experimentally, this is not needed:
                    if not nextSet.issubset( pinSets[i] ):
                        newPinsets.append( pinSets[i] )
                

                #experimentally, this is not needed:
                if len( newPinsets ) != len( pinSets ) and not superset:
                    falseMins["subset"] += 1 #just for benchmarking purposes
                    pinSets = newPinsets                
                
                if not superset or not minOnly:
                    #print( "Adding", nextSet )
                    pinSets.append( nextSet )
            numPinSets += 1
            return True

    """def getPinSetsWithinOld( regSet, minOnly = True, minIndex = 0):
        #print( "hi" )
        print( regSet, minIndex )
        #print( fullRegSet )
        if regSet != fullRegSet and not isPinning( regSet ):
            return set()
        else:
            minsWithin = []
            nextSet = regSet.copy()
            for i in range( minIndex, numRegions ):
                nextSet.remove( fullRegList[i] )
                curmin = getPinSetsWithin( nextSet, minOnly = minOnly, minIndex = i+1 )
                nextSet.add( fullRegList[i] )
                if not curmin:
                    continue

                
                #print( "curmin:", curmin )
                #print()
                
                minimal = True
                for elt in minsWithin:
                    if elt.issubset( curmin ):
                        print( elt, curmin )
                        minimal = False
                if minimal:
                    #print( "Adding", curmin )
                    minsWithin.append( curmin )

                #print( "HELLLOOOO", minsWithin )

            if minsWithin == []:
                print( "regSet", regSet, "is minimal" )
                pinSets.append( nextSet )
                return regSet
            else:
                return minsWithin[0]"""

    def powerSetCheck( powerset ):
        nonlocal rewriteFrom
        """Naive O(exp) function for debugging purposes"""
        pinsets = []
        
        i = 0
        for subset in powerset( fullRegSet ):
            s = set( subset )
            if s == fullRegSet:
                continue
            rep = T.reducedWordRep( gamma, s, source = rewriteFrom )[0]
            if s != fullRegSet and rep.si( T.orderDict ) == n:
                pinsets.append( fullRegSet.difference( s ) )
            i+=1
        #print( "Total number of subsets:", i )
        return pinsets

    getPinSetsWithin( fullRegSet, minOnly = minOnly )

    naivePinSets = None

    if debug and not minOnly:
        #getPinSetsWithin( fullRegSet, minOnly = False )
        naivePinSets = powerSetCheck( powerset )
        print( "naivePinSets:", len( naivePinSets ) )
        print( "recursivePinsets:", len( pinSets ) )
        print( "#Naive\\Recursive=", len( difference( naivePinSets, pinSets ) ) )
        print( "#Recursive\\Naive=", len( difference( pinSets, naivePinSets ) ) )
        
        for elt in naivePinSets:        
            assert( elt in pinSets )
        for elt in pinSets:
            assert( elt in naivePinSets )
        assert( fullRegSet in pinSets )
    if debug and minOnly:
        print( "Minimal Pinsets:", len( pinSets ) )
        for i in range( len( pinSets ) ):
            for j in range( len( pinSets ) ):
                if i != j:
                    assert( not pinSets[i].issubset( pinSets[j] ) )
        #getPinSetsWithin( fullRegSet, minOnly = minOnly )
        #print( "minPinsets:", len( pinSets ) )

    #print( pinSets )
    #print( "False minimals sets:", falseMins )  
            
    #print( pinSets )
    #print()
    #print( naivePinSets )
    if debug:
        return pinSets, naivePinSets

    return pinSets, numPinSets
    

####################### DATA STRUCTURES ####################################

class SurfaceGraph:
    """Encodes a local embedding of an ideal graph in a punctured surface S
    via local order of edges around each puncture.
    Methods expect that the graph's edges connect punctures in S
    and that the complement is a disk."""
    
    
    def __init__( self, wordDict, adjDict = None ):
        """Assumes wordDict is dict of integers that can be cast to Words.
        Each Word specifies a cyclic order
        of edge labels encountered around the vertex (key) 
        In case wordDict data comes from a spanning tree of a dual graph to a loop in the plane,
        Raises an assertion error if the there are any isolated vertices.
        If wordDict is a list, will create a dictionary with keys corresponding to list
        indices."""

        # if wordDict is a list, cast to dictionary
        if type( wordDict ) == list:
            wordDict = listToDict( wordDict )
            
        # Create dictionary whose keys are positive indices corresponding to edge labels
        # and values are vertex labels [left, right] encountered when crossing this
        # edge in the positive direction (for orientable surfaces, left is index 0 and right is index 1)
        # For nonorientable surface, this choice is not well-defined, but adjDict still contains the
        # adjacency information

        if adjDict is None:
            self.adjDict = {}
        else:
            self.adjDict = adjDict        
        
        self.wordDict = {}        

        for key in wordDict:
            w = Word( wordDict[ key ] )
            w.cycReduce() # Cyclically reducing all words
            assert( len( w ) > 0 ) # Ruling out isolated vertices
            if adjDict is None:
                for letter in w.seq:
                    try:
                        self.adjDict[ abs( letter ) ] # check if key error
                    except KeyError:
                        self.adjDict[ abs( letter ) ] = [ None, None ]
                    finally:

                        # if this is a new label, put this vertex on left or right according to sign
                        if self.adjDict[ abs( letter ) ] == [ None, None ]:                        
                            self.adjDict[ abs( letter ) ][ not (sign( 0, letter)+1)//2  ] = key

                            # otherwise put it in the left over slot
                        elif self.adjDict[ abs( letter ) ][0] is None:
                            self.adjDict[ abs( letter ) ][0] = key
                        elif self.adjDict[ abs( letter ) ][1] is None:
                            self.adjDict[ abs( letter ) ][1] = key

                            # unless you've seen it twice already
                        else:
                            raise( "An edge label occured more than twice" )
                    
            self.wordDict[key]= w

        # Make sure the adjDict has no remaining None labels:
        for key in self.adjDict:
            assert( self.adjDict[key][0] is not None and self.adjDict[key][1] is not None ) # otherwise you've got hanging edges

        # These attributes are used to store a global cyclic order on generators and their inverses
        # How this is calculated depends on the topology of the graph
        self.order = None
        self.orderDict = None

    def spanningTree( self, baseRegion = None ):
        """Returns a new SurfaceGraph formed from a spanning tree of self.
        Computes tree via dfs from baseRegion"""
       
        if baseRegion is None:
            baseRegion = getKey( self.wordDict )

        #print( baseRegion )

        edgesToKeep = {}

        for edge, vert in self.dfs( curVert = baseRegion, spanningTree = True ):
            edgesToKeep[edge]=None

        adjDict = {}
        for key in self.adjDict:
            try:
                edgesToKeep[key]
                adjDict[key]=self.adjDict[key]
            except KeyError:
                pass

        wordDict = {}
        for key in self.wordDict:
            newWord = []
            for letter in self.wordDict[key].seq:
                try:
                    edgesToKeep[abs(letter)]
                    newWord.append( letter )
                except KeyError:
                    pass
            wordDict[key] = newWord

        return SurfaceGraph( wordDict, adjDict = adjDict )

    def genProd( self ):
        """Returns the word which is the product of all generators
        in the order they are stored in self.adjDict"""
        return Word( list( self.adjDict.keys() ) )       

    def createCyclicGenOrder( self ):
        """This function computes a consistent cyclic order on the set
        of generators and their inverses, if possible.
        Right now it only works as expected in case the graph is a tree
        with a planar embedding whose cyclic orientations at each vertex are consistent with the data given
        (all clockwise or all anticlockwise; else we risk value error or other unexpected behavior at (*) )
        And in this case the cyclic order is found by 'walking around the tree and reading edge labels' """

        order = []
        startVert = getKey( self.wordDict )
        curVert = startVert
        curEdge = self.wordDict[ curVert ].seq[0]
        while True:
            order.append( curEdge )
            curVert = self.adjDict[ abs( curEdge )  ][ (sign( 0, curEdge )+1)//2 ]
            curWord = self.wordDict[ curVert ].seq
            curEdge = curWord[ ( curWord.index( -curEdge ) + 1 ) % len( curWord ) ] # (*)
            if curVert == startVert:
                break

        # Check that we hit every edge twice to know if we are in a tree
        # If graph is disconnected or contains cycles, this is false
        assert( len( order ) == len( self.adjDict )*2 ) # Otherwise this isn't a tree

        #order.reverse() # walking around the tree clockwise vs anticlockwise shouldn't change si
        self.order = order
                
        # to optimize cross function, we create a dictionary that allows us to get the index
        # of an edge or its inverse in O(1) (the information we need to pass to the cross function)
        orderDict = {}
        for i in range( len( self.order ) ):
            orderDict[order[i]]=i
            
        self.orderDict = orderDict

    def reducedWordRep( self, w, filledPunctures, source = 0 ):
        """Given a word w representing a loop in the punctured surface S carrying self
        (so that w is a "cutting sequence" of edges), this method computes a canonical
        reduced representative of w relative to a vertex source in the surface
        with all punctures in the set filledPunctures filled in. The vertex source must not be an element
        of filledPunctures and is taken to be a random such vertex by default.
        Each filled-in puncture gives rise to a simple rewriting rule which eliminates
        one generator (the one corresponding to the edge which is 'upstream' from the vertex
        relative to the source), and the reduced representative is unique up to this choice."""

        assert( type( w ) == Word )
        assert( type( source ) == int )
        #assert( source >= 0 )
        #assert( source < len( self.wordList ) )
        assert( type( filledPunctures ) == set )
        #fillDict = {}
        for puncture in filledPunctures:
            assert( type( puncture ) == int )
            #assert( puncture >= 0 )
            #assert( puncture < len( self.wordList ) )
            #assert( w.seq != puncture )
            #fillDict[ puncture ] = None

        # make sure the source is a key in wordDict
        # but is not in filledPunctures
        choices = set( self.wordDict.keys() ).difference( filledPunctures )
        assert( choices != set() )
        if source not in choices:
            source = getKey( choices )

        #print( "Searching from:", source )
        
        #try:
        #    self.wordDict[source]
        #    print( "0 is a vertex" )
        #except KeyError:
        #    choices = set( self.wordDict.keys() ).difference( filledPunctures )
        #    assert( choices != set() )
        #    source = getKey( choices )
        #print( "hi" )
            

        copyword = w.copy()
        
        for edge, vert in self.dfs( curVert = source ):
            
            if vert in filledPunctures:
                #filledPunctures[ vert ] # skip if KeyError; puncture unfilled
                currWord = self.wordDict[ vert ]           
            
                currInv = ~currWord
                try:
                    ind = currWord.seq.index( edge )
                    word = currWord
                except ValueError:
                    ind = currInv.seq.index( edge )
                    word = currInv

                replWord = ~word.wslice( 0,ind ) / word.wslice( ind+1, len(word) )

                copyword = copyword.simpleRewrite( edge, replWord )
               
            #except KeyError:
            #    pass

        copyword.freeReduce()
        return copyword, source
    
    def dfs( self, curVert=0, spanningTree = True ):
        """Recursively generates a list of (edge, downsteam vertex) pairs via depth first search from a source vertex,
        where downstream vertex is the endpoint farther from the source,
        visited is a dictionary whose keys are edges that have already been visited, and values
        are terminal vertices to search from. curVert is the current vertex to search from.
        All edges in the resulting list are positive
        Unless spanningTree is set to to False, only returns pairs with edges
        from a spanningTree"""
    
        pairList = []

        try:
            self.wordDict[curVert]
        except KeyError:
            curvert = getKey( self.wordDict )

        def dfsHelper( data, curVert, visitedV, visitedE, spanningTree ):                
            for edge in data.wordDict[ curVert ].seq:
                try:
                    e = abs( edge )
                    visitedE[ e ]
                    # If you made it here, you have seen this edge already
                    # so do nothing
                    continue
                except KeyError:
                    # get the other vertex of e:         
                    otherVert = data.adjDict[ e ][ not data.adjDict[ e ].index( curVert ) ]
                    # if in spanningTree mode, only add the pair
                    # and make a recursive call if the other vertex isn't seen
                    if spanningTree:
                        try:
                            visitedV[ otherVert ]
                            # if you made it here, add this edge
                            # to prevent infinite loop and go next
                            # no recursive call
                            visitedE[ e ] =  None
                            continue                            
                        except KeyError:
                            visitedV[ otherVert ] = None
                            pairList.append(( e, otherVert))
                    else: # otherwise, add the pair unconditionally
                        visitedE[ e ] =  None
                        visitedV[ otherVert ] = None
                        pairList.append(( e, otherVert))
                    # make a recursive call if appropriate
                    dfsHelper( data, otherVert, visitedV, visitedE, spanningTree )
        dfsHelper( self, curVert, {curVert:None}, {}, spanningTree )

        return pairList

    def __str__( self ):
        
        toRet = "Local words around each vertex: \n"
        for key in self.wordDict:
            toRet += str( binSet(key) ) + " ("+str(key)+"): "\
                     + str( self.wordDict[ key ] ) + "\n"
        

        toRet += "\nEdge to [left,right] vertices: {"
        for key in self.adjDict:
            toRet += str( ALPHABET[ key - 1] )+ ": [" \
                + str( binSet( self.adjDict[ key ][0] ) )+", " \
                + str( binSet( self.adjDict[ key ][1] ) )+"], "
        toRet = toRet[:-2]+"}\n\nGlobal cyclic edge order: "
        if self.order is not None:
            toRet += str(Word( self.order ) )
            return toRet
        return toRet + "None computed"             

class Word:
    def __init__( self, seq ):
        """seq is a list nonzero integers.
        The absolute value is the index of the generator and the sign indicates
        \pm 1 in the exponent"""
        # I feel like it might be better to use a linked list when we make the app
        # Depends on whether list slicing/gluing/shifting is O(1)
        assert( type( seq ) == list )
        for elt in seq:
            assert( type( elt ) == int )
            assert( elt != 0 )
        self.seq = seq

    def freeReduce( self ):
        """Find first reduction, remove it, and restart
        from the beginning of the word until reduced.
        Could be made more efficient by propogating
        outward before restarting. Complexity = O(n)
        Modifies self."""
        # I would like to rewrite this to use shifts and cycReduce
        reduced = False
        while not reduced:
            madeReduction = False
            for i in range( len( self.seq ) - 1 ):
                cur = self.seq[i]
                nxt = self.seq[i+1]
                if cur+nxt != 0:
                    #no reduction
                    continue
                else:
                    #reduce by slice and glue
                    self.seq = self.seq[:i]+self.seq[i+2:]
                    madeReduction = True
                    break
            if not madeReduction:
                reduced = True

    def cycReduce( self ):
        """Performs cyclic reduction by chopping off ends until cyclically reduced.
        Modifies self."""
        self.freeReduce()
        if len( self.seq ) == 0:
            return
        while True:
            if self.seq[0]+self.seq[-1] != 0:
                #no reduction
                break
            else:
                #chop off ends
                self.seq = self.seq[1:-1]

    def __mul__( self, other ):
        """Returns the product of two words as a new word. Call with self*other"""
        return Word( self.seq+other.seq )

    def __truediv__( self, other ):
        """Multiply self by other's inverse. Call with self/other"""
        return self*~other

    def __invert__( self ):
        """Returns the inverse word (call with ~word)"""
        revseq = []
        for i in range( len( self.seq ) - 1, -1, -1 ):
            revseq.append( -self.seq[i] )
        return Word( revseq ) 

    def __pow__( self, n):
        assert( type( n ) == int )
        seq = []
        for i in range( abs( n ) ):
            if n > 0:
                seq += self.seq
            else:
                seq += ~self.seq
        return Word( seq )            

    def wslice( self, i, j, wrap = False ):
        """Returns a new word which is the subword which is the slice of self
        from i (inclusive) to j (exclusive).
        If wrap is False it behaves like list slice (empty if i>=j)
        If wrap is True and i >= j we slice cyclically
        In fact we obtain the ith shift with i=j"""
        assert( i >= 0 )
        assert( j >= 0 )
        assert( i <= len( self ) )
        assert( j <= len( self ) )
        if not wrap or i<j:
            return Word( self.seq[i:j] )
        else:
            return Word( self.seq[i:]+self.seq[:j] )

    def shift( self, i ):
        """Returns the cyclically shifted word conjugate to self whose first letter is
        the one at index i in w. Returns a new word and does not modify w"""
        return self.wslice( i, i, wrap = True )
    
    def naivePrimitiveRoot( self ):
        """Returns the pair (w, n) such that self = w^n AS FREE WORDS and n is maximal.
        In particular will not find the root of gw^ng^(-1) for nontrivial g"""
        for i in range( 1, len( self )//2+1 ):
            if len( self )%i == 0:
                seg = self.wslice(0,i)
                power = len( self )//i
                if pow( seg, power )==self:
                    return seg, power
        return self.copy(), 1
    
    def si( self, order, bypassCycReduce = False, verbose = False ):
        """Counts self intersections of self with respect to a global cylic order
        EXPECTS INPUT TO BE CYCLICALLY REDUCED
        set bypassCycReduce to True to skip this check"""
        rootself, powself = self.naivePrimitiveRoot()
        I = rootself.I( rootself, order, bypassCycReduce = bypassCycReduce, assumePrimitive = False, verbose = verbose )
        return powself**2*I//2+powself-1
    
    def I( self, other, order, bypassCycReduce = False, assumePrimitive = False, verbose = False ):
        """ Computes the geometric self intersection between self and other relative to
        a global cyclic order on generators and their inverses occuring in the word
        EXPECTS WORDS TO BE CYCLICALLY REDUCED
        set bypassCycReduce to True to skip this check"""        
        # could stand to add more preconditions
        assert( type( order) == dict )
        
        if not bypassCycReduce:
            self.cycReduce()
            other.cycReduce()
        else:
            warnings.warn( "WARNING: input may not be cyclically reduced")

        # compute primitive roots by default
        if not assumePrimitive:            
            rootself, powself = self.naivePrimitiveRoot()
            rootother, powother = other.naivePrimitiveRoot()
        else:
            rootself, powself = self, 1
            rootother, powother = other, 1

        if verbose:
            print( "Computing cross/val for each shift of", self, "along", other )
            print( "(powself=", powself, ", powother=", powother, ")" )
            print()
        
        # count intersections of primitive roots
        # can make this faster by skipping ahead if fellow travel is encountered
        #crossValDict = {}
        primCrossCount = 0
        shiftCount = 0
        i = 0
        while i < len( rootself ):
            j=0
            while j < len( rootother ):
                cross, valplus, valminus = rootself.crossval( rootother, order, i=i, j=j, verbose = verbose)
                val = abs( valplus ) + abs( valminus )
                #crossValDict[((i-abs(valminus))%len(rootself),(j-abs(valminus))%len(rootother),\
                #              (i+abs(valplus))%len(rootself),(j+abs(valplus))%len(rootother))] = abs( cross )
                if verbose:
                    print( " cross:", cross, "val:", val )
                    print()
                shiftCount += 1
                primCrossCount += abs( cross )/(1 + val)
                j+= 1#abs( val ) + 1
            i+=1

        #trying to experiment with skipping ahead, it's not working so far:
        #count = 0
        #for key in crossValDict:
        #    count += crossValDict[key]

        #return count*powself*powother

        #an earlier attempt:

        #for key in crossValDict.copy():
        #    if key in crossValDict:
        #        for i in range( key[0]+1, crossValDict[key][2]+1 ):
        #            try:
        #                del crossValDict[((key[0]-i)%len(rootself),(key[1]-i)%len(rootother))]
        #            except KeyError:
        #                continue
        #        for i in range( key[0]+1, crossValDict[key][1]+1 ):
        #            try:
        #                del crossValDict[((key[0]+i)%len(rootself),(key[1]+i)%len(rootother))]
        #            except KeyError:
        #                continue
        #        if crossValDict[key][0] == 0:
        #            del crossValDict[key]

        #return len( crossValDict.keys() )*powself*powother

        #indexSet = {}
        #for i in range( len( rootself ) ):
        #    for j in range( len( rootother ) ):
        #        try:
                    
        #        indexSet[ (i,j) ] = None
        
        if verbose:
            print( "Number of shifts for this computation:", shiftCount )
            print( "primCrossCount=", primCrossCount )
            print()
                
        return round( primCrossCount )*powself*powother
    
    def crossval( self, other, order, i=0, j=0, verbose = False ):
        """ Words must be cyclically reduced and positive length
        WORDS MUST BE CYCLICALLY REDUCED
        returns (cross, valplus, valminus) triple where cross is -1,0 or 1 (right hand rule from self+ to other+)
        and valplus, valminus are signed lengths of fellow traveling in forward/backward directions
        for convenience, (valplus,valminus) is set to (0,0) if periodisations are identical up to inverses """
        
        assert( len( self ) > 0 and len( other ) > 0 )
        
        # could make this marginally faster by not slicing unless i, j != 0?
        w1plus = self.shift( i )
        w1minus = ~w1plus

        w2plus = other.shift( j )
        w2minus = ~w2plus
        
        # define letters that are relevant to consider, p for positive and n for negative
        p1 = w1plus.seq[0]
        p2 = w2plus.seq[0]
        n1 = w1minus.seq[0]
        n2 = w2minus.seq[0]

        if verbose:
            print( "w1plus:", w1plus, "w1minus:", w1minus )
            print( "w2plus:", w2plus, "w2minus:", w2minus )        

        assert( p1 != n1 and p2 != n2 ) # this would contradict cyclic reduction
        
        initcross1 = cord( order[n1], order[n2], order[p1] )
        initcross2 = cord( order[n1], order[p2], order[p1] )
        initcross = initcross2 - initcross1
        
        if abs( initcross ) == 2: #cross is \pm 1; no fellow traveling
            return sign( 0, initcross ), 0, 0
        
        # otherwise check for fellow traveling
        if p1 == p2 or n1 == n2: # val>0
            plusdata = w1plus.initinfo( w2plus )
            minusdata = w1minus.initinfo( w2minus )
            initcross1 = cord( order[plusdata[1]], order[plusdata[2]], order[plusdata[3]] )
            if initcross1 == 0: #equal periodisations at these indices
                return 0, 0, 0
            #print( "Nontrivial fellow travel" )
            initcross2 = cord( order[minusdata[1]], order[minusdata[2]], order[minusdata[3]] )
            assert( initcross2 != 0 )
            return int( initcross1 == initcross2 ), plusdata[0], minusdata[0]
        if p1==n2 or p2==n1:
        #else: # p1==n2 or p2==n1 #val <0
            plusdata = w1plus.initinfo( w2minus )
            minusdata = w1minus.initinfo( w2plus )
            initcross1 = cord( order[plusdata[1]], order[plusdata[2]], order[plusdata[3]] )
            if initcross1 == 0: #inverse periodisations at these indices
                return 0, 0, 0
            #print( "Nontrivial fellow travel" )
            initcross2 = cord( order[minusdata[1]], order[minusdata[2]], order[minusdata[3]] )
            assert( initcross2 != 0 )
            return -int( initcross1 == initcross2 ), -plusdata[0], -minusdata[0]

        # if here, there is no fellow traveling, and they don't cross
        return 0, 0, 0
        

        #print( "hi" )
        #print( p1, p2, n1, n2 )
        #print( order[p1], order[p2], order[n1], order[n2] )
        #print( initcross2, initcross1 )
        #assert( False )

        
            
    def initinfo( self, other ):
        """given two words, returns data about common initial segments of their periodisations
        as a quadruple (dist, letter1, letter2, letterprev)"""
        
        assert( len( self ) > 0 and len( other ) > 0 ) 
        
        threshold = len( self )+len( other )
        letter1 = self.seq[0]
        letter2 = other.seq[0]
        letterprev = -self.seq[-1] #ensures you return the right thing from crossval
        # if there is no fellow traveling in this direction, but there is in the opposite direction
        length = 0
        
        while letter1 == letter2:
            letterprev = -letter1
            letter1 = self.seq[ (length+1)%len( self ) ]
            letter2 = other.seq[ (length+1)%len( other ) ]
            length += 1
            if length > threshold: # These words share a root, 
                break # letter1 and letter2 will be equal so cross will be 0
        
        return length, letterprev, letter1, letter2

    def simpleRewrite( self, gen, repl ):
        """Iterates over self once, replacing each instance of gen with the Word repl
        and each instance of -gen with the inverse of repl.
        gen may be positive or negative
        Returns the new representative; does not modify self"""
        assert( type( repl ) == Word )
        assert( type( gen ) == int )
        assert( abs( gen ) > 0 )

        invRepl = ~repl

        wseq = []
        for letter in self.seq:
            if abs( letter )!= abs( gen ):
                wseq.append( letter )
            elif letter == gen:
                wseq += repl.seq
            else:
                wseq += invRepl.seq
        return Word( wseq )

    def copy( self ):
        """Returns a copy of self"""
        return Word( self.seq )

    def __eq__( self, other ):
        return self.seq == other.seq

    def __len__( self ):
        return len( self.seq )

    #def isTrivial():
    #    self.cycReduce()
    #    return len( self ) == 0

    def __str__( self ): #passing alphabet as kwarg is pointless
        if self.seq == []:
            return "{}"
        s = ""
        for elt in self.seq:
            try:
                letter = ALPHABET[ abs(elt) - 1 ]
            except IndexError as e:
                traceback.print_exc()
                raise Exception( e ) # bad alphabet
            assert ( letter.lower() != letter.upper() ) # bad alphabet
            if elt > 0:
                s += letter.lower()
            else:
                s += letter.upper()
        return s



####################### TESTS ####################################


def test7():
    link = '9_24'
    link = 'K11a340'
    G = SurfaceGraphFromPD( plinkPD( link ) )
    print()
    #print( G )
    T = G.spanningTree()
    T.createCyclicGenOrder()
    print( T )
    print()

    loop = T.genProd()

    print( "gamma", loop )
    print( "si(gamma):", loop.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564] )
    
    print( "gamma_{2564}", loop1) 
    print( "si(gamma_{2564}):", loop1.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564,18754] )    
    print( "gamma_{2564,18754}", loop1) 
    print( "si(gamma_{2564,18754}):", loop1.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564,18754,70152] )    
    print( "gamma_{2564,18754,70152}", loop1) 
    print( "si(gamma_{2564,18754,70152}):", loop1.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564,18754,70152,132138] )    
    print( "gamma_{2564,18754,70152,132138}", loop1) 
    print( "si(gamma_{2564,18754,70152,132138}):", loop1.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564,18754,70152,132138,37120] )    
    print( "gamma_{2564,18754,70152,132138,37120}", loop1) 
    print( "si(gamma_{2564,18754,70152,132138,37120}):", loop1.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564,18754,70152,132138,37120,41088] )    
    print( "gamma_{2564,18754,70152,132138,37120,41088}", loop1) 
    print( "si(gamma_{2564,18754,70152,132138,37120,41088}):", loop1.si( T.orderDict ) )
    print()
    
    #snappy.Link( link ).exterior().plink()
    plink( link )
    print(  "PD code from the hacky function:", plinkPD( link ) )
    print()
    print( "PD code that snappy returns:", snappy.Link( link ).PD_code() )
    print()
    print( "PD code from rolfsen tables:", readPlanarDiagram( link ) )

def test6():
    #snappy sample usage
    #draw link from PD code (note that the PD code generated by snappy is different from this one)
    #M = snappy.Link( [[4, 2, 5, 1], [8, 3, 9, 4], [10, 6, 11, 5], [14, 7, 15, 8],
    #                  [2, 9, 3, 10], [16, 12, 17, 11], [20, 14, 21, 13], [6, 15, 7, 16],
    #                  [22, 18, 1, 17], [12, 20, 13, 19], [18, 22, 19, 21]] ).exterior().plink()
    #draw link from standard identifier string

    
    # get link from standard identifier string
    L = snappy.Link( '8_3' )

    # draw link ( can be annotated with PD code )    
    M = L.exterior()
    M.plink()
    
    #store and print PD_code
    pd = L.PD_code()
    print( pd )

    # can convert from manifold to link as follows:
    L1 = M.exterior_to_link()
    



def test5():
    

    diagram = readPlanarDiagram( "0_1" )
    print( diagram )
    diagram = readPlanarDiagram( "3_1" )
    print( diagram )
    diagram = readPlanarDiagram( "K11a1")
    PlaneTreeFromPlanarDiagram( diagram )
    return
    print( diagram )
    diagram = readPlanarDiagram( "8_3")
    print( diagram )
    PlaneTreeFromPlanarDiagram( diagram )
    return
    diagram = readPlanarDiagram( "K11a368" )
    print( diagram )


def test4():
    
    trefoil = SurfaceGraph( [[-1],[-3,1],[4,3,2],[-2],[-4]] )
    trefoil.createCyclicGenOrder()
    print( trefoil )
    w=Word( [1,2,3,4] ) #represents the trefoil loop
    w2 = Word( list( range( 1, 25 ))*3 )
    print( w2.naivePrimitiveRoot()[0], w2.naivePrimitiveRoot()[1] )
    #return
    w1 = trefoil.reducedWordRep( w, [] )
    print( pow(w1,4).I(pow( w1, 4 ),trefoil.orderDict ) )
    print( pow(w1,4).si( trefoil.orderDict ) )
    return
    w = Word( [1,4])
    v = Word( [3,1])
    
    print( w.crossval(v,trefoil.orderDict) )
                           

def test3():
    #G = SurfaceGraph( [[-1], [-3, 1], [3, 2, 4], [-2],[-4]] )
    #print( "\nEdge to [left,right] vertices:", G.adjDict, "}\nGlobal cyclic edge order: ", G.order )
    #G.createCyclicGenOrder()
    #print( "\n\nMore human readable: \n" )
    #print( G )

    G = SurfaceGraph( [[2],[6,5,4,3],[-9,-5],[1,-3,-2],[-6,-8,-7],[-10],[12,11],[10,-11,9],[-12],[7],[8],[-1],[-4]] )
    G.createCyclicGenOrder()
    print()
    print( G )

    print( "DFS from v0: " )
    for edge, vert in G.dfs():
        print( "edge: ", ALPHABET[ edge-1 ],"     downstream vert: ", vert )

    def testReducedWordRep( graph, word, fill ):
        print( "\nOriginal word: ", word )
        print( "Punctures filled: ", fill )
        print( "Reduced word after filling: ", graph.reducedWordRep( word, fill ) )
        print()

    testReducedWordRep( G, Word( [3,6,5,4,-3] ), [1] ) 
    testReducedWordRep( G, Word( [3,6,5,4] ), [1] ) 
    testReducedWordRep( G, Word( [3,6,5,4] ), [11] ) 
    testReducedWordRep( G, Word( [3,6,5,4] ), [2] ) 
    testReducedWordRep( G, Word( [3,6,5,4] ), [2, 7] ) 
    testReducedWordRep( G, Word( [3,6,5,4] ), [2,7,5,6,8,4,12,3] ) 
    
    
        
    #print( G.reducedWordRep(  ) ) #OK
    #print( G.reducedWordRep( Word( [3,6,5,4] ), [11] ) )#OK
    #print( G.reducedWordRep( Word( [3,6,5,4] ), [2] ) )#OK
    
    #print( G.reducedWordRep( Word( [3,6,5,4] ),  ) ) #OK

    #print( "hi " )
    #for edge in G.dfs( curVert = 11 ):
    #    print( "hi" )
    #    print( edge )

def test2():
    print( cord(1,2,3) )
    print( cord(2,0,0.5) )
    print( cord(2,0,3) )
    print( cord( "a", "b", "c" ) )
    print( cord( "b", "a", "c" ) ) 

def test1():    
 
    e = Word( [] )
    e.freeReduce()
    e.cycReduce()
    #print( e )    
    w = randomWord( 20, 2, s="hit7t4yyy" )
    print()
    print( "w=\t\t",w.seq )
    w.freeReduce()
    print( "reduced, w=\t", w.seq)
    w.cycReduce()
    print( "cyc reduced, w=\t", w.seq )
    print()
    for i in range( len( w )+1 ):
        print() 
        print( w.wslice( 3, 0 ) )
        print( w.shift( i ) )

    w = randomWord( 10, 5, s="hit7t4yyy" )
    print( "w= ", w )
    print( "w( a-->BCdc )",w.simpleRewrite( 1, Word( [-2, -3, 4, 3 ] ) ) )
    print( "w( A-->BCdc )",w.simpleRewrite( -1, Word( [-2, -3, 4, 3 ] ) ) )

####################### RUN MAIN ####################################

if __name__ == "__main__":
    main()
