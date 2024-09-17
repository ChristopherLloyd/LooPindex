from planeloop import *

def main():
    oloop = link9
    #oloop = tripleLem # has a monogon
    loop = plinkPD( oloop )
    print( loop )
    
    G = SurfaceGraphFromPD( loop )
    #print( G )
    T = G.spanningTree()
    T.createCyclicGenOrder()
    print( T )
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
    print( gamma )


    s = Spherimultiloop( pd=loop )
    print( s.sigma )

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
            monogonWords.append( Word( subWord( startLabel, stopLabels )[0] ) )

        print( "Vertex ", vertcycle )
        print( "Monogon words", monogonWords[-1], monogonWords[-2])
        print()

    #print( "Monogon words")
    #for word in monogonWords:
    #    print( word )
    #print()

    bigonWords = []
    for i in range( len( s.sigma ) - 1 ):
        for j in range( i+1, len(s.sigma)):
            x = s.sigma[i]
            y = s.sigma[j]
            #stopLabelsY = [abs(y[0]),abs(y[1]),abs(y[2]),abs(y[3])]
            #stopLabelsX = [abs(x[0]),abs(x[1]),abs(x[2]),abs(x[3])]

            #bigonFound = False
            bigonCount = 0
            bigonsToAdd = []

            

            #print()
            #print( "Start:", x)
            #print( "Stop:", y)

            # test two opposing corners
            # in practice (because of pd code labeling conventions)
            # orientations of outgoing labels agree and
            # this is always the case of interlaced chords
            # so you will always find two bigons            

            bigonSegs = findBigon( x, y, 0, 1)
            if bigonSegs is not None:
                bigonsToAdd.append( Word(bigonSegs[0])/Word(bigonSegs[1]) )
                bigonCount += 1
                #print( x, y, Word(bigonSegs[0]), Word(bigonSegs[1]) )
                #print( "first")

            bigonSegs = findBigon( x, y, 2, 3)
            if bigonSegs is not None:
                bigonsToAdd.append( Word(bigonSegs[0])/Word(bigonSegs[1]) )
                bigonCount += 1
                #print( x, y, Word(bigonSegs[0]), Word(bigonSegs[1]) )
                #print( "second")

            # test from the other two opposing corners if a bigon is not yet found
            # in practice (because of pd code labeling conventions)
            # orientations of outgoing labels are opposite signs and
            # this is always the case of non-interlaced chords
            # so you will only find one bigon
                        
            bigonSegs = findBigon( x, y, 1, 2)
            if bigonSegs is not None:
                bigonsToAdd.append( Word(bigonSegs[0])/Word(bigonSegs[1]) )
                bigonCount += 1
                #print( x, y, Word(bigonSegs[0]), Word(bigonSegs[1]) )
                #print( "third")

            bigonSegs = findBigon( x, y, 3, 0)
            if bigonSegs is not None:
                bigonsToAdd.append( Word(bigonSegs[0])/Word(bigonSegs[1]) )
                bigonCount += 1
                #print( x, y, Word(bigonSegs[0]), Word(bigonSegs[1]) )
                #print( "fourth")
            
            assert( bigonCount <= 2 )

            bigonWords += bigonsToAdd
            print( "Star vertex ", x )
            print( "End vertex ", x )

            print( "Bigon words", end = " "  )
            for i in range( bigonCount ):
                print(bigonsToAdd[i], end=" " )
            print()
            print()



            """
            skip = False
            w1, stop1 = subWord( x[0], stopLabelsX+stopLabelsY )
            if stop1 in stopLabelsX:
                skip = True
            w2, stop2 = subWord( x[1], stopLabelsX+stopLabelsY )
            if stop2 in stopLabelsX:
                skip = True
            if not ( set( [stop1, stop2] ) == set( [stopLabels[0], stopLabels[2]]) or set( [stop1, stop2] ) == set( [stopLabels[1], stopLabels[3]]) ) and not skip:
                bigonWords.append( Word(w1)/Word(w2) )
                bigonFound = True
                bigonCount += 1
                print( x, y, Word( w1 ), Word( w2 ) )
                print( "first")
                input()

            w1, stop1 = subWord( x[2], stopLabelsX+stopLabelsY )
            w2, stop2 = subWord( x[3], stopLabelsX+stopLabelsY  )
            if not ( set( [stop1, stop2] ) == set( [stopLabels[0], stopLabels[2]]) or set( [stop1, stop2] ) == set( [stopLabels[1], stopLabels[3]]) ):
                bigonWords.append( Word(w1)/Word(w2) )
                bigonFound = True
                bigonCount += 1
                print( x, y, Word( w1 ), Word( w2 ) )
                print( "second")
                input()

         

            w1, stop1 = subWord( x[1], stopLabelsX+stopLabelsY  )
            w2, stop2 = subWord( x[2], stopLabelsX+stopLabelsY  )
            print( stop1, stop2 )
            print( stopLabels )
            print( set( [stop1, stop2] ) )
            print( set( [stopLabels[0], stopLabels[2]] ) )
            print( set( [stopLabels[1], stopLabels[3]] ) )
            if not ( set( [stop1, stop2] ) == set( [stopLabels[0], stopLabels[2]]) or set( [stop1, stop2] ) == set( [stopLabels[1], stopLabels[3]]) ):
                bigonWords.append( Word(w1)/Word(w2) )
                bigonCount += 1
                print( x, y, Word( w1 ), Word( w2 ) )
                print( "Ye")
                print( "third")
                input()
                

            w1, stop1 = subWord( x[3], stopLabelsX+stopLabelsY  )
            w2, stop2 = subWord( x[0], stopLabelsX+stopLabelsY  )
            if not ( set( [stop1, stop2] ) == set( [stopLabels[0], stopLabels[2]]) or set( [stop1, stop2] ) == set( [stopLabels[1], stopLabels[3]]) ):
                bigonWords.append( Word(w1)/Word(w2) )
                bigonCount += 1
                print( x, y, Word( w1 ), Word( w2 ) )
                print( "fourth")
                input() """


    #print( "Bigon words")
    #for word in bigonWords:
    #    print( word )
    #print()


            
            

                


                       
    #print( monogonWords )




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

if __name__ == "__main__":
    main()
