from planeloop import *
import mysql.connector
import os
# https://dev.mysql.com/doc/mysql-getting-started/en/#mysql-getting-started-basic-ops

db = mysql.connector.connect( username=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PASS') )
cursor = db.cursor()

try:
    cursor.execute("USE multiloops")
except NameError as msg:
    traceback.print_exc()
    #raise Exception( msg ) # database not found
    
def main():
    #createDatabase()
    #storeMinPinSets( "12_360^1" )
    #generateImageFilesForWeb( "12_360^1")
    #storeRefinedPinningData( "12_360^1" )
    #print( getFieldByName( "drawnpd", "12_361^1"  ) )

    #storeMinPinSets( "10_18^1" )
    #generateImageFilesForWeb( "10_18^1")
    #storeRefinedPinningData( "10_18^1")

    generateImageFilesForWeb( "11_97^1")
    storeMinPinSets( "11_97^1" )
    storeRefinedPinningData( "11_97^1")

def createDatabase( maxRegions = 12 ):
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
        pc VARCHAR(500),
        pd VARCHAR(500),     
        sigma VARCHAR(500),
        components INT,
        epsilon VARCHAR(500),
        drawnpd VARCHAR(500),        
        numRegions INT,
        name VARCHAR(20),
        next VARCHAR(20),
        prev VARCHAR(20),
        minPinSets VARCHAR(1028)
        )
    """
    cursor.execute(create_table)
    for k in range( 4, maxRegions+1):
        generateMultiloops( k, numComponents = "any" ,includeReflections = False, primeOnly = True, db = db, cursor = cursor )

def getFieldByName( field, name ):
    cursor.execute( 'select {} from mloops where name = "{}";'.format(field, name) )
    result = cursor.fetchall()[0][0]
    if result is None:  # Null value       
        return None
    return eval( result )

def setFieldByName( field, value, name ):
    cursor.execute( 'update mloops set {} = "{}" where name="{}";'.format(field,value,name) )
    db.commit()

def printRow( name ):
    cursor.execute("SHOW columns FROM mloops")
    columns = [column[0] for column in cursor.fetchall()]
    cursor.execute( 'select * from mloops where name = "{}";'.format( name) )
    #print( "returned", cursor.fetchall()[0][1] )
    entries = cursor.fetchall()[0]
    for i in range( len( entries )):
        print( columns[i], ":", entries[i] )

def storeDrawnPD( name ):
    setFieldByName( "drawnpd", plinkPD( getFieldByName( "pd", name) ), name)

def storeMinPinSets( name, debug = False, mode = "drawnPD" ):
    """Computes and stores the minimal pinning sets in the database
    mode = "originalPD" --> Use the pd code that is computed from the plantri rep
    mode = "drawnPD" --> Use the pd code that is drawn by snappy based on the pd code from the plantri rep """
    
    if mode == "drawnPD":
        storeDrawnPD( name )
        drawnpd = getFieldByName( "drawnpd", name)
        pinSets = getPinSets( drawnpd, debug=debug )
    elif mode == "originalPD":
        pd = getFieldByName( "pd", name)
        pinSets = getPinSets( pd, debug=debug )
    else:
        raise( "bad mode" )
   
    print( pinSets )
    setFieldByName( "minPinSets", pinSets["minPinSets"], name)
    #printRow( name )

def storeRefinedPinningData( name ):
    minPinSets = getFieldByName( "minPinSets", name )    
    labelData = getPinningSetLabelData( name )
    drawnpd = labelData["drawnpd"]
    minPinSetDict = labelData["minPinSetDict"]
    regList = labelData["regList"]
    numericRegionLabels = labelData["numericLabels"]
    degreeRegionLabels = labelData["degreeLabels"]
    emptyLabels = labelData["emptyLabels"]
    G = labelData["G"]

    #print( minPinSetDict )
        
    refinedPinData = []
    for pinningSet in minPinSetDict:
        refinedData = {}
        refinedData["Pin label"] = minPinSetDict[pinningSet]["letterLabel"]
        if refinedData["Pin label"].upper() == refinedData["Pin label"]:
            refinedData["Pin label"] += " (optimal)"
        else:
            refinedData["Pin label"] += " (minimal)"
        rgb = []
        for entry in minPinSetDict[pinningSet]["color"]:
            rgb.append( entry*255 )
        refinedData["Pin color"] = tuple( rgb )
        refinedData["Regions"] = set()
        for reg in pinningSet:
            refinedData["Regions"].add( numericRegionLabels[reg] )
        refinedData["Cardinality"] = len(pinningSet)
        refinedData["Degree sequence"] = []
        for reg in pinningSet:
             refinedData["Degree sequence"].append( degreeRegionLabels[reg] )
        refinedData["Degree sequence"].sort()
        refinedData["Average degree"] = sum( refinedData["Degree sequence"] )/len( refinedData["Degree sequence"] )
        refinedPinData.append( refinedData )

    
    print( eval( str( refinedPinData ) ) )
    # todo: add to database


def generateImageFilesForWeb( name ):
    minPinSets = getFieldByName( "minPinSets", name )    
    labelData = getPinningSetLabelData( name )
    drawnpd = labelData["drawnpd"]
    minPinSetDict = labelData["minPinSetDict"]
    regList = labelData["regList"]
    numericRegionLabels = labelData["numericLabels"]
    degreeRegionLabels = labelData["degreeLabels"]
    emptyLabels = labelData["emptyLabels"]
    G = labelData["G"]

    if not os.path.isdir("docs/img/"+name):
        os.mkdir("docs/img/"+name)

    # save the semilattice
    posetFile = drawLattice( None, minPinSets, set( regList ), minPinSetDict, labelMode = "pinning_sets", \
                                         regionLabels = None, forWeb = True, webImFolder = name, filename = name )
 
    # save raw loop
    plinkImgFile( str( getFieldByName( "pd", name) ), drawnpd, G.adjDict, G.wordDict,\
                                  [],None,\
                                  emptyLabels, pdToComponents( drawnpd ), forWeb = True, webImFolder = name, filename = name+"-raw" )
    
    # save raw with numeric labels
    plinkImgFile( str( getFieldByName( "pd", name) ), drawnpd, G.adjDict, G.wordDict,\
                                  [],None,\
                                  numericRegionLabels, pdToComponents( drawnpd ), forWeb = True, webImFolder = name, filename = name+"-num" )
    
    # save raw with degree labels
    plinkImgFile( str( getFieldByName( "pd", name) ), drawnpd, G.adjDict, G.wordDict,\
                                  [],None,\
                                  degreeRegionLabels, pdToComponents( drawnpd ), forWeb = True, webImFolder = name, filename = name+"-deg" )
    
    # save raw + pinning data
    plinkImgFile( str( getFieldByName( "pd", name) ), drawnpd, G.adjDict,\
                                         G.wordDict, minPinSets, minPinSetDict, emptyLabels,\
                                        pdToComponents( drawnpd ), forWeb = True, webImFolder = name, filename = name+"-raw+minpinning", debug=False )
    
    # save numeric + pinning data
    plinkImgFile( str( getFieldByName( "pd", name) ), drawnpd, G.adjDict,\
                                         G.wordDict, minPinSets, minPinSetDict, numericRegionLabels,\
                                        pdToComponents( drawnpd ), forWeb = True, webImFolder = name, filename = name+"-num+minpinning", debug=False )
    
    # save degree + pinning data
    plinkImgFile( str( getFieldByName( "pd", name) ), drawnpd, G.adjDict,\
                                         G.wordDict, minPinSets, minPinSetDict, degreeRegionLabels,\
                                        pdToComponents( drawnpd ), forWeb = True, webImFolder = name, filename = name+"-deg+minpinning", debug=False )
    
def getPinningSetLabelData( name ):
    minPinSets = getFieldByName( "minPinSets", name )
    if minPinSets is None:
        raise( Exception("Pinning sets have not yet been computed") )
    
    drawnpd = getFieldByName( "drawnpd", name)
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