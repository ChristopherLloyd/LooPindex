# Author: Ryan Pham
# Date: 7/27/25
# Modified by Ben Stucky

# this module contains several functions
# 1) a function which computes whether a plane curve given by a perm rep is self overlapping
# 2) a function which computes all mobidiscs for a given a multiloop
# 3) a function which computes all unicorn annuli for a given multiloop
from permrep import Multiloop
from circlepack import CirclePack
from drawloop import generate_circles, drawloop


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

def test1():
    example_loop = Multiloop([[-4, -3, 1, -1], [3, 4, -2, 2]])
    example_loop.inf_face = [-2]
    # example_loop = perm.Multiloop(
    #     [
    #         (9, 14, -10, -1),
    #         (7, 2, -8, -3),
    #         (3, 6, -4, -7),
    #         (11, 4, -12, -5),
    #         (1, 8, -2, -9),
    #         (13, 10, -14, -11),
    #         (5, 12, -6, -13),
    #     ]
    # )
    # example_loop.inf_face = (-2, 7, -4, 11, -14, 9)
    sequences, packed_circles, packed_circles_simplified, assigned_circles = get_draw_data( example_loop )
    #loop_to_circles = generate_circles(example_loop)
    #packed_circles = CirclePack(
    #    loop_to_circles["internal"], loop_to_circles["external"]
    #)
    print(example_loop)
    #print("TWO:", assigned_circles["sequences"] )
    print( packed_circles )
    drawloop(packed_circles, sequences=assigned_circles["sequences"], scale=500)

    print(is_self_overlapping(sequences, packed_circles_simplified))

def test2():
    name = '16^3_97'
    #name = '10^1_18'
    pd = eval( getFieldByName( "pd", name ) )
    #print( pd )
    sigma = sigmaFromPDCode(pd)[0]
    #print( sigma )
    loop = Multiloop( sigma )
    #print(len(get_draw_data( loop )))
    sequences, packed_circles, packed_circles_simplified, assigned_circles = get_draw_data( loop )
    print( assigned_circles["sequences"] )
    drawloop(packed_circles, sequences=assigned_circles["sequences"], scale=500)
    print(is_self_overlapping(sequences, packed_circles_simplified))

def test3():
    name = '11^1_97'
    #name = '10^1_18'
    pd = eval( getFieldByName( "drawnpd", name ) )
    #print( pd )
    
    sigma = sigmaFromPDCode(pd)[0]
    print( sigma )
    loop = Multiloop( sigma )
    #print( loop.inf_face )
    #print( loop.phi )
    loop.inf_face = selectInfRegion( loop )
    #print(len(get_draw_data( loop )))
    sequences, packed_circles, packed_circles_simplified, assigned_circles = get_draw_data( loop )
    #print( assigned_circles )
    #circlesToVerts = {}
    #vertsToCircles = {}
    # we need to be able to associate circles to vertices and vice versa
    # is it true that the circle label is just the index in sigma+1?
    #for vert in sigma:
    #    circlesToVerts[assigned_circles["circles"].vertices[vert[0]]]=vert
    #print( "circles to verts", circlesToVerts )

    # we need to be able to associate half-edge labels to the vertices that contain them as well as the
    # circle id of that vertex
    halfEdgeToContainingVert = {}
    for vertIndex in range( len( sigma ) ): 
        for he in sigma[vertIndex]:
            halfEdgeToContainingVert[he] = {"vert":sigma[vertIndex],"circle":vertIndex+1}

    print( halfEdgeToContainingVert )
    
    #print( sequences )
    #print( packed_circles )
    drawloop(packed_circles, sequences=assigned_circles["sequences"], scale=500)
    print(is_self_overlapping(sequences, packed_circles_simplified))

def selectInfRegion( mloop ):
    print( "Regions:")
    for i in range( 1, len( mloop.phi )+1 ):
        print( i, ": ", mloop.phi[i-1] )
    try:
        sel = int(input( "Select infinite region: "))
    except ValueError:
        print( "Bad input, using first region...")
        sel = 1
    return mloop.phi[sel-1]

def main():
    #test1()
    #test2()
    #test3()
    #return
    name = '11^1_97' # infinite region 10

    #from front page of paper
    name = '9^1_5' # infinite region 1

    #interesting multisimple
    name = '12^3_56' # infinite region 6

    #minimal example with different cardinalities
    #name = '8^1_2' # infinite region 5
    mobidisc_clause( name )

