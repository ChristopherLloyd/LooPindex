import snappy
import sys
from tkinter import font

# get args from command line
link = sys.argv[1]
if '[' in link:
    link = eval( link )
drawnpd = eval( sys.argv[2] )
adjDict = eval( sys.argv[3] )
minPinSets = eval( sys.argv[4] )
tolerance = eval( sys.argv[5] )
minPinSetDict = eval( sys.argv[6] )
regLabels = eval( sys.argv[7] )
filename = sys.argv[8]

# necessary for floating point nonsense
def closeTo( x0, y0, pointDict ):
    #nonlocal tolerance
    for key in pointDict:
        point1 = key
        break
    point1
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


# Create the loop drawing and tweak parameters
LE = snappy.Link( link ).view()
LE.style_var.set('pl')
LE.set_style()
c = LE.canvas
corners = {}
crosses = {}
LE.info_var.set(1)
LE.update_info()
#LE.show_DT()

#print( "minPinSetDict", minPinSetDict )

# store coordinates of all crossings
for crs in LE.Crossings:
    crs.locate()
    strandCount = len( LE.Crossings )*2
    hit1 = abs( crs.hit1 )
    hit2 = abs( crs.hit2 )

    if hit1 == 1 or hit2 == 1:
        startCross = (crs.x,crs.y)
    next1 = (hit1-1)%strandCount
    if next1 == 0:
        next1 = strandCount
    next2 = (hit2-1)%strandCount
    if next2 == 0:
        next2 = strandCount

    regs = set()
    adjStrands = {hit1,hit2,next1,next2}
    
    for strand in adjStrands:
        regs.add( adjDict[strand][0] )
        regs.add( adjDict[strand][1] )

    for elt in drawnpd:
        if set( elt ) == {hit1,hit2,next1,next2}:
            crosses[(crs.x,crs.y)]={"strands":elt, "testStrands":None, "segs":None, "regs":regs, "dirs":None }
            break
    #crossCoordDict[ abs( crs.hit1 ) ] = (crs.x, crs.y)
    #crossCoordDict[ abs( crs.hit2 ) ] = (crs.x, crs.y)

# store coordinates of all corners and the segments that crosses and corners belong to
for a in LE.Arrows:
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
        
    for seg in segs:
        closeData = closeTo(seg[0],seg[1],crosses)
        if not closeData[0]:
            if (seg[0],seg[1]) not in corners:
                corners[(seg[0],seg[1])] = {0:seg,1:None,"strand":None,"regs":None}
            else:
                corners[(seg[0],seg[1])][1]=seg
        else:
            if crosses[closeData[1]]["segs"] is None:
                crosses[closeData[1]]["segs"] = [seg]
            else:
                crosses[closeData[1]]["segs"].append( seg )
        closeData = closeTo(seg[2],seg[3],crosses)
        if not closeData[0]:
            if (seg[2],seg[3]) not in corners:
                corners[(seg[2],seg[3])] = {0:seg,1:None,"strand":None,"regs":None}
            else:
                corners[(seg[2],seg[3])][1]=seg
        else:
            if crosses[closeData[1]]["segs"] is None:
                crosses[closeData[1]]["segs"] = [seg]
            else:
                crosses[closeData[1]]["segs"].append( seg )

#curLabel = 1
#i = 0

