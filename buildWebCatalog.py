from planeloop import *
import mysql.connector
import os
import re
# https://dev.mysql.com/doc/mysql-getting-started/en/#mysql-getting-started-basic-ops

db = mysql.connector.connect( username=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PASS') )
cursor = db.cursor()

try:
    cursor.execute("USE multiloops")
except NameError as msg:
    traceback.print_exc()
    #raise Exception( msg ) # database not found
    
def main():
    #writeMainIndexPagesForWeb(  )

    #makeWebPagesMany( namesSatisfyingQuery( "numRegions < 13") )

    #return

    #createDatabase()
    #return

    # 12^3_74 has too many minimal pinning sets
    # 12^3_75 is borderline

    #tenOne = namesSatisfyingQuery( "numRegions = 10 and components = 1")

    #print( tenOne )

    # make monorbigonlesspage 

    computePinSetsAndBuildPagesForWeb( n=12 )

    #makeWebPagesMany( "10^1_18", "")    

    return

 
    # things to record (now or later): max number of minimal pinning sets to which a region belongs? is it an interesting counterexample?

def makeMonorbigonless():
    query = namesSatisfyingQuery( "minRegionDegree > 2 and numRegions < 13")
    writeIndexPage( query, "all multisimple", "Multisimple multiloops with 12 or fewer regions", "asdjfk.html",\
                    desc = "{} multiloops total.".format( len( query )) ) 
    
def makeMultiSimple():
    # make multisimple page
    query = namesSatisfyingQuery( "isMultiSimple = 1 and numRegions < 13")
    writeIndexPage( query, "all multisimple", "Multisimple multiloops with 12 or fewer regions", "multisimple.html",\
                    desc = "{} multiloops total.".format( len( query )) ) 

def writeMainIndexPagesForWeb():
    titles = ["4^2","5^1","6^1","6^2","7^1","7^2","8^1","8^2","8^3","9^1","9^2","9^3","10^1","10^2","10^3","10^4","11^1","11^2","11^3","11^4","12^1","12^2","12^3","12^4","12^5"]

    for regs in [4,5,6,7,8,9,10,11,12]:
        for comps in [1,2,3,4,5]:
            query = namesSatisfyingQuery( "numRegions = {} and components = {}".format( regs, comps ) )
            if query != []:
                
                if comps == 1:
                    M = "Loops"
                    m = "loops"
                    c = "component"
                else:
                    M = "Multiloops"
                    m = "multiloops"
                    c = "components"
                if len( query ) == 1:
                    m = m[:-1]
                pageName = "{}^{}".format(regs,comps)
                print( "Building index page", pageName, "with", len(query), "entries.")
                try: 
                    prev = titles[titles.index( pageName )-1]
                except IndexError:
                    pass
                try: 
                    next = titles[titles.index( pageName )+1]
                except IndexError:
                    pass               

                writeIndexPage( query, pageName, "{} with {} regions and {} {}".format(M,regs,comps,c),\
                                filename = "{}.html".format( pageName ), desc = "{} {} total.".format(len(query),m),\
                                     next=next, prev=prev )


def computePinSetsAndBuildPagesForWeb( n = 12, recomputePinData = False ): # has been done for n=12
    # minpinsets field not large enough for forweb[958] (12^2_301) at 1024, now it is doubled to 2048
    forweb = namesSatisfyingQuery( "numRegions < {}".format( n + 1 ) )
    if recomputePinData:
        storeDataForWebMany( forweb )
    makeWebPagesMany( forweb )

def writeIndexPage( names, pagetitle, title, filename, desc=None, next = None, prev = None ):
    """Generates a page with thumbnails for all the loops in names with the given title and description.
    names may be a list or dictionary whose values are lists. if it is a list then no subheaders are written,
    if it is a dictionary, the keys are the subheaders."""

    f = open( "docs/"+filename, 'w')
    f.write( generatePageString( names, pagetitle, title, desc, next, prev) )
    f.close()

def generatePageString( names, pagetitle, title, desc, next, prev  ):
    thumbnailStr = """
    <div class="float">
        <a href="multiloops/{name}.html" id="{name}" title="{name}"><img alt="{name}" src="multiloops/{name}/clean.svg" decoding="async"/>
        <span>{texname}</span></a>
    </div>
    """

    sublistSeparator = "\t\t\t<br>\n\t\t\t<hr>\n"

    subListHeader = """
    <h2><span id="{subtitle}">{subtitle}</span></h2>
    """

    listWrapper = """
    <div class="images">

    {thumbnaillist}

    </div>
    """
    
    header = """<!DOCTYPE html><html>
    <head><meta
    charset="utf-8"><meta
    name="viewport"
    content="width=device-width, initial-scale=1, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no">
    <title>LooPindex - {pagetitle}</title>
    <link rel="shortcut icon" href="webicon.svg"/>
    <link rel="stylesheet" type="text/css" href="style.css">	
    <script>
    MathJax = {{
        tex: {{
            inlineMath: [['$', '$'],['\\(', '\\)']]
        }}
    }};
    </script>
    <script type="text/javascript" id="MathJax-script" async
        src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
    </script>
    </head>

    <body>
    """

    footer = """
    </body>\n</html>\n"""

    navbar = """
    <div style="float: left"><a href = "{linkprev}">Prev</a></div>
	<div style="float: right"><a href = "{linknext}">Next</a></div>
	<div style="margin: 0 auto;  width: 200px;"><a href = "toc.html">Contents</a></div>
    """

    if prev is None:
        prev = "PREV"
    if next is None:
        next = "NEXT"

    pageStr = header.format(pagetitle=pagetitle)+navbar.format(linkprev=prev+".html", linknext=next+".html")+\
        "\n\n\t<hr>\n\t<h1>{title}</h1>\n".format( title=title )
    if desc is not None:
        pageStr += "\n\t<p>{desc}</p>\n\n".format( desc=desc )


    if type( names ) == list:
        listStr = ""
        for name in names:
            listStr += thumbnailStr.format( name=name, texname = texName( name ) )
        pageStr += listWrapper.format(thumbnaillist=listStr)
    elif type( names ) == dict:
        for subtitle in names:
            listStr = ""
            for name in names[subtitle]:
                listStr += thumbnailStr.format( name=name, texname = texName( name ) )
            pageStr += subListHeader.format(subtitle=subtitle)
            pageStr += listWrapper.format(thumbnaillist=listStr)
            pageStr += sublistSeparator
        pageStr = pageStr[:len(sublistSeparator)]
    else:
         raise( Exception( "names was a bad type" ) )  
    
    return pageStr + "<br>\n\t<hr>\n"+navbar.format(linkprev=prev+".html", linknext=next+".html") + footer   

def storeDataForWebMany( names ):
    """Analyze pinning data and generate images. Very slow/expensive."""
    go = input( "Ready to analyze {} multiloops. Continue? (y/n)".format(len(names)))
    if go != 'y':
        return
    for i in range(len( names ) ):
        print( "Analyzing {} ({} of {})".format( names[i], i+1, len( names )  ) )
        storeDataForWeb( names[i] )

def makeWebPagesMany( names ):
    """Generate web paes based on data in the database. Also very slow for some reason, but should not depend on anything about the loop."""
    for i in range( len( names ) ):
        print( "Writing web page for {} ({} of {})".format( names[i], i+1, len( names ) ) )
        makeWebPage( names[i] )

def createDatabase( maxRegions = 16 ):
    response = input( "Erase the existing database? (y/n)")    
    if response != 'y':
        return
    try:
        cursor.execute("DROP DATABASE multiloops") #hangs sometimes, if this happens:
        # run and kill the hanging processes with
        # sudo mysqladmin processlist -u root -p
        # sudo mysqladmin kill [pid]
    except: #DatabaseError
        pass

    cursor.execute("CREATE DATABASE multiloops")
    cursor.execute("USE multiloops")
    create_table = """
        CREATE TABLE mloops(
        id INT AUTO_INCREMENT PRIMARY KEY,
        pc VARCHAR(250),
        pd VARCHAR(250),     
        sigma VARCHAR(250),
        components INT,
        epsilon VARCHAR(250),
        phi VARCHAR(250),
        drawnpd VARCHAR(250),        
        numRegions INT,
        name VARCHAR(20),
        minPinSets VARCHAR(500),
        degSequence VARCHAR(75),
        minRegionDegree INT,
        isMultiSimple BOOL,
        pinNum INT,
        totOpt INT,
        totMin INT,
        totPinSets INT,
        avgOptDeg FLOAT,
        avgMinDeg FLOAT,
        avgOverallDeg FLOAT,
        refinedPinSetMat VARCHAR(5000),
        degDataMat VARCHAR(1000)        
        )
    """
    cursor.execute(create_table)
    for k in range( 4, maxRegions+1):
        generateMultiloops( k, numComponents = "any" ,includeReflections = False, primeOnly = True, db = db, cursor = cursor )


def nameToID( name ):
    cursor.execute( 'select id from mloops where name = "{}";'.format( name) )
    id = cursor.fetchall()[0][0]
    return id

def name_k_after( name, k ):
    nextID = nameToID( name )+k
    #print( nextID )
    cursor.execute( 'select name from mloops where id = {};'.format( nextID ) )
    nextName = cursor.fetchall()[0][0]
    if nextName is None:  # Null value       
        return None
    return nextName

#def smartName( name ):
#    comps = name.split( "^" )[1]
#    ind = name.split("^")[0].split("_")[1]
#    regs = name.split("_")[0]
#    return regs+"^"+comps+"_"+ind

def texName( name ): 
    pieces = re.split( "[_^]", name )
    return "$"+pieces[0]+"^{"+pieces[1]+"}_{"+pieces[2]+"}$"

def nextName( name ):
    return name_k_after( name, 1 )

def prevName( name ):
    return name_k_after( name, -1 )

def namesSatisfyingQuery( queryParams ):
    query = 'select name from mloops where {};'.format( queryParams )
    cursor.execute( query )
    result = []
    for elt in cursor.fetchall():
        result.append( elt[0] )
    return result

def getFieldByName( field, name ):
    query = 'select {} from mloops where name = "{}";'.format(field, name) 
    #print( query )
    cursor.execute( query )
    result = cursor.fetchall()[0][0]
    return result

def setFieldByName( field, value, name ):
    cursor.execute( 'update mloops set {} = "{}" where name="{}";'.format(field,value,name) )
    db.commit()

def printRow( name ):
    data = rowDict( name )
    for key in data:
        print( key, ":", data[key] )

def rowDict( name ):
    cursor.execute("SHOW columns FROM mloops")
    columns = [column[0] for column in cursor.fetchall()]
    cursor.execute( 'select * from mloops where name = "{}";'.format( name) )
    #print( "returned", cursor.fetchall()[0][1] )
    entries = cursor.fetchall()[0]
    data = {}
    for i in range( len( entries )):
        data[columns[i]] = entries[i]
    return data

def storeDrawnPD( name ):
    setFieldByName( "drawnpd", plinkPD( getFieldByName( "pd", name) ), name )

def storeDataForWeb( name ):
    print( " Computing pinning sets for {}".format( name ) )
    storeMinPinSetDataForWeb( name )
    print( " Generating images for {}".format( name ) )
    generateImageFilesForWeb( name )

def makeWebPage( name ):
    
    f = open( "docs/multiloop_page_template.html", 'r' )
    templateStr = f.read()
    f.close()
    f = open( "docs/multiloops/"+name+".html", "w")
    try:
        pName = prevName( name )
    except IndexError:
        pName = "nopreviousexists"
    nName = nextName( name )
    context = name.split("_")[0]+".html"+"#"+name

    data = rowDict( name )

    if data["isMultiSimple"] == 0:
        msimp = "No"
    else:
        msimp = '<a href="../multisimple.html#{}">Yes</a>'.format( name )

    if data[ "components" ] == 1:
        loopOrMultiloop = "loop"
        loopOrMultiloopCapitalized = "Loop"
    else:
        loopOrMultiloop = "multiloop"
        loopOrMultiloopCapitalized = "Multiloop"

    refinedTableHeaders = [["Pin label", "Pin color", "Regions", "Cardinality", "Degree sequence","Mean-degree"]]
    cardinalTableHeaders = [["Cardinality", "Optimal pinning sets", "Minimal suboptimal pinning sets", "Nonminimal pinning sets", "Averaged mean-degree"]]

    if data[ "minRegionDegree" ] > 2:
        minDegStr = '<a href="../index.html#{}">{}</a>'.format( name, data[ "minRegionDegree" ] )
    else:
        minDegStr = str( data[ "minRegionDegree" ] )

    #print( "hi ")
 
    f.write( templateStr.format( rawname = name, texname = texName( name ),\
                                 linkprev = pName+".html", \
                                 linknext = nName+".html", \
                                 linkcontext = "../"+context, \
                                 pinset_svg_path = name+"/pindata.svg",\
                                 lattice_svg_path = name+"/lattice.svg",\
                                 pinnum = data["pinNum"],\
                                 numOpt = data["totOpt"],\
                                 numMin = data["totMin"],\
                                 numTot = data["totPinSets"],\
                                 avgOptDeg = data[ "avgOptDeg" ],\
                                 avgMinDeg = data["avgMinDeg"],\
                                 avgOverallDeg = data["avgOverallDeg"],\
                                 refinedTableStr = htmlTable( refinedTableHeaders+eval( data["refinedPinSetMat"] )[1:] ),\
                                 degTableStr = htmlTable( cardinalTableHeaders+eval( data[ "degDataMat"] )[1:] ),\
                                 degseq = data[ "degSequence" ],\
                                 mindeg = minDegStr,\
                                 ismultisimp = msimp,\
                                 othercomments = "",\
                                 loopOrMultiloop = loopOrMultiloop,\
                                 loopOrMultiloopCapitalized = loopOrMultiloopCapitalized,\
                                 sigma = data[ "sigma" ],\
                                 epsilon = data["epsilon"],\
                                 annotated_svg_path = name+"/annotated.svg",\
                                 phi = data["phi"],\
                                 pc = data["pc"],\
                                 pd = data["pd"] ) ) 
    f.close()

def storeMinPinSetDataForWeb( name, debug = False ):
    """Computes and stores the minimal pinning set data in the database"""

    storeDrawnPD( name )
    drawnpd = eval( getFieldByName( "drawnpd", name) )
    #print( drawnpd )
    mloop = Spherimultiloop(drawnpd)
    setFieldByName( "sigma", mloop.sigmaToString(), name)
    setFieldByName( "epsilon", mloop.epsilonToString(), name)
    setFieldByName( "phi", mloop.phiToString(), name)

    pinSets = getPinSets( drawnpd, debug=debug )

    setFieldByName( "minPinSets", pinSets["minPinSets"], name)

    avgDegByCardTable, avgOptimalDeg, avgMinimalDeg, avgOverallDeg, pinningNum, numOptimal = avgDegByCardData( pinSets )

    setFieldByName( "degDataMat", avgDegByCardTable, name)
    setFieldByName( "avgOptDeg", avgOptimalDeg, name)
    setFieldByName( "avgMinDeg", avgMinimalDeg, name)
    setFieldByName( "avgOverallDeg", avgOverallDeg, name)
    #print( getRefinedTableMat( name ) )
    setFieldByName( "refinedPinSetMat", getRefinedTableMat( name ), name )
    setFieldByName( "pinNum", pinningNum, name )
    setFieldByName( "totOpt", numOptimal, name )
    setFieldByName( "totMin", len( pinSets["minPinSets"] ), name )
    setFieldByName( "totPinSets", len( pinSets["pinSets"] ), name )

    #print( htmlTable( getFieldByName( "refinedPinSetMat", name) ) )

def avgDegByCardData( pinningSets ):
    pinDict = {}
    for elt in pinningSets["pinSets"]:
        if len( elt ) not in pinDict:
            pinDict[len(elt)] = [elt]
        else:
            pinDict[len(elt)].append( elt )

    minPinDict = {}
    for elt in pinningSets["minPinSets"]:
        if len( elt ) not in minPinDict:
            minPinDict[len(elt)] = [elt]
        else:
            minPinDict[len(elt)].append( elt )

    pinningNum = min( list( minPinDict ) )
    numOptimal = len( minPinDict[pinningNum] )
    numMinimal = len( pinningSets["minPinSets"] )
    #gonalityDict = {}
    regToGonality = {}
    avgDegreesByCardinal = {}
    optAvgDegrees = []
    minAvgDegrees = []
    allAvgDegrees = []
    for reg in pinningSets["fullRegSet"]:
        regToGonality[reg] = len( binSet( reg ) )
    for elt in pinningSets["pinSets"]:
        degrees = []
        regs = list( elt )
        regs.sort()
        for reg in regs:
            degrees.append( regToGonality[reg] )
        thisAvgDegree = sum(degrees)/len(degrees)
        if len( elt ) not in avgDegreesByCardinal:
            avgDegreesByCardinal[len(elt)] = [thisAvgDegree]
        else:
            avgDegreesByCardinal[len(elt)].append( thisAvgDegree )
        isMinimal = ( elt in pinningSets["minPinSets"] )
        isOptimal = isMinimal and len( elt ) == pinningNum
        if isOptimal:
            optAvgDegrees.append( thisAvgDegree )
        if isMinimal:
            minAvgDegrees.append( thisAvgDegree )
        allAvgDegrees.append( thisAvgDegree )

    #print( "opts:", len( optAvgDegrees ), optAvgDegrees )
    #print( "mins:", len( minAvgDegrees ), minAvgDegrees)
        
        #gonalities = []
        #for reg in regs:
        #    gonalities.append( regToGonality[reg] )
        
        #gonalityDict[frozenset(elt)]={"gons":gonalities,"min":isMinimal}

    #tableMatrix = [["Cardinality", "Optimal pinning sets", "Minimal (suboptimal) pinning sets", "Nonminimal pinning sets", "Averaged mean-degree"]]
    tableMatrix = [[]] # use empty headers to save space

    for cardinal in sorted( pinDict ):
        tableRow = [cardinal]
        if cardinal == pinningNum:
            tableRow.append( numOptimal )            
        else:
            tableRow.append( 0 )
        if cardinal in minPinDict and cardinal != pinningNum:
            tableRow.append( len( minPinDict[cardinal] ) )
        else:
            tableRow.append( 0 )
        if cardinal in minPinDict:
            tableRow.append( len(pinDict[cardinal])-len(minPinDict[cardinal]) )
        else:
            tableRow.append( len( pinDict[cardinal] ) )
        tableRow.append( round( sum( avgDegreesByCardinal[cardinal] )/len( avgDegreesByCardinal[cardinal] ), 2 ) )
        tableMatrix.append( tableRow )
    tableMatrix.append(["Total", numOptimal, numMinimal-numOptimal, len(pinningSets["pinSets"])-numMinimal, ""])

    return tableMatrix, sum( optAvgDegrees )/len( optAvgDegrees ), sum( minAvgDegrees )/len( minAvgDegrees ), sum( allAvgDegrees )/len( allAvgDegrees ), pinningNum, numOptimal

def getRefinedTableMat( name ):
    #minPinSets = getFieldByName( "minPinSets", name )    
    labelData = getPinningSetLabelData( name )
    #drawnpd = labelData["drawnpd"]
    minPinSetDict = labelData["minPinSetDict"]
    #regList = labelData["regList"]
    numericRegionLabels = labelData["numericLabels"]
    degreeRegionLabels = labelData["degreeLabels"]
    #emptyLabels = labelData["emptyLabels"]
    G = labelData["G"]

    #print( minPinSetDict )

    sortedKeys = sorted( list( minPinSetDict ), key = lambda fset: minPinSetDict[fset]["label"] )
        
    #refinedPinData = [["Pin label", "Pin color", "Regions", "Cardinality", "Degree sequence","Mean-degree"]]
    refinedPinData = [[]] # use empty headers to save sapce

    for pinningSet in sortedKeys:
        refinedData = []
        label = minPinSetDict[pinningSet]["letterLabel"]
        if label.upper() == label:
            label += " (optimal)"
        else:
            label += " (minimal)"
        refinedData.append( label )
        rgb = []
        for entry in minPinSetDict[pinningSet]["color"]:
            rgb.append( entry*255 )
        refinedData.append( """rgb{}""".format( tuple( rgb ) ) )
        #refinedData.append( """<span style='font-size:100px;line-height:20px;color:rgb{};'>&bull;</span>""".format( tuple( rgb ) ) )
        regions = set()
        for reg in pinningSet:
            regions.add( int( numericRegionLabels[reg] ) )
        refinedData.append( "{"+str( sorted( regions ) )[1:-1]+"}" )
        refinedData.append( len(pinningSet) )
        degSeq = []
        for reg in pinningSet:
             degSeq.append( degreeRegionLabels[reg] )
        degSeq.sort()
        refinedData.append( degSeq )
        refinedData.append( "{:.2f}".format( sum( degSeq )/len( degSeq ) ) )
        refinedPinData.append( refinedData )

    return refinedPinData

def htmlTable( data ):
    """Assumes data is a list of lists where the first list is the headers"""

    #print( data )

    tableStr = """
    <table class="tg" style="table-layout: fixed; width: 100%; text-align:center;">
        <thead>
             <tr>"""
    for header in data[0]:
        tableStr += """
                <th class="tg-0pky">{}</th>""".format(header)
    tableStr += """
            </tr>
        </thead>
	<tbody>"""
    for i in range( 1, len( data ) ):
        tableStr += """
            <tr>"""
        for entry in data[i]:
            if type( entry ) == str and len( entry ) >= 3 and entry[0:3] == "rgb":
                tableStr += """
                    <td class="tg-0lax"><span style='font-size:100px;line-height:20px;color:{};'>&bull;</span></td>""".format(entry)
            else:
                tableStr += """
                    <td class="tg-0lax">{}</td>""".format(entry)
        tableStr += """
            </tr>"""
    tableStr +=  """
        </tbody>
    </table>\n"""

    return tableStr

def generateImageFilesForWeb( name ):
    minPinSets = eval( getFieldByName( "minPinSets", name ) )
    labelData = getPinningSetLabelData( name )
    drawnpd = labelData["drawnpd"]
    minPinSetDict = labelData["minPinSetDict"]
    regList = labelData["regList"]
    numericRegionLabels = labelData["numericLabels"]
    degreeRegionLabels = labelData["degreeLabels"]
    emptyLabels = labelData["emptyLabels"]
    G = labelData["G"]

    if not os.path.isdir("docs/multiloops/"+name):
        os.mkdir("docs/multiloops/"+name)

    # save the semilattice
    posetFile = drawLattice( None, minPinSets, set( regList ), minPinSetDict, labelMode = "pinning_sets", \
                                         regionLabels = None, forWeb = True, webImFolder = name, filename = "" )
 
    # save raw loop
    plinkImgFile( str( getFieldByName( "pd", name) ), drawnpd, G.adjDict, G.wordDict,\
                                  [],None,\
                                  emptyLabels, pdToComponents( drawnpd ), forWeb = True, webImFolder = name, filename = "clean"  )
    
    # save annotated loop
    plinkImgFile( str( getFieldByName( "pd", name) ), drawnpd, G.adjDict, G.wordDict,\
                                  [],None,\
                                  emptyLabels, pdToComponents( drawnpd ), forWeb = True, webImFolder = name, filename = "annotated", sigmaAnnotated = True )
    
    # save raw with numeric labels
    plinkImgFile( str( getFieldByName( "pd", name) ), drawnpd, G.adjDict, G.wordDict,\
                                  [],None,\
                                  numericRegionLabels, pdToComponents( drawnpd ), forWeb = True, webImFolder = name, filename = "labels_numeric" )
    
    # save raw with degree labels
    plinkImgFile( str( getFieldByName( "pd", name) ), drawnpd, G.adjDict, G.wordDict,\
                                  [],None,\
                                  degreeRegionLabels, pdToComponents( drawnpd ), forWeb = True, webImFolder = name, filename = "labels_degree" )
    
    # save raw + pinning data
    plinkImgFile( str( getFieldByName( "pd", name) ), drawnpd, G.adjDict,\
                                         G.wordDict, minPinSets, minPinSetDict, emptyLabels,\
                                        pdToComponents( drawnpd ), forWeb = True, webImFolder = name, filename = "pindata_clean", debug=False )
    
    # save numeric + pinning data
    plinkImgFile( str( getFieldByName( "pd", name) ), drawnpd, G.adjDict,\
                                         G.wordDict, minPinSets, minPinSetDict, numericRegionLabels,\
                                        pdToComponents( drawnpd ), forWeb = True, webImFolder = name, filename = "pindata", debug=False )
    
    # save degree + pinning data
    plinkImgFile( str( getFieldByName( "pd", name) ), drawnpd, G.adjDict,\
                                         G.wordDict, minPinSets, minPinSetDict, degreeRegionLabels,\
                                        pdToComponents( drawnpd ), forWeb = True, webImFolder = name, filename = "pindata_degree", debug=False )
    
def getPinningSetLabelData( name ):
    minPinSets = getFieldByName( "minPinSets", name )
    if minPinSets is None:
        raise( Exception("Pinning sets have not yet been computed") )
    minPinSets = eval( minPinSets )
    
    drawnpd = eval( getFieldByName( "drawnpd", name) )
    G = SurfaceGraphFromPD( drawnpd )
    regList = list( G.wordDict.copy().keys() )
    regList.sort()

    numericRegionLabels = {}
    degreeRegionLabels = {}
    emptyLabels = {}
    for i in range( len( regList ) ):
        numericRegionLabels[regList[i]] = i+1
        degreeRegionLabels[regList[i]] = len( G.wordDict[regList[i]] )
        emptyLabels[regList[i]] = ""
    
    minDict = {}    
    for elt in minPinSets:
        if len( elt ) not in minDict:
            minDict[len(elt)] = [elt]
        else:
            minDict[len(elt)].append( elt )
    minlen = min( minDict )
 
    minsuboptimals = []
    optimals = []
    for elt in minPinSets:
        if len( elt ) == minlen:
            optimals.append( elt )
        else:
            minsuboptimals.append( elt )
    
    numOptimal = len( minDict[minlen] )
    numMinimal = len( minPinSets ) - numOptimal 
    pinSetColors = computeRGBColors( numOptimal, numMinimal )
    minPinSetDict = {}
    label = 1
    for pinset in minPinSets:
        minPinSetDict[frozenset(pinset)] = {}
    
    j = 0

    letterLabel = 'A'
    firstTime = True
    sortedKeys = list( minDict )
    sortedKeys.sort()
    for key1 in sortedKeys:
        for i in range( len( minDict[key1] ) ):
            elt = frozenset( minDict[key1][i] )
            #print( elt )
            if key1 == minlen:
                dictkey = "opts"
                colorvar = i
                numColors = numOptimal
                #specifier = " (optimal)"
            else:
                dictkey = "mins"
                if firstTime:
                #    col3 += "\\end{enumerate}\n"
                #    col3 += "\\textbf{Minimal (suboptimal) pinning sets:}\n\n"
                #    col3 += "\\begin{enumerate}[a)]\n"
                    #rows.append( ["Minimal pinning set","","","","",""] )
                    letterLabel = 'a'
                firstTime = False
                colorvar = j
                numColors = numMinimal
                #specifier = " (minimal)"
                #elt = data[link]["minPinSets"][i]
            minPinSetDict[elt]["letterLabel"] = letterLabel
            #row.append( letterLabel+specifier )

            #numTotalColors = len( pinSetColors[dictkey] )    
            #colorIndex = int( colorvar*(numTotalColors/numColors) ) 
                                    
            minPinSetDict[elt]["label"] = label
            label += 1
            minPinSetDict[elt]["color"] = pinSetColors[dictkey][colorvar]["rgb"]
            if key1 != minlen:
                j+=1
            if letterLabel.isupper():
                letterLabel = alphabet[ (alphabet.index( letterLabel.lower())+1)%len(alphabet) ].upper() # chr(ord(letterLabel) + 1)
            else:
                letterLabel = alphabet[ (alphabet.index( letterLabel)+1)%len(alphabet) ]

    return {"drawnpd":drawnpd, "G":G, "numericLabels":numericRegionLabels, "degreeLabels":degreeRegionLabels, "emptyLabels":emptyLabels, "regList":regList, "minPinSetDict":minPinSetDict}
    
####################### RUN MAIN ####################################

if __name__ == "__main__":
    main()