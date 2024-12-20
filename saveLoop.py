import snappy
import sys
import traceback
from tkinter import font
from plinkpd2 import getLEwithPD
from sage.all import Polyhedron, QQ, Rational, RDF

#print( len( sys.argv ) )

# remove arrowheads by editing the svg file directly and removing all the <polygon> tags
# remove the component labels while you're at it
# https://stackoverflow.com/questions/42206123/python-remove-html-tag-with-regex
# https://stackoverflow.com/questions/3951660/how-to-replace-the-first-occurrence-of-a-regular-expression-in-python
import re
def cleanFile():
    f = open( filename, 'r' )
    toParse = f.read()
    f.close()
    removedArrows = re.sub(r'<polygon.+?/>', '',toParse)
    removedComponentLabels = re.sub(r'<text.+?<circle', '<circle',removedArrows,1)
    thickened = re.sub(r'stroke-width="3.0"', 'stroke-width="6.0"',removedComponentLabels )
    transparentRects = re.sub(r'<rect x', '<rect opacity = "0.8" x',thickened )
    f = open( filename, 'w' )
    f.write( transparentRects )
    f.close()

if len( sys.argv ) > 2:
    
    # get args from command line
    data = eval( sys.argv[1] )
    link = eval( data["link"] )
    #print( data )
    #input()
    drawnpd = data["drawnpd"]
    adjDict = data["adjDict"]
    regWords = data["regWords"]
    minPinSets = data["minPinSets"]
    tolerance = data["tolerance"]
    minPinSetDict = data["minPinSetDict"]
    regLabels = data["regionLabels"]
    components = data["components"]
    filename = data["filename"]
    debug = data["debug"]
    bufferFrac = data["bufferFrac"]
    diamFrac = data["diamFrac"]
    annotated = data["annotated"]

else: #debug test cases
    # test case with 1 strand
    tolerance = 0.0000001
    
    link = [[8, 3, 1, 4], [4, 7, 5, 8], [5, 2, 6, 3], [1, 6, 2, 7]]
    drawnpd = [(3, 8, 4, 1), (6, 1, 7, 2), (7, 4, 8, 5), (2, 5, 3, 6)]
    components = [[3, 4, 5, 6, 7, 8, 1, 2]]    

    # test case with 2 strands
    link = [[4, 8, 1, 5], [5, 3, 6, 4], [7, 1, 8, 2], [2, 6, 3, 7]]
    drawnpd = [(5, 4, 6, 1), (7, 2, 8, 3), (1, 8, 2, 5), (3, 6, 4, 7)]
    drawnpdold = [(6, 4, 7, 1), (8, 2, 5, 3), (1, 5, 2, 6), (3, 7, 4, 8)]
    components = [[6, 7, 8, 5], [4, 1, 2, 3]]

    #link = [[1, 6, 2, 1], [2, 5, 3, 6], [4, 3, 5, 4]]
    #drawnpd= [(2, 1, 3, 2), (6, 3, 1, 4), (5, 4, 6, 5)]
    #components = [[2, 3, 4, 5, 6, 1]]

    # a few more multiloops to try
    link = [[6, 12, 1, 7], [7, 5, 8, 6], [8, 11, 9, 12], [1, 4, 2, 5],\
            [10, 16, 11, 13], [9, 16, 10, 15], [3, 14, 4, 15], [2, 14, 3, 13]]
    drawnpd= [(5, 2, 6, 3), (12, 3, 13, 4), (13, 16, 14, 11), (4, 11, 5, 12), (7, 6, 8, 1), (1, 8, 2, 9), (9, 14, 10, 15), (15, 10, 16, 7)]
    components= [[1, 2, 3, 4, 5, 6], [14, 15, 16, 11, 12, 13], [8, 9, 10, 7]]

    #link = [[4, 10, 1, 5], [5, 3, 6, 4], [6, 9, 7, 10], [1, 7, 2, 8], [8, 2, 9, 3]]
    #drawnpd= [(5, 4, 6, 1), (8, 3, 9, 4), (6, 9, 7, 10), (1, 10, 2, 5), (2, 7, 3, 8)]
    #components= [[1, 2, 3, 4], [9, 10, 5, 6, 7, 8]]

    #link = [[5, 2, 6, 3], [12, 3, 13, 4], [13, 16, 14, 11], [4, 11, 5, 12],\
    #        [7, 6, 8, 1], [1, 8, 2, 9], [9, 14, 10, 15], [15, 10, 16, 7]]
    #drawnpd= [(7, 6, 8, 1), (16, 3, 13, 4), (2, 5, 3, 6), (4, 13, 5, 14), (10, 15, 11, 16), (14, 9, 15, 10), (8, 11, 9, 12), (1, 12, 2, 7)]
    #components= [[1, 2, 3, 4, 5, 6], [14, 15, 16, 13], [8, 9, 10, 11, 12, 7]]

    #link = [[6,7,1,8],[2,9,3,10],[8,1,9,2],[10,3,11,4],[4,11,5,12],[12,5,7,6]]
    #drawn = [(8, 1, 9, 2), (10, 3, 11, 4), (12, 5, 7, 6), (6, 7, 1, 8), (2, 9, 3, 10), (4, 11, 5, 12)]
    #components = [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]]