(curx, cury) = startCross
#j = 0
#dirDict = {0:"right",1:"up",2:"left",3:"down" }
for segOut in crosses[(curx,cury)]['segs']:
    # for each possible direction from the first crossing, we proceed with labeling along the
    # link until we finish, or encounter a PD code discrepancy, in which case we start over
    curSeg = segOut
    
    if closeTo( segOut[0],segOut[1],{(curx,cury)})[0]:
        (nextx,nexty) = (segOut[2],segOut[3])
    else:
        (nextx,nexty) = (segOut[0],segOut[1])
    #if (nextx,nexty) not in corners or corners[(nextx,nexty)]['strand'] is not None:
    #    continue
    #print( "AT START (curx,cury):", (curx,cury), "(nextx,nexty)", (nextx,nexty) )
    curLabel = 1
    happy = False
    ids = []
    while curLabel <= strandCount:
        i+=1
        closeData = closeTo(nextx,nexty,crosses)
        if closeData[0]: # you are at a crossing
            #(closenextx,closenexty)=(nextx,nexty)
            (nextx,nexty)=closeData[1]
            #ids.append( c.create_text(nextx,nexty,text=curLabel, fill="blue", font=('Helvetica 15 bold')) )
            
            # figure out the direction of the current segment,
            # then choose the next segment at this crossing which goes in the same direction
            curJump = {nextx-curx:0,curx-nextx:2,nexty-cury:3,cury-nexty:1}
            direction = curJump[max(curJump)]

            # add the label at this crossing in the appropriate direction

            if crosses[(nextx,nexty)]["dirs"] is None: # first encounter
                crosses[(nextx,nexty)]["dirs"] = {curLabel:direction}
            else: # second encounter, check for PD code discrepancy, if none, then continue
                crosses[(nextx,nexty)]["dirs"][curLabel] = direction
                assert( len( crosses[(nextx,nexty)]["dirs"] ) == 2 )
                #print( "too many labels in", crosses[(nextx,nexty)]["dirs"] )
                label0, label1 = tuple( crosses[(nextx,nexty)]["dirs"].keys() )
                label0plus = (label0+1)%strandCount
                if label0plus == 0:
                    label0plus = strandCount
                label1plus = (label1+1)%strandCount
                if label1plus == 0:
                    label1plus = strandCount                
                if crosses[(nextx,nexty)]["dirs"][label0] == (crosses[(nextx,nexty)]["dirs"][label1]-1)%4:
                    crosses[(nextx,nexty)]["testStrands"] = (label0,label1,label0plus,label1plus)
                else:
                    crosses[(nextx,nexty)]["testStrands"] = (label0,label1plus,label0plus,label1)
                possibleLabels = []
                for i in range( 4 ):
                    possibleLabels.append( crosses[(nextx,nexty)]["testStrands"][i:]+crosses[(nextx,nexty)]["testStrands"][:i] )
                if not crosses[(nextx,nexty)]["strands"] in possibleLabels:
                    # this labeling doesn't match the PD code; reset and try again
                    break
                
                #print( crosses[(nextx,nexty)]["dirs"] )
                
            #print( direction )
            #print( crosses[(nextx,nexty)]['segs'] )
                
            # determine which direction you were going and continue in that direction
            # after increasing the label
            for seg in crosses[(nextx,nexty)]['segs']:
                #curSeg = segOut
                if closeTo( seg[0],seg[1],{(nextx,nexty)})[0]:
                    #if (seg[0],seg[1])==(nextx,nexty) or (seg[0],seg[1]) == (closenextx,closenexty):
                    (nextnextx,nextnexty) = (seg[2],seg[3])
                else:
                    (nextnextx,nextnexty) = (seg[0],seg[1])
                nextJump = {nextnextx-nextx:0,nextx-nextnextx:2,nextnexty-nexty:3,nexty-nextnexty:1}
                nextDir = nextJump[max(nextJump)]
                #print( " first point:", (seg[0],seg[1]) )
                #print( " second point:", (seg[2],seg[3]) )
                #print( " curDir:", dirDict[ nextDir ] )
                if nextDir == direction:
                    break
            (curx,cury) = (nextx,nexty)
            (nextx,nexty) = (nextnextx,nextnexty)
            curSeg = seg
            curLabel += 1
            #print( "current label:", curLabel, "current direction:", dirDict[direction] )
            #print( "(curx,cury):", (curx,cury), "(nextx,nexty)", (nextx,nexty) )
            (nextx,nexty)
        else: # you are at a corner, add the appropriate label and continue
            
            #ids.append( c.create_text(nextx,nexty,text=curLabel, fill="black", font=('Helvetica 15 bold')) )
            corners[(nextx,nexty)]['strand'] = curLabel
            corners[(nextx,nexty)]['regs'] = set( adjDict[curLabel] )
            seg1 = corners[(nextx,nexty)][0]
            seg2 = corners[(nextx,nexty)][1]
            inFirst = False
            if (curx,cury) == (seg1[0],seg1[1]) or (curx,cury) == (seg1[2],seg1[3]):
                inFirst = True
            if inFirst:
                curSeg = corners[(nextx,nexty)][1]
            else:
                curSeg = corners[(nextx,nexty)][0]
            (curx,cury) = (nextx,nexty)
            if (curSeg[0],curSeg[1]) == (nextx,nexty):
                (nextx,nexty) = (curSeg[2],curSeg[3])
            else:
                (nextx,nexty) = (curSeg[0],curSeg[1])
            #break
        if curLabel == strandCount + 1:
            happy = True
    if happy: # you're back where you started and the labels are consistent with the PD code
        #print( "HAPPY" )
        #for cross in crosses:
        #    pass
        #for corner in corners:
        #    print( corners[corner]['strand'] )
        # c.create_text(corner[0],corner[1],text=corners[corner]['strand'], fill="blue", font=('Helvetica 15 bold'))
        break
    else: #start over in a new direction
        # reset all labels
        for cross in crosses:
            crosses[cross]["testStrands"] = None
            crosses[cross]["dirs"] = None
        for corner in corners:
            corners[corner]['strand'] = None
            corners[corner]['regs']
        #if j != 3:
            #for iD in ids:
                #c.delete(iD)
        (curx, cury) = startCross
    #j+=1
    
# make sure every corner is labeled
for (x,y) in corners:        
    assert( corners[(x,y)][1] is not None )


# associate boundary coordinates to regions
regBoundaries = {}
for key in corners:
    randomCorner = key
    break