def mobidisc_clause( name, sphere = False ):    
    #name = '10^1_18'
    oloop = getFieldByName( "pd", name )
    loop = eval( getFieldByName( "drawnpd", name ) )
    debug = False

    #trefoil plus a monogon:
    #loop = [(1,5,2,4),(2,5,3,6),(3,7,4,6),(8,8,1,7)]

    # properly immersed with monogon
    # it's currently not working quite right for this - try making 5 the infinite region
    #loop = [(2,5,3,6),(1,7,2,6),(4,8,5,7),(3,10,4,11),(8,10,9,9),(12,11,1,12)]

    
    #loop = [[12,7,1,8],[8,4,9,3],[11,2,12,3],[6,1,7,2],[4,10,5,9],[5,10,6,11]]

    #properly immersed no monogon
    # infinite region has 5 on the outside: 6
    #loop = [(1,7,2,6),(3,8,4,9),(4,12,5,11),(7,14,8,15),(2,15,3,16),(10,18,11,17),(5,21,6,20),(9,18,10,19),(16,19,17,20),(24,22,1,21),(13,23,14,22),(12,23,13,24)]

    #pretty big one, 94 faces
    #takes too long. but also the code is unoptimized, one big optimization would be not to compute
    #any monogon words at all, which is almost certainly valid for the computation (assuming no monogon regions)
    loop = [(184,20,1,19),(6,27,7,28),(9,37,10,36),(13,40,14,41),(30,47,31,48),(32,46,33,45),(16,52,17,51),(22,55,23,56),(24,60,25,59),(38,61,39,62),(39,67,40,66),(8,69,9,70),(60,67,61,68),(34,71,35,72),(14,78,15,77),(42,76,43,75),(52,79,53,80),(17,80,18,81),(29,85,30,84),(33,86,34,87),(74,90,75,89),(12,92,13,91),(65,93,66,92),(10,95,11,96),(44,100,45,99),(62,93,63,94),(72,97,73,98),(87,98,88,99),(5,105,6,104),(48,101,49,102),(58,108,59,107),(83,103,84,102),(56,109,57,110),(1,112,2,113),(50,116,51,115),(81,114,82,115),(76,118,77,117),(41,118,42,119),(90,120,91,119),(35,123,36,122),(70,123,71,124),(96,121,97,122),(28,125,29,126),(103,127,104,126),(4,128,5,127),(20,132,21,131),(111,130,112,131),(54,134,55,133),(23,134,24,135),(57,136,58,137),(108,136,109,135),(25,141,26,140),(106,139,107,140),(7,142,8,143),(124,144,125,143),(46,146,47,145),(85,144,86,145),(31,146,32,147),(100,148,101,147),(15,151,16,150),(78,152,79,151),(116,149,117,150),(53,152,54,153),(18,153,19,154),(113,155,114,154),(2,156,3,155),(129,156,130,157),(26,160,27,159),(105,158,106,159),(37,162,38,163),(68,162,69,161),(94,164,95,163),(141,161,142,160),(64,166,65,165),(11,168,12,169),(43,173,44,172),(63,166,64,167),(73,170,74,171),(88,171,89,172),(120,170,121,169),(164,167,165,168),(148,173,149,174),(3,177,4,176),(49,174,50,175),(82,176,83,175),(128,177,129,178),(138,180,139,179),(157,179,158,178),(137,180,138,181),(21,183,22,182),(110,181,111,182),(132,184,133,183)]

    # big but smaller, 49 faces
    # takes at least 15 minutes to generate the mobidisc cnf
    # took about half and hour
    loop = [(1,16,2,17),(7,21,8,20),(10,25,11,26),(13,29,14,28),(5,34,6,35),(19,36,20,37),(4,40,5,39),(18,38,19,37),(23,44,24,45),(32,42,33,41),(9,46,10,47),(8,48,9,47),(14,55,15,56),(21,49,22,48),(30,53,31,54),(42,52,43,51),(11,59,12,58),(26,58,27,57),(43,60,44,61),(6,63,7,64),(35,64,36,65),(49,63,50,62),(38,66,39,65),(2,68,3,67),(29,71,30,70),(54,69,55,70),(24,73,25,74),(59,73,60,72),(45,74,46,75),(22,76,23,75),(50,78,51,77),(61,76,62,77),(33,78,34,79),(15,82,16,83),(40,80,41,79),(68,82,69,81),(94,83,1,84),(17,85,18,84),(66,85,67,86),(3,87,4,86),(31,89,32,88),(52,89,53,90),(80,87,81,88),(12,91,13,92),(71,91,72,90),(27,92,28,93),(56,94,57,93)]
    #pd = eval( getFieldByName( "drawnpd", name ) )
    #print( pd )

    # big handdrawn multisimple
    loop =[(2,75,3,146),(69,78,70,77),(71,75,72,76),(40,85,41,84),(41,83,42,84),(52,83,53,82),(54,80,55,81),(4,86,5,87),(5,88,6,87),(25,91,26,92),(28,93,29,92),(39,93,40,94),(42,95,43,94),(51,95,52,96),(55,98,56,97),(64,98,65,99),(15,109,16,110),(23,108,24,107),(30,106,31,107),(37,106,38,105),(44,104,45,105),(50,103,51,102),(56,100,57,101),(63,100,64,99),(13,112,14,111),(9,113,10,114),(67,116,68,115),(11,128,12,127),(18,126,19,127),(21,126,22,125),(32,124,33,125),(34,123,35,122),(47,121,48,122),(48,121,49,120),(58,118,59,119),(61,118,62,117),(66,116,67,117),(74,144,1,145),(12,128,13,129),(16,131,17,130),(22,132,23,133),(31,134,32,133),(36,134,37,135),(45,136,46,135),(49,137,50,138),(57,140,58,139),(62,140,63,141),(65,142,66,141),(68,142,69,143),(73,144,74,143),(1,148,2,147),(72,148,73,149),(145,147,146,192),(70,151,71,150),(76,149,77,150),(78,152,79,151),(79,152,80,153),(53,153,54,154),(81,155,82,154),(96,155,97,156),(101,157,102,156),(119,159,120,158),(138,157,139,158),(59,160,60,159),(60,160,61,161),(33,162,34,161),(123,162,124,163),(35,163,36,164),(46,165,47,164),(103,166,104,167),(136,166,137,165),(24,171,25,170),(29,169,30,170),(38,169,39,168),(43,167,44,168),(108,172,109,171),(131,172,132,173),(17,173,18,174),(129,175,130,174),(14,177,15,176),(26,178,27,179),(90,178,91,177),(110,175,111,176),(27,180,28,179),(7,181,8,182),(89,180,90,181),(8,183,9,182),(10,184,11,185),(19,186,20,185),(112,184,113,183),(20,186,21,187),(114,187,115,188),(6,189,7,188),(88,190,89,189),(3,191,4,192),(85,190,86,191)]
    
    # another one with a tree, use infregion 9
    loop = [(9,31,10,60),(8,31,9,32),(6,34,7,33),(11,34,12,35),(27,39,28,38),(1,40,2,41),(4,44,5,43),(13,44,14,45),(16,46,17,45),(25,46,26,47),(19,49,20,48),(23,50,24,51),(21,53,22,52),(20,53,21,54),(5,58,6,59),(12,58,13,57),(17,56,18,57),(24,56,25,55),(7,62,8,63),(10,62,11,61),(32,64,33,63),(35,84,36,61),(59,64,60,65),(3,67,4,66),(14,67,15,68),(15,69,16,68),(42,66,43,65),(22,74,23,73),(26,69,27,70),(47,70,48,71),(51,72,52,73),(54,72,55,71),(18,75,19,76),(49,75,50,74),(28,78,29,77),(37,76,38,77),(39,79,40,78),(2,79,3,80),(41,80,42,81),(30,82,1,81),(29,82,30,83),(36,84,37,83)]
    loop = [(9,33,10,64),(8,33,9,34),(6,36,7,35),(11,36,12,37),(29,41,30,40),(1,42,2,43),(4,46,5,45),(13,46,14,47),(16,48,17,47),(25,48,26,49),(19,53,20,52),(23,54,24,55),(21,57,22,56),(20,57,21,58),(5,62,6,63),(12,62,13,61),(17,60,18,61),(24,60,25,59),(7,66,8,67),(10,66,11,65),(34,68,35,67),(37,88,38,65),(63,68,64,69),(3,71,4,70),(14,71,15,72),(15,73,16,72),(44,70,45,69),(22,78,23,77),(26,73,27,74),(49,74,50,75),(55,76,56,77),(58,76,59,75),(18,79,19,80),(53,79,54,78),(30,82,31,81),(39,80,40,81),(41,83,42,82),(2,83,3,84),(43,84,44,85),(32,86,1,85),(31,86,32,87),(38,88,39,87),(50,27,51,28),(51,29,52,28)]
    # inf region 10
    loop = [(9,37,10,72),(8,37,9,38),(6,40,7,39),(11,40,12,41),(33,45,34,44),(1,46,2,47),(4,50,5,49),(13,50,14,51),(16,52,17,51),(27,52,28,53),(19,59,20,58),(25,60,26,61),(23,63,24,62),(21,64,22,65),(5,70,6,71),(12,70,13,69),(17,68,18,69),(26,68,27,67),(7,74,8,75),(10,74,11,73),(38,76,39,75),(41,104,42,73),(71,76,72,77),(3,79,4,78),(14,79,15,80),(15,81,16,80),(48,78,49,77),(24,86,25,85),(28,81,29,82),(53,82,54,83),(61,84,62,85),(66,84,67,83),(18,87,19,88),(59,87,60,86),(34,98,35,97),(43,96,44,97),(45,99,46,98),(2,99,3,100),(47,100,48,101),(36,102,1,101),(35,102,36,103),(42,104,43,103),(55,30,56,31),(56,32,57,31),(57,88,58,89),(29,95,30,94),(32,95,33,96),(54,94,55,93),(65,92,66,93),(20,90,21,89),(22,91,23,92),(63,91,64,90)]
    # inf region 33
    loop =[(35,6,36,7),(9,36,10,37),(31,41,32,40),(1,42,2,43),(45,4,46,5),(11,46,12,47),(47,14,48,15),(25,48,26,49),(17,55,18,54),(23,56,24,57),(21,59,22,58),(19,60,20,61),(5,66,6,67),(65,10,66,11),(15,64,16,65),(63,24,64,25),(7,98,8,97),(96,35,97,68),(67,96,68,95),(3,93,4,94),(92,12,93,13),(13,91,14,92),(94,45,95,44),(86,23,87,22),(90,26,91,27),(49,90,50,89),(57,88,58,87),(88,63,89,62),(84,16,85,17),(55,85,56,86),(74,33,75,32),(39,76,40,75),(41,73,42,74),(72,2,73,3),(43,72,44,71),(51,28,52,29),(29,52,30,53),(53,84,54,83),(27,77,28,78),(76,30,77,31),(78,51,79,50),(61,80,62,79),(82,19,83,18),(80,20,81,21),(59,81,60,82),(8,98,9,99),(34,70,1,71),(33,70,34,69),(38,100,39,69),(37,100,38,99)]
    #loop = [(9,35,10,70),(36,8,37,7),(38,5,39,6),(10,39,11,40),(32,42,33,41),(34,43,1,44),(46,3,47,4),(12,47,13,48),(48,15,49,16),(26,49,27,50),(18,56,19,55),(24,57,25,58),(22,60,23,59),(20,61,21,62),(4,67,5,68),(66,11,67,12),(16,65,17,66),(64,25,65,26),(6,100,7,99),(98,38,99,37),(68,98,69,97),(2,95,3,96),(94,13,95,14),(14,93,15,94),(96,46,97,45),(88,24,89,23),(92,27,93,28),(50,92,51,91),(58,90,59,89),(90,64,91,63),(86,17,87,18),(56,87,57,88),(76,34,77,33),(40,78,41,77),(42,75,43,76),(74,1,75,2),(44,74,45,73),(52,29,53,30),(30,53,31,54),(54,86,55,85),(28,79,29,80),(78,31,79,32),(80,52,81,51),(62,82,63,81),(84,20,85,19),(82,21,83,22),(60,83,61,84),(69,72,70,73),(8,71,9,72),(35,71,36,100)]
    #loop = [(9,37,10,72),(38,8,39,7),(40,5,41,6),(12,41,13,42),(34,44,35,43),(36,45,1,46),(48,3,49,4),(14,49,15,50),(50,17,51,18),(28,51,29,52),(20,58,21,57),(26,59,27,60),(24,62,25,61),(22,63,23,64),(4,69,5,70),(68,13,69,14),(18,67,19,68),(66,27,67,28),(6,102,7,101),(100,40,101,39),(70,100,71,99),(2,97,3,98),(96,15,97,16),(16,95,17,96),(98,48,99,47),(90,26,91,25),(94,29,95,30),(52,94,53,93),(60,92,61,91),(92,66,93,65),(88,19,89,20),(58,89,59,90),(78,36,79,35),(42,80,43,79),(44,77,45,78),(76,1,77,2),(46,76,47,75),(54,31,55,32),(32,55,33,56),(56,88,57,87),(30,81,31,82),(80,33,81,34),(82,54,83,53),(64,84,65,83),(86,22,87,21),(84,23,85,24),(62,85,63,86),(71,74,72,75),(8,73,9,74),(37,73,38,104),(11,102,12,103),(10,104,11,103)]
    sigma = sigmaFromPDCode(loop)[0]

    packedLoop = Multiloop( sigma )
    #print( "tau", packedLoop.tau )

    #print( packedLoop.tau.apply( 6 ) )

    #return
    #print( loop.inf_face )
    #print( loop.phi )
    packedLoop.inf_face = selectInfRegion( packedLoop )
    #print(len(get_draw_data( loop )))
    sequences, packed_circles, circle_to_coord, assigned_circles = get_draw_data( packedLoop )

    print( circle_to_coord )
    print( "VERTEX CIRCLES",assigned_circles["circles"].vertices)
    print( "EDGE CIRCLES",assigned_circles["circles"].edges)
    print( "FACE CIRCLES",assigned_circles["circles"].faces)

    print( "sequences:", assigned_circles["sequences"])
    print(is_self_overlapping(sequences, circle_to_coord))

    # associate face cycles to circles and circles to face cycles
    faceCycleToCircle = {}
    circleToFaceCycle = {}
    for faceIndex in range( len( packedLoop.phi )):
        facelabels = []
        for elt in packedLoop.phi[faceIndex]:
            facelabels.append( abs(elt) )
        faceKey = binHash(facelabels)
        circ = assigned_circles["circles"].faces[packedLoop.phi[faceIndex][0]]
        faceCycleToCircle[faceKey] = circ
        circleToFaceCycle[circ] = faceKey
        if packedLoop.phi[faceIndex] == packedLoop.inf_face:
            infRegion = faceKey
    print( faceCycleToCircle )
    print( circleToFaceCycle )

    
    #drawloop(packed_circles, sequences=assigned_circles["sequences"], scale=200, reg_dict = None )   
    drawloop(packed_circles, sequences=assigned_circles["sequences"], scale=75, reg_dict = {}, circleWidth = 0, mobidisc_data=None )    
    #drawloop(packed_circles, sequences=assigned_circles["sequences"], scale=200, reg_dict = None, circleWidth = 5, mobidisc_data=None )
    return

    # we need to be able to associate half-edge labels to the vertices that contain them as well as the
    # circle id of that vertex, and its coordinates
    #heToVertData = {}
    #for vertIndex in range( len( sigma ) ): 
    #    for he in sigma[vertIndex]:
    #        heToVertData[he] = {"vert":sigma[vertIndex],"circle":vertIndex+1,"coord":circle_to_coord[vertIndex+1]}
    #print( heToVertData )

    # finally we associate a half edge to the coordinate of the vertex containing it
    he_to_coord = {}

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
        """This function is currently wrong when there are multiple strands. 
        For example for simple multiloops it gets in infinite loops"""
        word = []
        curLabel = strtLabel
        #we have to do silly sign adjustments due to past transgressions
        #sgn = sign(0, strtLabel )
        circs = [assigned_circles["circles"].vertices[strtLabel]]

        #print( "startLabel", strtLabel )
        #print( "stpLabels", stpLabels)
        #goodCurLabel = strtLabel
        while curLabel not in stpLabels or curLabel == strtLabel:
            word.append( -curLabel )
            lastLabel = curLabel
            curLabel = -packedLoop.tau.apply( -curLabel )
            #curLabel = ( curLabel -  1 ) % (2*len( loop ))
            #circs.append()
            #if sgn < 0:
            #    curLabel -= 2*len(loop)             
            #if curLabel == 0:
            #    curLabel = 2*len( loop )
            #print( "curLabel", curLabel )
            #print( "from tau:", goodCurLabel )
            #curLabel = goodCurLabel
            #input()
            circs.append( assigned_circles["circles"].edges[lastLabel] )
            #print( "lastLabel:", lastLabel)
            if assigned_circles["circles"].edges[lastLabel] != assigned_circles["circles"].edges[-lastLabel]:
                #print( "HI" )
                #assert( False )
                circs.append( assigned_circles["circles"].edges[-lastLabel] )
            circs.append( assigned_circles["circles"].vertices[curLabel] )
            if curLabel == strtLabel:# and curLabel not in stpLabels:
                return None, None, None
        #print()
        #print( "CIRCS", circs  )
        #print()       
        return word, curLabel, circs
    

    def findBigon( x, y, startIndex1, startIndex2 ):
        stopLabelsY = y#[abs(y[0]),abs(y[1]),abs(y[2]),abs(y[3])]
        stopLabelsX = x#[abs(x[0]),abs(x[1]),abs(x[2]),abs(x[3])]

        #print( "Start:", x)
        #print( "Stop:", y)
        
        skip = False
        w1, stop1, circs1 = subWord( x[startIndex1], stopLabelsX+stopLabelsY )
        #print( "w1, stop1:", w1, stop1 )
        if w1 is None:
            return
        if stop1 in stopLabelsX:
            skip = True
        w2, stop2, circs2 = subWord( x[startIndex2], stopLabelsX+stopLabelsY )
        #print( "w2, stop2:", w2, stop2 )
        if w2 is None:
            return
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
            circs2.reverse()
            return w1, w2, circs1[:-1]+circs2[:-1]
        #print( "No corner at y")
            #bigonWords.append( Word(w1)/Word(w2) )
    
    monogonWords = []
    for vertcycle in s.sigma:
        stopLabels = [vertcycle[1],vertcycle[3]]
        for startLabel in [vertcycle[0], vertcycle[2]]:
            w, stop, circs = subWord( startLabel, stopLabels )
            if w is not None:
                monogonWords.append( [Word(w), vertcycle, circs[:-1]] )

        #if debug:
        #print( "Vertex ", vertcycle )
        #print( "Monogon words", monogonWords[-1], monogonWords[-2])
        #print()

    print( "Monogon words")
    for word in monogonWords:
        revWord = word[-1].copy()
        revWord.reverse()
        print( word[0], word[1], word[2], is_self_overlapping(word[-1], circle_to_coord) or is_self_overlapping(revWord, circle_to_coord) )
    print()

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
                bigonsToAdd.append( [Word(bigonSegs[0])/Word(bigonSegs[1]), x, y, bigonSegs[2]] )
                bigonCount += 1
                #print( x, y, Word(bigonSegs[0]), Word(bigonSegs[1]) )
                #print( "first")

            bigonSegs = findBigon( x, y, 2, 3)
            if bigonSegs is not None:
                bigonsToAdd.append( [Word(bigonSegs[0])/Word(bigonSegs[1]), x, y, bigonSegs[2]] )
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
                bigonsToAdd.append( [Word(bigonSegs[0])/Word(bigonSegs[1]), x, y, bigonSegs[2]] )
                bigonCount += 1
                #print( x, y, Word(bigonSegs[0]), Word(bigonSegs[1]) )
                #print( "third")

            # you can also skip the check below if you found one above (with our PD convention)

            bigonSegs = findBigon( x, y, 3, 0)
            if bigonSegs is not None:
                bigonsToAdd.append( [Word(bigonSegs[0])/Word(bigonSegs[1]), x, y, bigonSegs[2]] )
                bigonCount += 1
                #print( x, y, Word(bigonSegs[0]), Word(bigonSegs[1]) )
                #print( "fourth")
            
            #assert( bigonCount <= 2 )

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

    print( "Bigon words")
    for word in bigonWords:
        revWord = word[-1].copy()
        revWord.reverse()
        print( word[0], word[1], word[2], word[3], is_self_overlapping(word[-1], circle_to_coord) or is_self_overlapping(revWord, circle_to_coord) )
    print()


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
    labelToCirc = {}
    circlesToLabels = {}
    circToCirc = {}
    for i in range( len( regList ) ):
        regLabels[regList[i]] = i+1
        labelToCirc[i+1]=faceCycleToCircle[regList[i]]
        circlesToLabels[faceCycleToCircle[regList[i]]]=i+1
        circToCirc[faceCycleToCircle[regList[i]]]=faceCycleToCircle[regList[i]] #lol
    print( infRegion )
    

    #return

    monobigClause = dict()

    for j in range( len( regList ) ):#: in regList:
        if sphere:
            infRegion = regList[j]        
        for wordList in [monogonWords, bigonWords]:
            for word in wordList:
                #outer = {1}
                revWord = word[-1].copy()
                revWord.reverse()
                if not is_self_overlapping(word[-1], circle_to_coord) and not is_self_overlapping(revWord, circle_to_coord):
                    continue
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

                #print(" To remove: ")
                for clause in toRemove:
                    #print( "Removing:", monobigClause[clause] )
                    del monobigClause[clause]
                if not supset or subset:
                    monobigClause[frozenset( nonZeroWinding ) ]=word+[j+1]
                #if not innerSupSet or innerSubSet:
                #    monobigClause.add( frozenset( inner ) )

                #print( "monorbigon clause", monobigClause)

        if not sphere:
            break

    #print(monobigClause)

   

    f = open( 'mobidisc_cnf.txt', 'w')

    writeStr = ""
    print( "Monorbigon clause:")
    mobidiscs = {}
    i=0
    for disjunction in monobigClause:
        # translate old region labels to circle labels
        disj = []
        toWrite = ""     
        for elt in disjunction:
            disj.append( labelToCirc[elt] )
            #disj.append(elt)
            toWrite +=  str(labelToCirc[elt]) + " "
        writeStr += toWrite[:-1]+"\n"
        mobidiscs[i] ={"regions":disj}
        i+=1
        #disjunction = disj
        print( " clause: {:<30} at vertex/vertices: {:<40} and infinite region {:<10}".format( str(list( disj )), str( monobigClause[ disjunction ][1:-1]  ), monobigClause[ disjunction ][-1] ) )

    drawloop(packed_circles, sequences=assigned_circles["sequences"], scale=50, reg_dict = circToCirc, circleWidth = 0, mobidisc_data=mobidiscs )    
    #drawloop(packed_circles, sequences=assigned_circles["sequences"], scale=50, reg_dict = {}, circleWidth = 0, mobidisc_data=None )    
    #drawloop(packed_circles, sequences=assigned_circles["sequences"], scale=200, reg_dict = None, circleWidth = 5, mobidisc_data=None )    
    #drawloop(packed_circles, sequences=assigned_circles["sequences"], scale=100, reg_dict = circlesToLabels, circleWidth = 0, mobidisc_data=mobidiscs )

    f.close()

    # standard usage of murakami uno: shd 0 medium_mobidisc.txt -    
    # or: shd 0 medium_mobidisc.txt medium_mobidisc_sol.txt
    # use this syntax to create a temp file and read/execute with shd
    #echo "2 7\n6 3 9\n2 9 4\n5\n8\n6 7" > /dev/shm/temp_input.txt && shd 0 /dev/shm/temp_input.txt - && rm /dev/shm/temp_input.txt
    #echo "2 7\n6 3 9\n2 9 4\n5\n8\n6 7" > temp_input.txt && shd 0 temp_input.txt - && rm temp_input.txt
    #printf "2 7\n6 3 9\n2 9 4\n5\n8\n6 7" > /dev/shm/temp_input.txt && shd 0 /dev/shm/temp_input.txt - && rm /dev/shm/temp_input.txt

    return

    input( "Press any key to draw loop")
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





