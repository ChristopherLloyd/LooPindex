import lightrdf
import gzip
from random import *
import traceback
#import itertools

ALPHABET = "abcdefghijklmnopqrstuvwxyz" # generator alphabet, used for readable output only. Inverses are upper case

def main():
    
    RDF_FILENAME = 'knotdata/Knots11.rdf.gz'

    f = gzip.open(RDF_FILENAME, 'rb')
    #doc = lightrdf.RDFDocument(f, parser=lightrdf.xml.PatternParser)
    #for (s, p, o) in doc.search_triples(None, None, None):
                #print(s, p, o)
    test3()

####################### TESTS ####################################

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
        print( w.slice( 3, 0 ) )
        print( w.shift( i ) )

    w = randomWord( 10, 5, s="hit7t4yyy" )
    print( "w= ", w )
    print( "w( a-->BCdc )",w.simpleRewrite( 1, Word( [-2, -3, 4, 3 ] ) ) )
    print( "w( A-->BCdc )",w.simpleRewrite( -1, Word( [-2, -3, 4, 3 ] ) ) )

####################### GENERALLY USEFUL FUNCTIONS ####################################

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

####################### DATA STRUCTURES ####################################

class SurfaceGraph:
    """Encodes a local embedding of an ideal graph in a punctured surface S
    via local order of edges around each puncture.
    Methods expect that the graph's edges connect punctures in S
    and that the complement is a disk."""
    
    
    def __init__( self, wordList ):
        """Assumes wordList is list of integers that can be cast to Words.
        Each Word specifies a cyclic order
        of edge labels encountered around the vertex of that Word's index in the list.
        In case wordList data comes from a spanning tree of a dual graph to a loop in the plane,
        it is convenient to assume that the vertex 0 corresponds to the region at infinity.
        Raises an assertion error if the there are any isolated vertices."""


        # Create dictionary whose keys are positive indices corresponding to edge labels
        # and values are vertex labels [left, right] encountered when crossing this
        # edge in the positive direction (for orientable surfaces, left is index 0 and right is index 1)
        # For nonorientable surface, this choice is not well-defined, but adjDict still contains the
        # adjacency information

        self.adjDict = {}

        self.wordList = []

        for i in range( len( wordList ) ):
            w = Word( wordList[ i ] )
            w.cycReduce() # Cyclically reducing all words
            assert( len( w ) > 0 ) # Ruling out isolated vertices
            for letter in w.seq:
                try:
                    self.adjDict[ abs( letter ) ] # check if key error
                except KeyError:
                    self.adjDict[ abs( letter ) ] = [ None, None ]
                finally:

                    # if this is a new label, put this vertex on left or right according to sign
                    if self.adjDict[ abs( letter ) ] == [ None, None ]:                        
                        self.adjDict[ abs( letter ) ][ not (sign( 0, letter)+1)//2  ] = i

                        # otherwise put it in the left over slot
                    elif self.adjDict[ abs( letter ) ][0] is None:
                        self.adjDict[ abs( letter ) ][0] = i
                    elif self.adjDict[ abs( letter ) ][1] is None:
                        self.adjDict[ abs( letter ) ][1] = i

                        # unless you've seen it twice already
                    else:
                        raise( "An edge label occured more than twice" )
                    
            self.wordList.append( w )


        # Make sure the adjDict has no remaining None labels:
        for key in self.adjDict:
            assert( self.adjDict[key][0] is not None and self.adjDict[key][1] is not None ) # otherwise you've got hanging edges

        # This attribute is used to store a global cyclic order on generators and their inverses
        # How this is calculated depends on the topology of the graph
        self.order = None

    def createCyclicGenOrder( self ):
        """This function computes a consistent cyclic order on the set
        of generators and their inverses, if possible.
        Right now it only works as expected in case the graph is a tree
        with a planar embedding whose cyclic orientations at each vertex are consistent with the data given
        (all clockwise or all anticlockwise; else we risk value error or other unexpected behavior at (*) )
        And in this case the cyclic order is found by 'walking around the tree and reading edge labels' """

        order = []
        curVert = 0
        curEdge = self.wordList[ curVert ].seq[0]
        while True:
            order.append( curEdge )
            curVert = self.adjDict[ abs( curEdge )  ][ (sign( 0, curEdge )+1)//2 ]
            curWord = self.wordList[ curVert ].seq
            curEdge = curWord[ ( curWord.index( -curEdge ) + 1 ) % len( curWord ) ] # (*)
            if curVert == 0:
                break

        # Check that we hit every edge twice to know if we are in a tree
        # If graph is disconnected or contains cycles, this is false
        assert( len( order ) == len( self.adjDict )*2 ) # Otherwise this isn't a tree

        self.order = order


    def reducedWordRep( self, w, filledPunctures, source = 0 ):
        """Given a word w representing a loop in the punctured surface S carrying self
        (so that w is a "cutting sequence" of edges), this method computes a canonical
        reduced representative of w relative to a vertex source in the surface
        with all punctures in the list filledPunctures filled in. The vertex source must not be an element
        of filledPunctures and is taken to be the vertex at infinity by default.
        Each filled-in puncture gives rise to a simple rewriting rule which eliminates
        one generator (the one corresponding to the edge which is 'upstream' from the vertex
        relative to the source), and the reduced representative is unique up to this choice."""

        assert( type( w ) == Word )
        assert( type( source ) == int )
        assert( source >= 0 )
        assert( source < len( self.wordList ) )
        assert( type( filledPunctures ) == list )
        fillDict = {}
        for puncture in filledPunctures:
            assert( type( puncture ) == int )
            assert( puncture >= 0 )
            assert( puncture < len( self.wordList ) )
            assert( w != puncture )
            fillDict[ puncture ] = None

        copyword = w.copy()
        
        for edge, vert in self.dfs( curVert = source ):

            #print( "edge: ", edge,"     vert: ", vert )
            
            try:
                fillDict[ vert ] # skip if KeyError; puncture unfilled
                currWord = self.wordList[ vert ]           
            
                currInv = ~currWord
                try:
                    ind = currWord.seq.index( edge )
                    word = currWord
                except ValueError:
                    ind = currInv.seq.index( edge )
                    word = currInv

                replWord = ~word.slice( 0,ind ) / word.slice( ind+1, len(word) )

                copyword = copyword.simpleRewrite( edge, replWord )
               
            except KeyError:
                pass

        copyword.freeReduce()
        return copyword
    
    def dfs( self, curVert=0, visited={} ):
        """Recursively generates a list of (edge, downsteam vertex) pairs via depth first search from a source vertex,
        where downstream vertex is the endpoint farther from the source,
        visited is a dictionary whose keys are edges that have already been visited, and values
        are terminal vertices to search from. curVert is the current vertex to search from.
        All edges yielded are positive"""
    
        pairList = []

        def dfsHelper( data, curVert=0, visited={} ):                
            for edge in data.wordList[ curVert ].seq:
                try:
                    e = abs( edge )
                    visited[ e ]
                    # Base case. If you made it here with no error, time to backtrack.
                except KeyError:               
                    visited[ e ] =  data.adjDict[ e ][ not data.adjDict[ e ].index( curVert ) ] # get the other vertex of e 
                    pairList.append(( e, visited[ e ]))
                    dfsHelper( data, curVert=visited[ e ], visited=visited )
        dfsHelper( self, curVert=0, visited = {} )

        return pairList

    def __str__( self ):
        
        toRet = "Local words around each vertex: \n"
        for i in range( len( self.wordList ) ):
            toRet += str( i ) + ": " + str( self.wordList[ i ] ) + "\n"
        

        toRet += "\nEdge to [left,right] vertices: {"
        for key in self.adjDict:
            toRet += str( ALPHABET[ key - 1] )+ ": " + str( self.adjDict[ key ] )+", "
        toRet = toRet[:-2]+"}\nGlobal cyclic edge order: "
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

    def slice( self, i, j, wrap = False ):
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
        return self.slice( i, i, wrap = True )

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

####################### RUN MAIN ####################################

if __name__ == "__main__":
    main()