#randomCorner = getKey(corners)
minX = randomCorner[0]
maxX = randomCorner[0]
minY = randomCorner[1]
maxY = randomCorner[1]
for dct in [corners,crosses]:
    for coord in dct:
        for reg in dct[coord]['regs']:
            if reg not in regBoundaries:
                regBoundaries[reg] = {"coords":[coord],"topLeft":None, "bottomLeft":None,"infRegion":False}
            else:
                regBoundaries[reg]["coords"].append( coord )
        if coord[0] < minX:
            minX = coord[0]
        if coord[0] > maxX:
            maxX = coord[0]
        if coord[1] < minY:
            minY = coord[1]
        if coord[1] > maxY:
            maxY = coord[1]

# compute anchor points for labels and label regions

for reg in regBoundaries:
    #dReg1 = 42
    #dReg2 = 84
    topLeft = regBoundaries[reg]["coords"][0]
    bottomLeft = regBoundaries[reg]["coords"][0]
    regMinX = topLeft[0]
    regMaxX = topLeft[0]
    regMinY = topLeft[1]
    regMaxY = topLeft[1]
    for point in regBoundaries[reg]["coords"]:
        if point[0] < regMinX:
            regMinX = point[0]
        if point[0] > regMaxX:
            regMaxX = point[0]
        if point[1] < regMinY:
            regMinY = point[1]
        if point[1] > regMaxY:
            regMaxY = point[1]
        #if reg == dReg1 or reg == dReg2:
        #    c.create_text(point[0],point[1],text=str(reg)[0], fill="black", font=('Helvetica 15 bold'))
        if point[0] < topLeft[0] - tolerance or ( abs( point[0]-topLeft[0] ) < tolerance and point[1] < topLeft[1] ):
            
            topLeft = point

        if point[0] < bottomLeft[0] - tolerance or ( abs( point[0]-bottomLeft[0] ) < tolerance and point[1] > bottomLeft[1] ):
            
            bottomLeft = point
    regBoundaries[reg]["topLeft"] = [topLeft]
    regBoundaries[reg]["bottomLeft"] = [bottomLeft]        

    if abs( minX-regMinX ) < tolerance and abs( minY-regMinY ) < tolerance \
       and abs( maxX-regMaxX ) < tolerance and abs( maxY-regMaxY )<tolerance:
        regBoundaries[reg]["infRegion"] = True


    # compute matrix of colored dots for this region corresponding to the pinning sets it belongs to
    dotDict = {}
    for key in minPinSetDict:
        pinSet = key
        if reg in key:
            dotDict[ minPinSetDict[key]["label"] ] = tkColorfromRgb( minPinSetDict[key]["color"] )   

    i = 0
    j = 0
    k = 0
    spacing = 14
    labelsPerLine = 4
    diam = 8
    leftbuffer = 10
    downbuffer = 30
    #j = 0
    
    if not regBoundaries[reg]["infRegion"]:
        anchor1 = topLeft
    else:
        anchor1 = bottomLeft
        
    c.create_text(anchor1[0]+leftbuffer,anchor1[1]+leftbuffer*5/3,text=regLabels[reg], fill="black", anchor="w", font = ("Helvetica", 12, "bold" ))
    #font.families()[0], 36, "bold") )#, font="Arial 10 bold")

    sortedkeys = list( dotDict.keys() )
    sortedkeys.sort()
    for key in sortedkeys:
        # can label circles with key after you figure out how to change font size
        c.create_oval( anchor1[0]+leftbuffer + i*spacing, anchor1[1]+downbuffer+k*spacing,\
                       anchor1[0]+leftbuffer + i*spacing+diam, anchor1[1]+downbuffer+k*spacing+diam,\
                       outline = dotDict[key], fill = dotDict[key], width = 4 )
        #c.create_text(topLeft[0]+10 + i*spacing,topLeft[1]+40+k*spacing,text="•", fill=dotDict[key], anchor="w" ) #font=('Arial',30, "bold italic" ), 
        i+=1
        j += 1
        if j == labelsPerLine:
            i = 0
            j = 0
            k += 1
    #else:
    #    c.create_text(bottomLeft[0]+10,bottomLeft[1]+20,text=reg, fill="black", anchor="w") #font=('Terminal 10 bold')
        
    #    for key in dotDict:
            #c.create_text(bottomLeft[0]+10 + i*spacing,bottomLeft[1]+40,text="•", fill=dotDict[key], anchor="w") # font=('Terminal','30','bold')
    #        c.create_oval( bottomLeft[0]+leftbuffer + i*spacing, bottomLeft[1]+downbuffer+k*spacing,\
    #                       bottomLeft[0]+leftbuffer + i*spacing+diam, bottomLeft[1]+downbuffer+k*spacing+diam,\
    #                       outline = dotDict[key], fill = dotDict[key], width = 2 )
    #        i+=1
    #c.pack()
    

# save file
LE.save_as_svg(filename)
LE.done()