################### Ryan's code ################################


def cross_product(a: tuple, b: tuple, c: tuple) -> float:
    """Calculate the cross product of vectors AB and AC, where A, B, C are points in 2D space."""
    x1, y1 = a
    x2, y2 = b
    x3, y3 = c
    return (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)


def is_convex(a: tuple, b: tuple, c: tuple) -> bool:
    """Check if the points (x1, y1), (x2, y2), (x3, y3) form a convex angle (if it turns right at (x2, y2))."""
    # Using the cross product to determine the orientation
    return cross_product(a, b, c) < 0


def is_counterclockwise(a: tuple, b: tuple, c: tuple) -> bool:
    """Check if the points (x1, y1), (x2, y2), (x3, y3) are in counterclockwise order."""
    # Using is_convex to determine if the angle at 'c' is convex
    # If the angle is convex, then it is counterclockwise
    return is_convex(a, c, b)


def is_appear_counterclockwise(vertices: list[int]) -> bool:
    """Check if the indices appear in counterclockwise order around a vertex."""
    i, j, k, l, m = vertices  # l = k+1, m = k-1
    if not (j == l) and not is_counterclockwise(i, j, l):
        return False
    if not (j == l) and not is_counterclockwise(j, l, m):
        return False
    if not (m == i) and not is_counterclockwise(l, m, i):
        return False
    if not (m == i) and not is_counterclockwise(m, i, j):
        return False
    toggle = True
    if not is_counterclockwise(k, i, j):
        if not toggle:
            return False
        toggle = False
    if not (j == l) and not is_counterclockwise(k, j, l):
        if not toggle:
            return False
        toggle = False
    if not is_counterclockwise(k, l, m):
        if not toggle:
            return False
        toggle = False
    if not (m == i) and not is_counterclockwise(k, m, i):
        if not toggle:
            return False
        toggle = False
    return True


