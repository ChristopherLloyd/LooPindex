import lightrdf
import gzip


def main():
    
    RDF_FILENAME = 'knotdata/Knots11.rdf.gz'

    f = gzip.open(RDF_FILENAME, 'rb')
    #doc = lightrdf.RDFDocument(f, parser=lightrdf.xml.PatternParser)
    #for (s, p, o) in doc.search_triples(None, None, None):
                #print(s, p, o)
    #test1()
    print( cord(1,2,3) )
    print( cord(2,0,0.5) )
    print( cord(2,0,3) )
    print( cord( "a", "b", "c" ) )
    print( cord( "b", "a", "c" ) )

def test1():
    
 
    e = Word( [] )
    e.freeReduce()
    e.cycReduce()
    print( e )

    w = Word( [[7,0],[2,3],[0,5],[1,-2],[1,0],[1,0],[0,3],[0,6],[0,-2],[2,-3]] )
    print( w )
    w.freeReduce()
    print( w)
    w.cycReduce()
    print( w )

def sign(i,j):
    return int(i!=j)*(int(i<j)*2-1)

def cord(i,j,k):
    """returns 1 or -1 according to the cyclic order of i,j, and k in (-inf,inf)
    e.g. cord(-1,2,3)=cord(3,1,2)=1 while cord(2,1,3)=-1
    works for any data types with '=' and '>' operators"""
    if i == j or j == k or i == k:
        return 0
    return (int(j>i)*2-1)*(int(k>j)*2-1)*(int(k>i)*2-1)

    #n is the length of the list

    #if n is None:
    #    n=abs(max(i,j,k))
    #i,j,k=i%n,j%n,k%n
    
    #if i < j:
    #    if ( (j<k) or (k<i) ):
    #        return 1
    #    if ( (k=j) or (k=1) ):
    #        return 0
    #    return -1
    #if j < i:
    #    return int( (
    #print( i, j, k )

    
    
#def Cyclist:
#    def __init__( self ):
#        pass

class PlanarGraph:
    """Encodes a topological embedding of a graph in the plane,  """
    def __init__( self ):
        pass

class Word:
    def __init__( self, tupList ):
        """tupList is a list of size 2 lists of integers.
    The first entry is nonnegative and gives the generator index,
    and the second is its exponent"""
    # I feel like it might be better to use a linked list when we make the app
        assert( type( tupList ) == list )
        for elt in tupList:
            assert( type( elt ) == list and len( elt ) == 2 )
            assert( type( elt[0] ) == int )
            assert( type( elt[1] ) == int )
            assert( elt[0] >= 0 )
        self.tupList = tupList

    def freeReduce( self ):
        """Find first reduction, remove it, and restart
        from the beginning of the word until reduced.
        Could be made more efficient by propogating
        outward before restarting."""
        reduced = False
        while not reduced:
            madeReduction = False
            for i in range( len( self.tupList ) - 1 ):
                cur = self.tupList[i]
                nxt = self.tupList[i+1]
                if cur[1]==0:
                    #exponent 0, remove
                    self.tupList = self.tupList[:i]+self.tupList[i+1:]
                    madeReduction = True
                    break
                if cur[0] != nxt[0]:
                    #indices differ, move on
                    continue
                else:
                    #add exponents
                    cur[1] += nxt[1]
                    if cur[1] == 0:
                        #remove both if 0
                        self.tupList = self.tupList[:i]+self.tupList[i+2:]
                    else:
                        #otherwise delete the second element
                        self.tupList = self.tupList[:i+1]+self.tupList[i+2:]
                    madeReduction = True
                    break
            if not madeReduction:
                reduced = True

    def cycReduce( self ):
        """Performs cyclic reduction by adding exponent if first and last generators agree,
        and recording sum in first generator slot and deleting last generator.
        Note the cyclic reduction is only unique up to cyclic permutation"""
        self.freeReduce()
        if len( self.tupList ) == 0:
            return
        while True:
            if self.tupList[0][0] != self.tupList[-1][0]:
                break
            else:
                self.tupList[0][1] += self.tupList[-1][1]
                if self.tupList[0][1] != 0:
                    self.tupList = self.tupList[:-1]
                    break
                self.tupList = self.tupList[1:-1]


    def algInt( self, other ):
        """Computes the algebraic intersection between two Words using modification of Birman-Series Cohen-Lustig ideas"""
        pass       
       

    def __str__( self ):
        if self.tupList == []:
            return "{}"
        return str( self.tupList  )
            
    

#class FreeGroup:
#    def __init__( self, gens ):
#        """gens is a string of distinct, lowercase generators"""
#        validGens = "abcdefghijklmnopqrstuvwxyz"
#        self.gens = []
#        assert( gens != "" )
#        for char in gens:
#            assert( char in validGens )
#        self.gens = gens

if __name__ == "__main__":
    main()
