from planeloop import *
from buildWebCatalog import *
#import mysql.connector
#import os
# https://dev.mysql.com/doc/mysql-getting-started/en/#mysql-getting-started-basic-ops

#db = mysql.connector.connect( username=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PASS') )
#cursor = db.cursor()

try:
    cursor.execute("USE multiloops")
except NameError as msg:
    traceback.print_exc()
    #raise Exception( msg ) # database not found

def main():
    name = '11^1_97'
    name = '10^1_18'
    oloop = getFieldByName( "pd", name )
    loop = eval( getFieldByName( "drawnpd", name ) )
    debug = False
    #loop = link9
    #oloop = tripleLem # has a monogon
    #loop = plinkPD( oloop )
    print( loop )
    
    G = SurfaceGraphFromPD( loop )
    #print( G )
    T = G.spanningTree()
    T.createCyclicGenOrder()
    #print( T.wordDict )
    print( T.adjDict )
    gammaListUnpruned = pdToComponents( loop )
    #print( gammaListUnpruned )
    gammalist = []
    for elt in gammaListUnpruned:
        gamma = []
        for gen in elt:
            if gen in G.adjDict:
                gamma.append( gen )
        gammalist.append( Word( gamma ) )
        #print( gammalist[-1] )
    gamma = gammalist[0]
    #print( gamma )


    s = Spherimultiloop( pd=loop )
    #print( s.sigma )

    def subWord( strtLabel, stpLabels ):
        word = []
        curLabel = strtLabel
        #we have to do silly sign adjustments due to past transgressions
        sgn = sign(0, strtLabel )
        while curLabel not in stpLabels or curLabel==strtLabel:
            word.append( -curLabel )
            curLabel = ( curLabel -  1 ) % (2*len( loop ))
            if sgn < 0:
                curLabel -= 2*len(loop)             
            if curLabel == 0:
                curLabel = 2*len( loop )           
        return word, curLabel
    

    def findBigon( x, y, startIndex1, startIndex2 ):
        stopLabelsY = y#[abs(y[0]),abs(y[1]),abs(y[2]),abs(y[3])]
        stopLabelsX = x#[abs(x[0]),abs(x[1]),abs(x[2]),abs(x[3])]

        #print( "Start:", x)
        #print( "Stop:", y)
        
        skip = False
        w1, stop1 = subWord( x[startIndex1], stopLabelsX+stopLabelsY )
        #print( "w1, stop1:", w1, stop1 )
        if stop1 in stopLabelsX:
            skip = True
        w2, stop2 = subWord( x[startIndex2], stopLabelsX+stopLabelsY )
        #print( "w2, stop2:", w2, stop2 )
        if stop2 in stopLabelsX:
            skip = True

        #print( "skip", skip)
        if skip:
            return
            
        #print( "stop1, stop2", stop1, stop2)
        #print( "stopLabelsY[0], stopLabelsY[2]]", stopLabelsY[0], stopLabelsY[2])
        #print( "stopLabelsY[1], stopLabelsY[3]])", stopLabelsY[1], stopLabelsY[3] )
        #input()
        if set( [stop1, stop2] ) != set( [stopLabelsY[0], stopLabelsY[2]]) and \
                set( [stop1, stop2] ) != set( [stopLabelsY[1], stopLabelsY[3]]):
            return w1, w2
        #print( "No corner at y")
            #bigonWords.append( Word(w1)/Word(w2) )
    
    monogonWords = []
    for vertcycle in s.sigma:
        stopLabels = [vertcycle[1],vertcycle[3]]
        for startLabel in [vertcycle[0], vertcycle[2]]:
            monogonWords.append( [Word( subWord( startLabel, stopLabels )[0] ), vertcycle] )

        #if debug:
        #    print( "Vertex ", vertcycle )
        #    print( "Monogon words", monogonWords[-1], monogonWords[-2])
        #    print()

    #print( "Monogon words")
    #for word in monogonWords:
    #    print( word )
    #print()

    bigonWords = []
    for i in range( len( s.sigma ) - 1 ):
        for j in range( i+1, len(s.sigma)):
            x = s.sigma[i]
            y = s.sigma[j]
 
            bigonCount = 0
            bigonsToAdd = []

            # test two opposing corners
            # in practice (because of pd code labeling conventions)
            # orientations of outgoing labels agree and
            # this is always the case of interlaced chords
            # so you will always find two or zero bigons            

            bigonSegs = findBigon( x, y, 0, 1)
            if bigonSegs is not None:
                bigonsToAdd.append( [Word(bigonSegs[0])/Word(bigonSegs[1]), x, y] )
                bigonCount += 1
                #print( x, y, Word(bigonSegs[0]), Word(bigonSegs[1]) )
                #print( "first")

            bigonSegs = findBigon( x, y, 2, 3)
            if bigonSegs is not None:
                bigonsToAdd.append( [Word(bigonSegs[0])/Word(bigonSegs[1]), x, y] )
                bigonCount += 1
                #print( x, y, Word(bigonSegs[0]), Word(bigonSegs[1]) )
                #print( "second")

            if bigonCount == 0:
                # if bigons are found already, then none will be found here,
                # so you could put the snippets below here for a speedup
                pass
            
            # test from the other two opposing corners if a bigon is not yet found
            # in practice (because of pd code labeling conventions)
            # orientations of outgoing labels are opposite signs and
            # this is always the case of non-interlaced chords
            # so you will always find one bigon
                        
            bigonSegs = findBigon( x, y, 1, 2)
            if bigonSegs is not None:
                bigonsToAdd.append( [Word(bigonSegs[0])/Word(bigonSegs[1]), x, y] )
                bigonCount += 1
                #print( x, y, Word(bigonSegs[0]), Word(bigonSegs[1]) )
                #print( "third")

            # you can also skip the check below if you found one above (with our PD convention)

            bigonSegs = findBigon( x, y, 3, 0)
            if bigonSegs is not None:
                bigonsToAdd.append( [Word(bigonSegs[0])/Word(bigonSegs[1]), x, y] )
                bigonCount += 1
                #print( x, y, Word(bigonSegs[0]), Word(bigonSegs[1]) )
                #print( "fourth")
            
            assert( bigonCount <= 2 )

            bigonWords += bigonsToAdd
            #if debug:
            #    print( "Start vertex ", x )
            #    print( "End vertex ", y )#

            #    print( "Bigon words", end = " "  )
            #    for k in range( bigonCount ):
            #        print(bigonsToAdd[k], end=" " )
            #    print()
            #    print()


    #return


    print( T  )
    for pruneWords in [monogonWords, bigonWords]:
        for i in range( len( pruneWords ) ):
            projWord = []
            for letter in pruneWords[i][0].seq:
                if abs( letter ) in T.adjDict:
                    projWord.append( letter )
            #print( monogonWords[i] )
            #print( projWord )
            pruneWords[i][0] = Word( projWord )

    
    for word in monogonWords+bigonWords:
        print( word[0], end= " " )

    print()

    regList = list( T.wordDict.copy().keys() )
    regList.sort()
    fullRegSet = set( regList )
    regLabels = {}
    for i in range( len( regList ) ):
        regLabels[regList[i]] = i+1
    #infRegion = regList[0]

    monobigClause = dict()

    for j in range( len( regList ) ):#: in regList:
        infRegion = regList[j]        
        for wordList in [monogonWords, bigonWords]:
            for word in wordList:
                #outer = {1}
                nonZeroWinding = set()
                for i in range( 0, len( regList ) ):
                    #if regList[i] == infRegion:
                    #    continue
                    fillWord = T.reducedWordRep( word[0], fullRegSet.difference( {infRegion,regList[i]} ), source = infRegion )[0]
                    #if word.seq == [-8, -7, -6, 11, 12, 14]:
                    #    print( "region", i+1, "fillWord", fillWord )
                    if fillWord.seq == []:
                        continue                        
                    else:
                        nonZeroWinding.add( i+1 )


                #if outer == {1,7} or inner == {1,7}:
                #    print( "outer:", outer)
                #    print( "inner:", inner)
                #    print( word )
                #    print( word.seq )
                #    input()

                supset = False
                subset = False
                toRemove = set()
                for disj in monobigClause:
                    if disj < nonZeroWinding:
                        supset = True
                    if nonZeroWinding < disj:
                        toRemove.add( disj )                    
                        subset = True      


                    #if disj < inner:
                    #    innerSupSet = True
                    #if inner < disj:
                    #    toRemove.add( disj )
                    #    innerSubSet = True

                
                if supset and subset:
                    print( "nonzeroWinding:", nonZeroWinding)
                    raise( Exception( "Monorbigon clause violates antichain property") )

                #if innerSupSet and innerSubSet:
                #    print( "inner:", inner)
                #    raise( Exception( "Monorbigon clause violates antichain property") )

                for clause in toRemove:
                    del monobigClause[clause]
                if not supset or subset:
                    monobigClause[frozenset( nonZeroWinding ) ]=word+[j+1]
                #if not innerSupSet or innerSubSet:
                #    monobigClause.add( frozenset( inner ) )

                #print( "monorbigon clause", monobigClause)

    #print(monobigClause)

    print( "Monorbigon clause:")
    for disjunction in monobigClause:
        print( " clause: {:<30} at vertex/vertices: {:<40} and infinite region {:<10}".format( str(list( disjunction )), str( monobigClause[ disjunction ][1:-1]  ), monobigClause[ disjunction ][-1] ) )

    return

    input( "Press and key to draw loop")
    drawLoopWithRegLabels( oloop, loop, G )


    
    #print( monogonWords )


    # project monogon and bigon words to the spanning tree

    return
    drawAnnotatedLoop( oloop, loop, G)

def drawAnnotatedLoop( pd, drawnpd, G ):
    regList = list( G.wordDict.copy().keys() )
    regList.sort()
    emptyLabels = {}
    for i in range( len( regList ) ):
        emptyLabels[regList[i]] = ""
    plinkImgFile( str( pd ), drawnpd, G.adjDict, G.wordDict,[],None,emptyLabels,\
                 pdToComponents( drawnpd ), forWeb = False, filename = str( drawnpd )+"annotated", sigmaAnnotated = True, simpleSave = True )
    
def drawLoopWithRegLabels( pd, drawnpd, G ):
    regList = list( G.wordDict.copy().keys() )
    regList.sort()
    numLabels = {}
    for i in range( len( regList ) ):
        numLabels[regList[i]] = i+1
    plinkImgFile( str( pd ), drawnpd, G.adjDict, G.wordDict,[],None,numLabels,\
                 pdToComponents( drawnpd ), forWeb = False, filename = str( drawnpd )+"numLabels", sigmaAnnotated = False, simpleSave = True )

if __name__ == "__main__":
    main()