def is_intersect_interior(a: tuple, b: tuple, triangle: list[tuple]) -> bool:
    def is_intersect(a: tuple, b: tuple, c: tuple, d: tuple) -> bool:
        """Check if line segments AB and CD intersect."""
        # Using the cross product to determine if segments intersect
        return (
            cross_product(a, b, c) * cross_product(a, b, d) < 0
            and cross_product(c, d, a) * cross_product(c, d, b) < 0
        )

    for i in range(3):
        s1 = triangle[i]
        s2 = triangle[(i + 1) % 3]
        if is_intersect(a, b, s1, s2):
            return True
    return False

def get_draw_data( multiloop ):
    assigned_circles = generate_circles(multiloop)
    packed_circles = CirclePack(
        assigned_circles["internal"], assigned_circles["external"]
    )
    sequences = assigned_circles["sequences"][0]["circle_ids"]
    packed_circles_simplified = {}
    for circle_id, (center, radius) in packed_circles.items():
        packed_circles_simplified[circle_id] = (center.real, center.imag)
    tup = (sequences, packed_circles, packed_circles_simplified, assigned_circles)
    return tup

def is_self_overlapping(sequences, packed_circles ):#multiloop: "Multiloop") -> bool:
    #assigned_circles = generate_circles(multiloop)
    #packed_circles = CirclePack(
    #    assigned_circles["internal"], assigned_circles["external"]
    #)
    #sequences = assigned_circles["sequences"][0]["circle_ids"]
    #for circle_id, (center, radius) in packed_circles.items():
    #    packed_circles[circle_id] = (center.real, center.imag)

    #print(sequences)
    #print( packed_circles )

    n = len(sequences)
    q = [[0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        q[i][(i + 1) % n] = 1
        q[i][(i + 2) % n] = (
            1
            if is_convex(
                packed_circles[sequences[i % n]],
                packed_circles[sequences[(i + 1) % n]],
                packed_circles[sequences[(i + 2) % n]],
            )
            else 0
        )
    for length in range(3, n):
        for i in range(n):
            j = (i + length) % n
            for k in range(n):
                #print(
                #    f"Checking i={i}, j={j}, k={k}, circles={sequences[i % n]}, {sequences[j % n]}, {sequences[k % n]}"
                #)
                # Check if Q[i][k] = Q[k][j] = 1
                if not q[i][k % n] or not q[k % n][j % n]:
                    #print(f"Skipping k={k} due to Q[i][k] or Q[k][j] not being 1")
                    continue
                if not (i <= k <= j) and (i < j):
                    #print("294928473")
                    raise ValueError(
                        "Invalid k index: k must be between i and j in the sequence."
                    )
                if not (k >= i or k <= j) and (i > j):
                    #print("artkarenst")
                    raise ValueError(
                        "Invalid k index: k must be between i and j in the sequence."
                    )
                #print(f"Q[i][k] and Q[k][j] are both 1 for k={k}")
                # Check if v[i]v[j]v[k] is oriented counterclockwise
                if not is_counterclockwise(
                    packed_circles[sequences[i % n]],
                    packed_circles[sequences[j % n]],
                    packed_circles[sequences[k % n]],
                ):
                    #    print(f"Skipping k={k} due to counterclockwise orientation")
                    continue
                #print(f"v[i]v[j]v[k] is oriented counterclockwise for k={k}")
                # Check if v[i], v[j], v[k+1], and v[k-1], appear in that order counterclockwise around v[k]
                # if not is_appear_counterclockwise(
                #     [
                #         packed_circles[sequences[i % n]],
                #         packed_circles[sequences[j % n]],
                #         packed_circles[sequences[(k) % n]],
                #         packed_circles[sequences[(k + 1) % n]],
                #         packed_circles[sequences[(k - 1) % n]],
                #     ]
                # ):
                #     print(f"Skipping k={k} due to appearance order around v[k]")
                #     continue
                ##print(
                #   f"v[i], v[j], v[k+1], and v[k-1] appear in counterclockwise order around v[k] for k={k}"
                #)
                # Check if the following four segments intersect the interior of v[i]v[j]v[k]: v[i]v[i+1],, v[k-1]v[k], v[k]v[k+1], and v[j-1]v[j]
                if is_intersect_interior(
                    packed_circles[sequences[i % n]],
                    packed_circles[sequences[(i + 1) % n]],
                    [
                        packed_circles[sequences[i % n]],
                        packed_circles[sequences[j % n]],
                        packed_circles[sequences[k % n]],
                    ],
                ):
                #    print(f"Skipping k={k} due to intersection with v[i]v[i+1]")
                    continue

                if is_intersect_interior(
                    packed_circles[sequences[(k - 1) % n]],
                    packed_circles[sequences[k % n]],
                    [
                        packed_circles[sequences[i % n]],
                        packed_circles[sequences[j % n]],
                        packed_circles[sequences[k % n]],
                    ],
                ):
                #    print(f"Skipping k={k} due to intersection with v[k-1]v[k]")
                    continue

                if is_intersect_interior(
                    packed_circles[sequences[k % n]],
                    packed_circles[sequences[(k + 1) % n]],
                    [
                        packed_circles[sequences[i % n]],
                        packed_circles[sequences[j % n]],
                        packed_circles[sequences[k % n]],
                    ],
                ):
                #    print(f"Skipping k={k} due to intersection with v[k]v[k+1]")
                    continue

                if is_intersect_interior(
                    packed_circles[sequences[(j - 1) % n]],
                    packed_circles[sequences[j % n]],
                    [
                        packed_circles[sequences[i % n]],
                        packed_circles[sequences[j % n]],
                        packed_circles[sequences[k % n]],
                    ],
                ):
                #    print(f"Skipping k={k} due to intersection with v[j-1]v[j]")
                    continue
                #print(f"All condition checks passed for k={k}")
                # If we reach here, it means there exists an index k that satisfies the conditions
                q[i][j % n] = 1
                break

    #print("Table Q:")
    #for row in q:
    #    print(row)

    for i in range(n):
        if q[i][i - 1] == 1:
            # If we find a self-overlapping condition, we can return True immediately
            return True

    return False

if __name__ == "__main__":
    main()
