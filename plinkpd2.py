import snappy #gives annoying deprecation warning every time
import sys

#print( "hi" )

def main():
    try:
        link = eval( sys.argv[1] )
        data = getLEwithPD( link )
        print( data[1] )
        data[0].done()
    except IndexError as e:
        print( e )

#link = eval( link )
#link = link = [[6, 12, 1, 7], [7, 5, 8, 6], [8, 11, 9, 12], [1, 4, 2, 5],\
#  [10, 16, 11, 13], [9, 16, 10, 15], [3, 14, 4, 15], [2, 14, 3, 13]]

#link = [[6, 12, 1, 7], [7, 5, 8, 6], [8, 11, 9, 12], [1, 4, 2, 5],\
#  [10, 16, 11, 13], [9, 16, 10, 15], [3, 14, 4, 15], [2, 14, 3, 13]]

#link = [[10, 16, 1, 11], [11, 9, 12, 10], [15, 1, 16, 2], [8, 12, 9, 13], [2, 17, 3, 22],\
#        [14, 26, 15, 23], [13, 26, 14, 25], [19, 7, 20, 8], [17, 20, 18, 21], [3, 21, 4, 22],\
#        [23, 4, 24, 5], [5, 24, 6, 25], [6, 18, 7, 19]]

#link = [ ( 3 , 8 , 4 , 1 ) , ( 6 , 1 , 7 , 2 ) , ( 7 , 4 , 8 , 5 ) , ( 2 , 5 , 3 , 6 ) ]

#link = [[1,7,6,12],[1,8,2,7],[6,11,5,12],[8,3,9,2],[11,4,10,5],[3,10,4,9]]

#link = [[8, 3, 1, 4], [4, 7, 5, 8], [5, 2, 6, 3], [1, 6, 2, 7]]

#link = [(2, 1, 3, 2), (6, 3, 1, 4), (5, 4, 6, 5)]

#link = [(4, 1, 5, 2), (2, 3, 3, 4), (8, 5, 1, 6), (7, 6, 8, 7)]

def getLEwithPD( link ):
    LE = snappy.Link( link ).view()

    components = LE.crossing_components()

    LE.style_var.set('pl')
    LE.set_style()
    #c = LE.canvas
    #corners = {}
    #crosses = {}
    LE.info_var.set(1)

    LE.update_info()
    LE.show_DT()

    #code = []
    crossings = {}
    for crossing in LE.Crossings:
        crossings[str( crossing )] = crossing
    comps = []
    for complist in components:
        comp = []
        #print( "new component" )
        for ecrossing in complist:
            crossing = crossings[str(ecrossing.crossing)]
            comp.append( {"a":abs( crossing.hit1 ), "b":abs( crossing.hit2 )} )
            #if crossing.flipped:
            #    comp.append( {"a":abs( crossing.hit2 ), "b":abs( crossing.hit1 )} )
            #else:
            #    comp.append( {"a":abs( crossing.hit1 ), "b":abs( crossing.hit2 )} )
        comps.append( comp )
            #continue
                    
            #print( ecrossing )
            #emptycrossing = ecrossing.crossing
            #print( "ecrossing crossing:", ecrossing.crossing )
            #for crossing in LE.Crossings:
                #print( "test crossing:", crossing )
                #input()
            #    if crossing == emptycrossing:
            #        if crossing.flipped:
            #            comp.append( {"first":abs( crossing.hit2 ), "second":abs( crossing.hit1 )} )
            #        else:
            #            comp.append( {"first":abs( crossing.hit1 ), "second":abs( crossing.hit2 )} )
            #        break
        #comps.append( comp )
    #print( comps )

    strandcomps = []
    usedLabels = set()

    for comp in comps:
        compsize = len( comp )
        for initchoice in ["a","b"]:
            strandcomp = []
            if comp[0][initchoice] not in usedLabels:
                prev = comp[0][initchoice]
                strandcomp.append( prev )
                for j in range( 1, compsize ):
                    keepGoing = False
                    for elt in [comp[j]["a"],comp[j]["b"]]:
                        if elt not in usedLabels and\
                           (elt == prev+1 or elt == prev-compsize+1):
                            prev = elt
                            strandcomp.append( prev )
                            keepGoing = True
                            break
                    if not keepGoing:
                        break
                if keepGoing:
                    strandcomps.append( strandcomp )
                    usedLabels = usedLabels.union( set( strandcomp ) )
                    break
                else:
                    continue
                
    #print( strandcomps )

    prevOf = {}
    for i in range( len( strandcomps ) ):
        compsize = len( strandcomps[i] )
        for j in range( len( strandcomps[i] ) ):
            prevOf[strandcomps[i][j]]=strandcomps[i][(j-1)%compsize]

    #print( prevOf )

    pdcode = []

    for crossing in crossings:
        crs = crossings[crossing]
        if crs.flipped:
            first,second = abs( crs.hit2 ), abs( crs.hit1 )
        else:
            first,second = abs( crs.hit1 ), abs( crs.hit2 )
        # this pays no attention to whether the crossing is under or over
        # so it likely changes the link in general
        # pay attention to the signs if this becomes necessary
        # alternatively, you can modify the crossing so that components always
        # show up in a certain order
        pdcode.append((prevOf[first],prevOf[second],first,second))

    return LE, pdcode, strandcomps
    #if pdcode != [(1, 6, 2, 1), (2, 5, 3, 6), (4, 3, 5, 4)]:
    #    LE.done()
    #else:
    #    input()

    #f = open( sys.argv[2], 'w' )

    #f.write( str( pdcode ) )
    #f.close()
    #print( "hi" )
    #if pdcode == [[1, 6, 2, 1], [2, 5, 3, 6], [4, 3, 5, 4]]:
    #    print
    #input()
    #LE.done()