#print(drawnpd, ",---")    

# necessary for floating point nonsense
def closeTo( x0, y0, pointDict ):
    assert( len( pointDict ) != 0 )
    #print( "len(pointDict)=", len( pointDict ) )
    #nonlocal tolerance
    for key in pointDict:
        point1 = key
        break
    #point1
    mindist = abs( x0 - point1[0] )+abs( y0 - point1[1] )
    closestPoint = (point1[0], point1[1])
    for point in pointDict:
        nextd = abs( x0 - point[0] )+abs( y0 - point[1] )
        if nextd < mindist:
            mindist = nextd
            closestPoint = (point[0], point[1])
    return mindist < tolerance, closestPoint

def tkColorfromRgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code"""
    r, g, b = round( rgb[0]*255 ),round( rgb[1]*255 ),round( rgb[2]*255 )
    return f'#{r:02x}{g:02x}{b:02x}'


# Create the loop drawing with expected PD code
badpdcount = 0
while True:    
    LE, pd, comps = getLEwithPD( link )
    #pd = eval( check_output(['python3', 'plinkpd2.py', str(link) ]) )
    #pd = plinkPD( link )
    #print( drawnpd )
    #print( pd )
    if drawnpd is None or pd == drawnpd:
        break
    badpdcount += 1
    LE.done()
    #LE = None
    #print("hi")

#print( "original:", link )
#print( "drawn:", drawnpd )
#print( "components:", components )

if badpdcount > 0:
    print( "For pd=", link)
    print( "and drawnpd=", drawnpd )
    print( "We had to regenerate", badpdcount, "times to get the expected PD code." )

# tweak parameters
LE.style_var.set('pl')
LE.set_style()
c = LE.canvas
corners = {}
crosses = {}
LE.info_var.set(1)
LE.update_info()
if len( sys.argv ) <= 2 or debug:   
    LE.show_DT()

#print( "minPinSetDict", minPinSetDict )

# create coordinate dictionary of strands from the component list
compCoordDict = {}
for i in range( len( components ) ):
    for j in range( len( components[i] ) ):
        if components[i][j] not in compCoordDict:
            compCoordDict[components[i][j]] = (i,j)
        else:
            print( "Bad component list" )
            assert( False )

#print( components )
#print( compCoordDict )        

# store coordinates of all crossings as well as their outgoing labels
for crs in LE.Crossings:
    crs.locate()
    if crs.flipped:
        first,second = abs( crs.hit2 ), abs( crs.hit1 )
    else:
        first,second = abs( crs.hit1 ), abs( crs.hit2 )
   
    firstx = compCoordDict[first][0]
    numStrands1 = len( components[ firstx ] )
    firsty = compCoordDict[first][1]
    next1 = components[firstx][(firsty-1)%numStrands1]

    
    secondx = compCoordDict[second][0]
    numStrands2 = len( components[ secondx ] )
    secondy = compCoordDict[second][1]
    next2 = components[secondx][(secondy-1)%numStrands2]    

    regs = set()
    adjStrands = {first,second,next1,next2}

    if len( sys.argv ) > 2 and regLabels is not None: 
        for strand in adjStrands:
            regs.add( adjDict[strand][0] )
            regs.add( adjDict[strand][1] )

    crosses[(crs.x,crs.y)]={"segs":None, "regs":regs,"outdirs":None,\
                                    "outdict":{"a":{"label":first,"seg":None,"dir":None},\
                                               "b":{"label":second,"seg":None,"dir":None}}}


# store coordinates of all corners and the segments that crosses and corners belong to
#dirDict = {0:"right",1:"up",2:"left",3:"down" }
for a in LE.Arrows:
    # expose arrows and add in missing segments
    a.expose()
    segs = a.find_segments( LE.Crossings, include_overcrossings=True )
    toAdd = []
    for i in range( len( segs )-1 ):
        if (segs[i][2],segs[i][3]) != (segs[i+1][0],segs[i+1][1]):
            midx = (segs[i][2]+segs[i+1][0])/2
            midy = (segs[i][3]+segs[i+1][1])/2
            toAdd.append( [segs[i][2],segs[i][3],midx,midy] )
            toAdd.append( [midx,midy,segs[i+1][0],segs[i+1][1]] )
    segs += toAdd
    if regLabels is None:
        continue

    # create a linked list out of segments
    # and correctly associate outgoing labels to segments
    # emanating from crossings
    for seg in segs:
        closeData = closeTo(seg[0],seg[1],crosses)
        if not closeData[0]:
            if (seg[0],seg[1]) not in corners:
                corners[(seg[0],seg[1])] = {"nextseg":seg,"strand":None,"regs":None}#,1:None,}
            else:
                assert( False )
                corners[(seg[0],seg[1])][1]=seg
        else:
            #c.create_text(nextx,nexty,text=label, fill="blue", font=('Helvetica 15 bold')) 
            if crosses[closeData[1]]["segs"] is None:
                crosses[closeData[1]]["segs"] = [seg]
                jumps = {seg[2]-seg[0]:0,seg[0]-seg[2]:2,seg[3]-seg[1]:3,seg[1]-seg[3]:1}
                direction = jumps[max(jumps)]
                crosses[closeData[1]]["outdirs"] = [direction]
                
            else:
                crosses[closeData[1]]["segs"].append( seg )
                jumps = {seg[2]-seg[0]:0,seg[0]-seg[2]:2,seg[3]-seg[1]:3,seg[1]-seg[3]:1}
                direction = jumps[max(jumps)]
                crosses[closeData[1]]["outdirs"].append( direction )

                if (crosses[closeData[1]]["outdirs"][0]+1)%4==crosses[closeData[1]]["outdirs"][1]:
                    crosses[closeData[1]]["outdict"]["a"]["seg"]=crosses[closeData[1]]["segs"][0]
                    crosses[closeData[1]]["outdict"]["b"]["seg"]=crosses[closeData[1]]["segs"][1]
                    crosses[closeData[1]]["outdict"]["a"]["dir"]=crosses[closeData[1]]["outdirs"][0]
                    crosses[closeData[1]]["outdict"]["b"]["dir"]=crosses[closeData[1]]["outdirs"][1]
                else:
                    assert( (crosses[closeData[1]]["outdirs"][0]-1)%4==crosses[closeData[1]]["outdirs"][1] )
                    crosses[closeData[1]]["outdict"]["a"]["seg"]=crosses[closeData[1]]["segs"][1]
                    crosses[closeData[1]]["outdict"]["b"]["seg"]=crosses[closeData[1]]["segs"][0]
                    crosses[closeData[1]]["outdict"]["a"]["dir"]=crosses[closeData[1]]["outdirs"][1]
                    crosses[closeData[1]]["outdict"]["b"]["dir"]=crosses[closeData[1]]["outdirs"][0]
                    

if regLabels is None:
    LE.save_as_svg(filename)
    LE.done()
    cleanFile()
    raise( "All done" )


#for key in crosses:
#    print( crosses[key] )
#    print()

# build a polygon for each region by computing consecutive coordinates

coordPlacementDict = {}
# keys are strands, values are (reg,index) tuples
# which specify where that strand appears in the regWords dictionary

regToSegCoords = {}
# keys are regions, values are lists of coordinates along edges bounding that region

for reg in regWords:
    regToSegCoords[reg] = []
    for i in range( len( regWords[reg] ) ):
        #sign = regWords[reg][i] > 0
        strand = abs(regWords[reg][i])
        if strand not in coordPlacementDict:
            coordPlacementDict[(strand,reg)]={"val":regWords[reg][i],"index":i}
        regToSegCoords[reg].append( None )

#print( regWords )

# associate appropriate region labels to each corner

# Compute the size of the pl grid
nonzeroDistances = set()
for i in range( len( LE.Crossings )-1 ):
    for j in range( i+1, len( LE.Crossings ) ):
        crs1 = LE.Crossings[i]
        crs2 = LE.Crossings[j]
        nonzeroDistances.add( abs( crs1.x - crs2.x )+abs( crs1.y - crs2.y ) )
gridLength = min( nonzeroDistances )
labelFontSize = max( int( gridLength/5 ), 1 )
offset = gridLength/6
# Define parameters for plotted data in regions based on grid size

if bufferFrac is not None:
    leftbuffer = gridLength*bufferFrac #1/10
else:
    leftbuffer = gridLength*1/15
topbuffer = leftbuffer

if diamFrac is not None:
    diam = gridLength*diamFrac #1/4 
else:
    diam = gridLength*1/7 #1/7 or 1/8
circleWidth = 0
dotFontSize = max( int( diam*0.9 ), 1 )
spacing = (diam+circleWidth)*1.1
labelsPerLine = 5
#diam = 8
#leftbuffer = 10

# create dictionary for the next label based on the current label (for annotate=True)
nextOf = {}
for i in range( len( components ) ):
    compsize = len( components[i] )
    for j in range( len( components[i] ) ):
        nextOf[components[i][j]]=components[i][(j+1)%compsize]

for cross in crosses:
    for choice in ["a","b"]:
        # label each outgoing segment
        curSeg = crosses[cross]["outdict"][choice]["seg"]
        label = crosses[cross]["outdict"][choice]["label"]
        coordList = [(curSeg[0],curSeg[1])]
        #if len( sys.argv ) > 2: 
        #    for reg in adjDict[label]:
        #        if reg not in regToSegCoords:            
        #        regToSegCoords[reg] = []
        (nextx,nexty) = (curSeg[2],curSeg[3])
        closeData = closeTo(nextx,nexty,crosses)
        # follow until the next crossing
        while not closeData[0]:
            corners[(nextx,nexty)]['strand'] = label
            
            if len( sys.argv ) > 2: 
                corners[(nextx,nexty)]['regs'] = set( adjDict[label] )
                #for reg in adjDict[label]:
                #    regToSegCoords[reg].append((nextx,nexty))
                coordList.append((nextx,nexty))
            #if len( sys.argv ) <= 2 or debug:
            #    c.create_text(nextx,nexty,text=label, fill="blue", font=('Helvetica 15 bold')) 
            curSeg = corners[(nextx,nexty)]["nextseg"]
            (curx,cury) = (nextx,nexty)
            (nextx,nexty) = (curSeg[2],curSeg[3])
            closeData = closeTo(nextx,nexty,crosses)

        if annotated:
            seg = curSeg
            jumps = {seg[2]-seg[0]:0,seg[0]-seg[2]:2,seg[3]-seg[1]:3,seg[1]-seg[3]:1}
            #offset = 10#max(jumps)
            direction = jumps[max(jumps)]
            #dirDict = {0:"right",1:"up",2:"left",3:"down" }
            #if label + 1 == len(drawnpd)*2+1:
            #    nextLabel = 1
            #else:
            #    nextLabel = label + 1
            nextLabel = nextOf[ label ]
            prevLabel = label            
            if direction == 0: #moving right
                textNext = c.create_text(nextx+offset,nexty,text=-nextLabel, fill="black", font=('Helvetica {} bold'.format(dotFontSize)), anchor = "sw")
                textPrev = c.create_text(nextx-offset,nexty,text=prevLabel, fill="black", font=('Helvetica {} bold'.format(dotFontSize)), anchor = "ne")
            if direction == 2: #moving left
                textNext = c.create_text(nextx-offset,nexty,text=-nextLabel, fill="black", font=('Helvetica {} bold'.format(dotFontSize)), anchor = "ne")
                textPrev = c.create_text(nextx+offset,nexty,text=prevLabel, fill="black", font=('Helvetica {} bold'.format(dotFontSize)), anchor = "sw")
            if direction == 1: #moving up
                textNext = c.create_text(nextx,nexty-offset,text=-nextLabel, fill="black", font=('Helvetica {} bold'.format(dotFontSize)), anchor = "se")
                textPrev = c.create_text(nextx,nexty+offset,text=prevLabel, fill="black", font=('Helvetica {} bold'.format(dotFontSize)), anchor = "nw")
            if direction == 3: #moving down
                textNext = c.create_text(nextx,nexty+offset,text=-nextLabel, fill="black", font=('Helvetica {} bold'.format(dotFontSize)), anchor = "nw")
                textPrev = c.create_text(nextx,nexty-offset,text=prevLabel, fill="black", font=('Helvetica {} bold'.format(dotFontSize)), anchor = "se")
            upshift = diam/7
            x1, y1, x2, y2 = c.bbox(textNext)
            width = 0
            outline = "black" #loop red = tkColorfromRgb((216,38,38))
            r=c.create_rectangle(x1, y1-upshift, x2, y2-upshift , fill="white", outline = outline , width = width ) 
            c.tag_lower(r,textNext)
            x1, y1, x2, y2 = c.bbox(textPrev)
            r=c.create_rectangle(x1, y1-upshift, x2, y2-upshift, fill="white", outline = outline, width = width )
            c.tag_lower(r,textPrev)

        coordList.append(closeData[1])
        # put the crossing/corner coordinates into the appropriate place in each region polygon
        if len( sys.argv ) > 2:
            coordListRev = coordList.copy()
            coordListRev.reverse()
            for reg in adjDict[label]:
                val = coordPlacementDict[(label,reg)]["val"]
                ind = coordPlacementDict[(label,reg)]["index"]
                if val > 0:
                    regToSegCoords[reg][ind] = coordList[:-1]
                else:
                    regToSegCoords[reg][ind] = coordListRev[:-1]
                #if reg not in regToSegCoords:
                #    regToSegCoords[reg] = [coordList.copy()]
                #else:
                #    regToSegCoords[reg].append( coordList.copy() )
                #


                
        
if len( sys.argv ) <= 2:   
    input("Press any key to close the window")
    LE.done()
    #cleanFile()
    assert( False )


#print( regToSegCoords )
# create the actual polygons from the lists assembled above
regPolys = {}
for reg in regToSegCoords:
    regPolys[reg] = []
    for coordList in regToSegCoords[reg]:
        for coords in coordList:
            regPolys[reg].append( coords )

#print( regPolys )

regPolysSage = {}
regPolyType = {}

for reg in regPolys:
    #print( regLabels[reg], type( regLabels[reg] ) )
    #if regLabels[reg]== 4:
    #    c.create_polygon(regPolys[reg], outline = "purple", fill = "", width = 2)
    #if regLabels[reg]== 7:
    #    c.create_polygon(regPolys[reg], outline = "green", fill = "", width = 3)
    #if regLabels[reg]== 11:
    #    c.create_polygon(regPolys[reg], outline = "orange", fill = "", width = 4)
    #if regLabels[reg]== 12:
    #    c.create_polygon(regPolys[reg], outline = "black", fill = "", width = 5)
    regPolysSage[reg] = Polyhedron(vertices = regPolys[reg], backend='ppl', base_ring=QQ )
    #try:
    #    regPolysSage[reg] = Polyhedron(vertices = regPolys[reg], backend='ppl', base_ring=QQ )#base_ring=RDF)
    #    regPolyType[reg]=float
    #except ValueError as e:
    #    traceback.print_exc()
    #    regPolysSage[reg] = Polyhedron(vertices = regPolys[reg], backend='ppl', base_ring=QQ )
    #    warningCaption = "Floating point error likely. Take this figure with a grain of salt."
    #    p = regPolysSage[reg].center()
    #    repPoint = (float( p[0] ), float( p[1] ) )
    #    #c.create_polygon(regPolys[reg], outline = "orange", fill = "", width = 4) #cleanFile() deletes this
    #    c.create_text( repPoint[0],repPoint[1],text=warningCaption,\
    #                  fill="orange", anchor="nw", font = ("Helvetica", 6, "bold" ))
    #    regPolyType[reg]=Rational
    #    #raise( e )

# https://groups.google.com/g/sage-support/c/lsUODuV47kc
# Polyhedron constructor has an issue with the multiloop below - that is why the kwargs are added
# [[5, 8, 6, 1], [4, 20, 5, 9], [7, 19, 8, 20], [6, 19, 7, 18],[1, 16, 2, 15],\
# [9, 3, 10, 4], [17, 12, 18, 13], [16, 12, 17, 11], [2, 14, 3, 15], [10, 14, 11, 13]]

infRegion = reg
#print( "New infinite region:", regLabels[reg] )

#print( regPolysSage )

# find infinite region using polygon containment
for reg in regPolysSage:
    #p = regPolysSage[reg].representative_point()
    #repPoint = (float( p[0] ), float( p[1] ) )
    #print( repPoint )
    #print( type( repPoint ) )
    #print( type( repPoint[0] ) )
    #print( type( float( repPoint[0] ) ) )
    #c.create_oval( repPoint[0]-1, repPoint[1]-1,repPoint[0]+1,repPoint[1]+1,
    #                       outline ="red", fill = "red", width = 10 )
    #c.create_text( repPoint[0],repPoint[1],text=regLabels[reg],\
    #                  fill="green", anchor="nw", font = ("Helvetica", 12, "bold" ))   
    bigger = True
    for vert in regPolysSage[infRegion].vertices():
        if not regPolysSage[reg].contains( vert ): #vert not in regPolysSage[reg]:
            #if regLabels[reg]== 12:
                #print( "hi" )
                #c.create_oval( vert[0]-1, vert[1]-1,vert[0]+1,vert[1]+1,\
                #           outline ="green", fill = "green", width = 10 )
            bigger = False
            #break
    if bigger:
        infRegion = reg
        #print( "New infinite region:", regLabels[reg] )

#print( "here" )

#c.create_polygon(regPolys[infRegion], outline = "blue", fill = "orange", width = 2)


# make sure every corner is labeled
#for (x,y) in corners:
#    print( corners[(x,y)] )
#    print()
    #assert( corners[(x,y)][1] is not None )


#c.create_rectangle( crs.x, crs.y,crs.x+gridLength,crs.y+gridLength,\
#                       outline = "orange", width = 10 )



    
# associate boundary coordinates to regions
regBoundaries = {}

for dct in [corners,crosses]:
    for coord in dct:
        for reg in dct[coord]['regs']:
            if reg not in regBoundaries:
                regBoundaries[reg] = {"coords":[coord],"topLeft":None, "bottomLeft":None,"infRegion":False}
            else:
                regBoundaries[reg]["coords"].append( coord )


# compute anchor points for labels and label regions
# plot the appropriate pinning sets in each region

for reg in regBoundaries:

    #print( reg, regLabels[ reg ] )
    
    #dReg1 = 42
    #dReg2 = 84
    topLeft = regBoundaries[reg]["coords"][0]
    bottomLeft = regBoundaries[reg]["coords"][0]

    # find the top left and bottom left of each region
    for point in regBoundaries[reg]["coords"]:

        #if reg == dReg1 or reg == dReg2:
        #    c.create_text(point[0],point[1],text=str(reg)[0], fill="black", font=('Helvetica 15 bold'))
        if point[0] < topLeft[0] - tolerance or ( abs( point[0]-topLeft[0] ) < tolerance and point[1] < topLeft[1] ):
            
            topLeft = point

        if point[0] < bottomLeft[0] - tolerance or ( abs( point[0]-bottomLeft[0] ) < tolerance and point[1] > bottomLeft[1] ):
            
            bottomLeft = point
    regBoundaries[reg]["topLeft"] = [topLeft]
    regBoundaries[reg]["bottomLeft"] = [bottomLeft]        


    regBoundaries[infRegion]["infRegion"]=True
    # label the infinite region based on the bottom left, all else anchored from top left
    if not regBoundaries[reg]["infRegion"]:
        anchor1 = topLeft
    else:
        anchor1 = bottomLeft

    #font.families()[0], 36, "bold") )#, font="Arial 10 bold")

    
    if regLabels[reg] == "":
        dotTopBuffer = topbuffer
    else:
        dotTopBuffer = labelFontSize+2*topbuffer
        c.create_text(anchor1[0]+leftbuffer,anchor1[1]+topbuffer,text=regLabels[reg],\
                      fill="black", anchor="nw", font = ("Helvetica", labelFontSize, "bold" ))    

    if minPinSets is not None:
        # compute matrix of colored dots for this region corresponding to the pinning sets it belongs to
        dotDict = {}
        for key in minPinSets:
            pinSet = frozenset(key)
            if reg in key:
                dotDict[ minPinSetDict[pinSet]["label"] ] =\
                         {"color":tkColorfromRgb( minPinSetDict[pinSet]["color"] ),\
                          "letter":minPinSetDict[pinSet]["letterLabel"] } 

        i = 0
        j = 0
        k = 0
        
        #j = 0
       
        
            
        
        sortedkeys = list( dotDict.keys() )
        sortedkeys.sort()
        for key in sortedkeys:
            c.create_oval( anchor1[0]+leftbuffer + i*spacing, anchor1[1]+dotTopBuffer+k*spacing,\
                           anchor1[0]+leftbuffer + i*spacing+diam, anchor1[1]+dotTopBuffer+k*spacing+diam,\
                           outline = dotDict[key]["color"], fill = dotDict[key]["color"], width = circleWidth )
            centerx = anchor1[0]+leftbuffer + i*spacing+diam/2
            centery = anchor1[1]+dotTopBuffer+k*spacing+diam/1.7 #looks a little better to push down past half
            c.create_text(centerx,centery,text=dotDict[key]["letter"], fill="white",\
                          anchor="center", font = ("Helvetica", dotFontSize ) ) #font=('Arial',30, "bold italic" ), "•"
            i+=1
            j += 1
            if j == labelsPerLine:
                i = 0
                j = 0
                k += 1    

# save file
LE.save_as_svg(filename)
LE.done()
cleanFile()