if __name__ == "__main__":
    main()
    
"""def attempt1():
    for i in range( len( comps ) ):
        compsize = len( comps[i] )
        prev1 = comps[i][0]["a"]
        prev2 = comps[i][0]["b"]
        print( prev1, prev2, usedLabels )
        input()
        if prev1 not in usedLabels:
            list1 = [prev1]
        else:
            list1 = None
        if prev2 not in usedLabels:
            list2 = [prev2]
        else:
            list2 = None
        
        for j in range( 1, compsize ):
            for elt in [comps[i][j]["a"],comps[i][j]["b"]]:
                if list1 is not None:
                    if elt == prev1+1 or elt == prev1-compsize+1:
                        #usedLabels.add( elt )
                        list1.append( elt )
                        prev1 = elt
                if list2 is not None:
                    if elt == prev2+1 or elt == prev2-compsize+1:
                        #usedLabels.add( elt )
                        list2.append( elt )
                        prev2 = elt
        print( list1, list2 )
        if list1 is not None and len( list1 ) == compsize:
            strandcomps.append( list1 )
            usedLabels = usedLabels.union( set( list1 ) )
        else:
            strandcomps.append( list2 )
            usedLabels = usedLabels.union( set( list2 ) )
        if list1 is not None and list2 is not None and len( list1 ) == len( list2 ):
            print( "lists have the same size so there could be ambiguity" )
            assert( False )
        if (list1 is not None and len( list1 ) < compsize)\
           or (list2 is not None and len( list2 ) < compsize):
            print( "Neither list is long enough" )
            assert( False )
        if list1 is None and list2 is None:
            print( "Both lists are empty...that doesn't make any sense" )
            assert( False)"""


    
    


                    


    



#for component in LE.crossing_components():
#    compLabels[str(component)] = i
#    i+=1

#print( compLabels )


"""compLabels = {}
i = 0
for crossing in LE.Crossings:
    crossing.locate()
    if str( crossing.comp1 ) not in compLabels:
        compLabels[ str( crossing.comp1 ) ] = i
        i+=1
    if str( crossing.comp2 ) not in compLabels:
        compLabels[ str( crossing.comp2 ) ] = i
        i+=1
    flipped = crossing.flipped
    hit1 = abs( crossing.hit1 )
    hit2 = abs( crossing.hit2 )
    comp1 = compLabels[str( crossing.comp1 )]
    comp2 = compLabels[str( crossing.comp2 )]
    if flipped:
        print( "flipped")
        print( "(comp1,hit2)=", (comp1,hit2) )
        print( "(comp2,hit1)=", (comp2,hit1) )
    else:
        print( "not flipped")
        print( "(comp1,hit1)=", (comp1,hit1) )
        print( "(comp2,hit2)=", (comp2,hit2) )
    print()"""
    
#print( comps )

#print( compLabels )
#    print( "NEW COMPONENT" )
#    for ecrossing in component:
#        print( ecrossing.crossing.hit1, ecrossing.crossing.hit2 )
#        print( ecrossing.arrow )
#        print( ecrossing.strand )
#        print()
#for crossing in LE.Crossings:
    #flipped = crossing.flipped
#    hit1 = crossing.hit1
#    hit2 = crossing.hit2
#    if str( crossing.comp1 ) not in comps:
#        comps[ str( crossing.comp1 ) ] = {"hit1list":[abs(hit1)],\
#                                           "hit2list":[abs(hit2)]}
#    else:
#        comps[ str( crossing.comp1 ) ]["hit1list"].append(abs(hit1))
#        comps[ str( crossing.comp1 ) ]["hit2list"].append(abs(hit2))
#    if str( crossing.comp2 ) not in comps:
#        comps[ str( crossing.comp2 ) ] = {"hit1list":[abs(hit1)],\
#                                       "hit2list":[abs(hit2)]}
#    else:
#        comps[ str( crossing.comp2 ) ]["hit1list"].append(abs(hit1))
#        comps[ str( crossing.comp2 ) ]["hit2list"].append(abs(hit2))


#print( comps )

#else:
#for cross2 in crossing.comp1:
#    print( cross2

#print( crossing.flipped )
#print( crossing.hit1, crossing.hit2 )
#print( len( crossing.comp1 ), len( crossing.comp2 ) )
#print()
#hit1 = crossing.hit1
#hit2 = crossing.hit2
#if flipped:
        
#code = LE.PD_code()

#f = open( sys.argv[2], 'w' )

#f.write( str( code ) )
#f.close()
#print( "hi" )
#LE.done()

