"""
 Title: planeloop.py
 Authors: Christopher-Lloyd Simon and Ben Stucky
 Description: Computes pinning sets of loops in the plane and sphere
 Github: https://github.com/ChristopherLloyd/LooPin

 Important info for other users:

 This program is intended to be loaded/run from within sage
 using the command:

 load( 'planeloop.py' )

 It will not work as a standalone python script,
 except from the python environment bundled with sage.
 to override this (for example if only using functions
 which use snappy), uncomment the line below."""

from sage.all import *

"""All imported python packages must be installed in the python environment
 that sage uses. For instance you need to run:

 sage -pip install snappy

 or

 sage -pip install snappy_15_knots  # Larger version of HTLinkExteriors

 to be able to use snappy."""


# Get the needed imports

from random import *
import traceback #used for warnings/debugging
import warnings #used for warnings/debugging
import snappy #used for plotting knots and links
import os #used for removing temp files
import shutil #used for removing temp files
from subprocess import call #used for running external scripts
from subprocess import check_output
from latextable_lite import utils
import mysql.connector
import matplotlib.pyplot as plt


#import pylatex as p

# Currently unused imports:

#import lightrdf
#import gzip
#import rdflib
#import re
#from math import sqrt
#import timeit

# Global constants

ALPHABET = "abcdefghijklmnopqrstuvwxyz"*5 # generator alphabet, used for readable output only. Inverses are upper case
alphabet = "abcdefghijklmnopqrstuvwxyz"

# SOME OF OUR FAVORITE LOOPS FOR TESTING

#8 crossing loop with no embedded monorbigons
link8 = [(1, 7, 2, 6), (3, 8, 4, 9), (5, 11, 6, 10), (16, 12, 1, 11), \
        (2, 13, 3, 14), (4, 16, 5, 15), (7, 12, 8, 13), (9, 15, 10, 14)]

# a 9 crossing example
link9 = [(1, 7, 2, 6), (4, 9, 5, 10), (2, 12, 3, 11),\
        (7, 13, 8, 12), (18, 13, 1, 14), (3, 17, 4, 16),\
        (5, 14, 6, 15), (8, 18, 9, 17), (10, 15, 11, 16)]

#mona lisa loop:
monalisa = [(24, 6, 1, 5), (3, 10, 4, 11), (1, 13, 2, 12), \
        (6, 14, 7, 13), (2, 17, 3, 18), (8, 15, 9, 16), \
        (11, 19, 12, 18), (4, 20, 5, 19), (7, 23, 8, 22),\
        (9, 20, 10, 21), (14, 24, 15, 23), (16, 21, 17, 22)]

weird3case = [[1, 6, 2, 1], [5, 4, 6, 5], [2, 4, 3, 3]]

another3 = [[6, 12, 1, 7], [7, 5, 8, 6], [8, 11, 9, 12], [1, 4, 2, 5],\
           [10, 16, 11, 13], [9, 16, 10, 15], [3, 14, 4, 15], [2, 14, 3, 13]]

labelIssue1 = [[6, 12, 1, 7], [7, 3, 8, 4], [11, 5, 12, 6], [1, 13, 2, 16],\
               [2, 15, 3, 16], [8, 15, 9, 14], [4, 10, 5, 11],[13, 10, 14, 9]]

labelIssue2 = [[4, 14, 1, 5], [5, 10, 6, 11], [11, 3, 12, 4], [13, 18, 14, 15],\
               [1, 9, 2, 10], [6, 2, 7, 3], [12, 16, 13, 15], [8, 17, 9, 18], [7, 17, 8, 16]]

labelIssue3 = [[6, 14, 1, 7], [7, 15, 8, 18], [13, 5, 14, 6], [1, 16, 2, 15],\
               [8, 11, 9, 12], [12, 17, 13, 18], [4, 16,5, 17], [2, 10, 3, 11], [9, 3, 10, 4]]

# for some of the figures:
smallMonorbigonLess = [[[4, 8, 1, 5], [5, 9, 6, 12], [3, 11, 4, 12], [7, 10, 8, 11], [1, 10, 2, 9], [6, 2, 7, 3]],\
[[5, 16, 6, 1], [9, 4, 10, 5], [10, 15, 11, 16], [6, 11, 7, 12], [1, 12, 2, 13], [13, 8, 14, 9], [14, 3, 15, 4], [7, 3, 8, 2]],\
[[18, 5, 1, 6], [6, 11, 7, 12], [12, 17, 13, 18], [13, 4, 14, 5], [1, 10, 2, 11], [7, 16, 8, 17], [8, 3, 9, 4], [14, 9, 15, 10], [2, 15, 3, 16]],\
[[13, 20, 14, 1], [5, 12, 6, 13], [6, 19, 7, 20], [14, 7, 15, 8], [1, 8, 2, 9], [17, 4, 18, 5], [18, 11, 19, 12], [15, 3, 16, 2], [9, 16, 10, 17], [10, 3, 11, 4]],\
[[14, 20, 1, 15], [15, 6, 16, 5], [13, 4, 14, 5], [9, 19, 10, 20], [1, 10, 2, 11], [6, 11, 7, 12], [16, 12, 17, 13], [8, 3, 9, 4], [18, 2, 19, 3], [7, 18, 8, 17]],\
[[6, 12, 1, 7], [7, 13, 8, 16], [5, 15, 6, 16], [11, 14, 12, 15], [1, 14, 2, 13], [8, 17, 9, 20], [4, 19, 5, 20], [10, 18, 11, 19], [2, 18, 3, 17], [9, 3, 10, 4]]]


tripleLem = [(4,5,5,6),(1,8,2,9),(6,12,7,11),(3,12,4,13),\
             (10,13,11,14),(22,15,1,16),(7,19,8,18),(14,18,15,17),\
             (2,19,3,20),(9,20,10,21),(16,21,17,22)]

quadTrefoil =  [(102,16,1,15),(7,16,8,17),(8,24,9,23),(14,25,15,26),(17,33,18,32),\
                (22,33,23,34),(1,41,2,40),(26,40,27,39),(6,41,7,42),(9,49,10,48),(31,42,32,43),\
                (34,48,35,47),(13,50,14,51),(18,58,19,57),(38,51,39,52),(43,57,44,56),(21,58,22,59),\
                (46,59,47,60),(2,66,3,65),(27,65,28,64),(52,64,53,63),(5,66,6,67),(30,67,31,68),(55,68,56,69),\
                (10,74,11,73),(35,73,36,72),(60,72,61,71),(12,75,13,76),(19,83,20,82),(37,76,38,77),(44,82,45,81),\
                (62,77,63,78),(69,81,70,80),(20,83,21,84),(45,84,46,85),(70,85,71,86),(3,91,4,90),(28,90,29,89),\
                (53,89,54,88),(78,88,79,87),(4,91,5,92),(29,92,30,93),(54,93,55,94),(79,94,80,95),(11,99,12,98),\
                (36,98,37,97),(61,97,62,96),(86,96,87,95),(24,102,25,101),(49,101,50,100),(74,100,75,99)]

naiveGonalityCounterExample = [(12,1,13,2),(6,3,7,4),(10,5,11,6),(14,7,15,8),\
                               (4,9,5,10),(16,11,1,12),(8,13,9,14),(2,15,3,16)]

strongerCounterEx10 = [[1, 5, 20, 6], [1, 14, 2, 15],\
                     [5, 11, 4, 12], [20, 12, 19, 13], [6, 13, 7, 14],\
                     [2, 9, 3, 10], [15, 10, 16, 11], [4, 16, 3, 17], \
                     [19, 8, 18, 7], [9, 18, 8, 17]]

strongerCounterEx9 = [[1, 4, 18, 3], [1, 12, 2, 13], [4, 10, 5, 9], [18, 9, 17, 8],\
                      [3, 11, 2, 12], [13, 11, 14,10], [5, 14, 6, 15],\
                      [17, 7, 16, 8], [6, 16, 7, 15]]

sumCounterEx = [(5,8,6,9),(2,12,3,11),(1,16,2,17),(12,16,13,15),(4,20,5,19),(9,18,10,19),\
                (6,22,7,21),(7,22,8,23),(20,24,21,23),(3,24,4,25),(10,26,11,25),(17,26,18,27),\
                (30,28,1,27),(13,28,14,29),(14,30,15,29)]

flypeExample =  [(1,10,2,1),(5,2,6,3),(3,9,4,8),(7,5,8,4),(9,6,10,7)]
flypeExample2 = [(2,5,3,6),(6,1,7,2),(8,4,9,3),(4,8,5,7),(10,9,1,10)]

flype1 = [(3,10,4,11),(11,4,12,5),(13,9,14,8),(9,17,10,16),\
         (17,13,18,12),(19,7,20,6),(21,14,22,15),(23,1,24,32),\
         (15,22,16,23),(25,2,26,3),(1,26,2,27),(27,25,28,24),\
         (5,29,6,28),(29,18,30,19),(7,30,8,31),(31,21,32,20)]
flype2 = [(3,10,4,11),(11,4,12,5),(13,9,14,8),(9,17,10,16),\
         (17,13,18,12),(19,7,20,6),(21,14,22,15),(15,22,16,23),\
         (1,24,2,25),(25,32,26,1),(23,27,24,26),(27,3,28,2),\
         (5,29,6,28),(29,18,30,19),(7,30,8,31),(31,21,32,20)]

flype_mutation1 =  [ [ 7, 14, 8, 1] , [ 6, 11, 7, 12] , [ 13, 10, 14, 11] , [ 8, 3, 9, 4] ,\
             [ 1, 4, 2, 5] , [ 12, 5, 13, 6] , [ 2, 9, 3, 10] ]
flype_mutation2 =  [ [ 5, 14, 6, 1] , [ 4, 11, 5, 12] , [ 13, 10, 14, 11] , [ 6, 10, 7, 9] ,\
            [ 1, 9, 2, 8] , [ 12, 3, 13, 4] , [ 7, 3, 8, 2] ] 

memoryTest = [[[24, 21, 1, 22], [22, 18, 23, 17], [23, 16, 24, 17], [20, 7, 21, 8],\
              [1, 7, 2, 6], [18, 6, 19, 5], [15, 10, 16, 11], [8, 14, 9, 13], [19, 2, 20, 3],\
              [4, 11, 5, 12], [9, 14, 10, 15], [12, 3, 13, 4]],\
[[17, 24, 18, 1], [21, 16, 22, 17], [23, 14, 24, 15], [18, 8, 19, 7], [1, 7, 2, 6], [20, 5, 21, 6],\
 [15, 22, 16, 23], [13, 8, 14, 9], [19, 3, 20, 2], [11, 4, 12, 5], [9, 12, 10, 13], [3, 10, 4, 11]],\
[[17, 24, 18, 1], [21, 16, 22, 17], [23, 14, 24, 15], [18, 7, 19, 8], [1, 8, 2, 9], [9, 20, 10, 21],\
 [15, 22, 16, 23], [6, 13, 7, 14], [19, 3, 20, 2], [10, 5, 11, 6], [12, 3, 13, 4], [4, 11, 5, 12]],\
[[24, 21, 1, 22], [22, 18, 23, 17], [23, 16, 24, 17], [20, 9, 21, 10], [1, 9, 2, 8], [18, 8, 19, 7],\
 [15, 10, 16, 11], [19, 2, 20, 3], [6, 11, 7, 12], [14, 3, 15, 4], [12, 5, 13, 6], [4, 13, 5, 14]],\
[[11, 24, 12, 1], [7, 10, 8, 11], [8, 23, 9, 24], [12, 18, 13, 17], [1, 17, 2, 16], [6, 15, 7, 16],\
 [22, 9, 23, 10], [18, 22, 19, 21], [13, 3, 14, 2], [14, 5, 15, 6], [19, 5, 20, 4], [20, 3, 21, 4]]]

r3one =  [(1,7,2,6),(24,7,1,8),(5,10,6,11),(4,12,5,11),(9,15,10,14),(8,15,9,16),(13,18,14,19),\
          (12,20,13,19),(2,22,3,21),(3,20,4,21),(17,23,18,22),(16,23,17,24)]
r3two = [(1,7,2,6),(24,7,1,8),(5,10,6,11),(3,13,4,12),(9,15,10,14),(8,15,9,16),(13,18,14,19),\
         (4,19,5,20),(2,22,3,21),(11,21,12,20),(17,23,18,22),(16,23,17,24)]

Kinoshita_Terasaka_K11n42  = [(22,5,1,6),(1,9,2,8),(4,9,5,10),(7,15,8,14),(6,15,7,16),(11,16,12,17),\
                              (12,18,13,17),(2,20,3,19),(13,18,14,19),(3,20,4,21),(10,22,11,21)]
Conway_K11n34 = [(22,5,1,6),(6,12,7,11),(7,12,8,13),(8,14,9,13),(1,15,2,14),(4,15,5,16),(9,19,10,18),\
                 (10,17,11,18),(2,20,3,19),(3,20,4,21),(16,22,17,21)]

missing = [[5, 8, 6, 1], [4, 20, 5, 9], [7, 19, 8, 20], [6, 19, 7, 18],[1, 16, 2, 15], [9, 3, 10, 4],\
           [17, 12, 18, 13], [16, 12, 17, 11], [2, 14, 3, 15], [10, 14, 11, 13]]

#L = snappy.Link('DT: [4,   8, -14,   2,  20, -16,  -6, -18, -12,  22,  10]')
#M = snappy.Link('DT: [4,   8, -14,   2,  -20, 16,  -6, 18, 12,  -22,  -10]')

# Main

def main():
    #createCatalog( "debug case" , {3:[weird3case],8:[labelIssue1],9:[labelIssue2,labelIssue3]} )#,8:[another3,link8],9:[link9],12:[monalisa]}, debug = False )
    #for entry in generateMultiloops( crossings = 13, numComponents = 4, allowReflections = True, primeOnly = True ):
    #    print( "Original PD code:", entry["pd"] )
    #    return
    #    drawnpd = plinkPD( entry["pd"] )
    #    print( "PD code drawn by snappy:", drawnpd )            
    #    print( "Components as calculated from drawn PD code:", pdToComponents( drawnpd )  )
    #    break
               
    #return
    #test12()
    #return
    #for i in range( 2, 7 ):
    #    print( " n =", i, "| Number of multiloops:",  len( generateMultiloops( crossings = i, numComponents = 1, allowReflections = False, primeOnly = False ) ) )
    #    print()
    #return
    #for mloop in irrPrime( 6, loopsOnly = False ):
    #    pd = plinkPD( mloop["pd"] )
    #    print( "input pd", mloop["pd"] )
    #    print( "output pd", pd )
    #    print( "components:", mloop["components"] )
    #    print( "complist:", pdToComponents( pd ) )
    #    print()"""
        
    #print( len( irrPrime( 6, loopsOnly = True ) ) )
    #irrPrime( n = 10 )
    #return
    #monorbigonFig()
    #smallMonorBigonlessPinningSets()

    #saveLoops( [naiveGonalityCounterExample,strongerCounterEx9,strongerCounterEx10,sumCounterEx] )

    #loops = {8:[naiveGonalityCounterExample],10:[missing]}
    #createCatalog( "Debugging some rendering errors in saveLoops", loops, detailTables = True, includeIntro = False )

    #loops = {8:[naiveGonalityCounterExample],9:[strongerCounterEx9],10:[strongerCounterEx10],15:[sumCounterEx]}
    #createCatalog( "Some counterexamples to naive degree conjectures", loops, detailTables = True, includeIntro = False )

    #loops = {9:[flype_mutation1,flype_mutation2]}
    #loops = {16:[flype1,flype2]}
    #createCatalog( "Pinning posets changes drastically under flypes and mutations" , loops )

    #loops={13:[Kinoshita_Terasaka_K11n42, Conway_K11n34]}
    #createCatalog( "Testing mutants" , loops )

    #createCatalog( "Pinning poset changes drastically under Reidemeister III" , {12:[r3one,r3two]} )

    #createCatalog( "Testing memory usage" , {12:memoryTest} )

    #plantriCatalog( 13, 4, numComponents = "any", multiloopPlotThreshold = 12 )
    #plantriCatalog( 9, 9, numComponents = "any", multiloopPlotThreshold = 9, detailTables = True )

    #print( "hi" )
    #smallMonorBigonLessCatalog( 16 )

    #loops = []

    #findMonorbigonLess( 10 )
    #return

    for i in range( 11, 12 ):
        saveLoops( i )
        

def saveLoops( numRegions ):
    counter = 1
    webStr = """    <div class="float">
        <a href="img/loops/{}.svg" title=""><img alt="" src="img/loops/{}.svg" decoding="async" width="100px" height="100px" /></a>
        <span>${}$</span>
    </div>"""
    f = open( "htmloutput.txt", 'w' )
    for loop in generateMultiloops( numRegions, numComponents = 1, includeReflections = False, primeOnly = True )[0]:
        drawnpd = plinkPD( loop.pd )
        G = SurfaceGraphFromPD( drawnpd )
        fullRegList = list( G.wordDict.copy().keys() )
        regLabels = {}
        for i in range( len( fullRegList ) ):
            regLabels[fullRegList[i]] = i+1
        name = str( numRegions )+"_"+str( counter )
        texName = str( numRegions )+"_{"+str( counter )+"}"
        plinkFile = plinkImgFile( str(loop.pd), drawnpd, G.adjDict, G.wordDict,\
                                  [],None,\
                                  regLabels, pdToComponents( drawnpd ), filename = name )
        f.write( webStr.format( name, name, texName )+"\n" )
        counter += 1
    f.close()    
        

def smallMonorBigonLessCatalog( n ):
    data = findMonorbigonLess( n )
    #input( "Ready to create catalog with "+str( data[1])+" entries. Press any key to begin." )
    createCatalog( "Pinning sets of all spherimultiloops with at most $"+str(n)+"$ regions and no monorbigon regions",\
                   data[0], oeisSeq = "A078666")
    

def smallMonorBigonlessPinningSets():
    a = smallMonorbigonLess
    loops = {8:[a[0]],10:[a[1]],11:[a[2]],12:[a[3],a[4],a[5]]}
    print( loops )
    createCatalog( "Pinning sets of all spherimultiloops with at most $12$ regions and no monorbigons" , loops )

def monorbigonFig():
    """Used to generated hte first figure in the paper."""
    loop = [[3, 18, 4, 1], [2, 15, 3, 16], [17, 14, 18, 15], [4, 7, 5, 8],\
            [1, 17, 2, 16], [8, 13, 9, 14], [11, 6, 12, 7], [5, 12, 6, 13], [9, 10, 10, 11]]

    LE = snappy.Link( loop ).view()
    LE.style_var.set('pl')
    LE.set_style()
    for a in LE.Arrows:
    # expose arrows and add in missing segments
        a.expose()

    LE.save_as_svg("monobig.svg")
    LE.done()

    return
    for loop in generateMultiloops( crossings = 9, numComponents = 1, includeReflections = False, primeOnly = False ):
        G = SurfaceGraphFromPD( loop["pd"] )
        moveOn = False
        monogonCount = 0
        bigonCount = 0
        for word in G.wordDict:
            if len( G.wordDict[word] ) == 1:
                monogonCount += 1
            if len( G.wordDict[word] ) == 2:
                bigonCount += 1
            if monogonCount > 1 or bigonCount > 2:
                #print( G.wordDict[word] 
                moveOn = True
                break    
                
        if moveOn:
            continue
        print( loop["pd"] )
        input()
            #print( 
    #findMonorbigonLess()
    #plantriCatalog()

#def saveLoops( loops ):
#    #loops = smallMonorbigonLess
#    counter = 1    
#    for loop in loops:
#        plinkFile = plinkImgFile( str(loop), None, None,\
#                                      [],\
#                                      None, None,\
#                                      None, pdToComponents( loop ), filename = str(loop) )#"monorbigonless"+str(counter))
#        counter += 1

def findMonorbigonLess( n ):
    
    primeOnly = True
    includeReflections = False
    numComponents = "any"
    numLoops = 0
    #n=14
    loops = {}
    for k in range(4, n+1 ):
        loops[k] = []
        for loop in generateMultiloops( k, numComponents = numComponents, includeReflections = includeReflections, primeOnly = primeOnly )[0]:
            #print( loop )
            loops[k].append( loop.pd )
            #break
            #return
        numLoops += len( loops[k] )
        if loops[k] == []:
            del loops[k]

    
    monorbigonLess = {}
    regLabels = {}
    numLoops = 0
    for crossNum in loops:
        #print( "Number of regions:", crossNum )
        counter = 1
        for loop in loops[crossNum]:
            #print( "Checking loop", loop )
            
            #drawnpd = plinkPD( loop )
            G = SurfaceGraphFromPD( loop )
            #print( G )
            #print( G.wordDict )
            moveOn = False
            for word in G.wordDict:
                #print( G.wordDict[word] )
                #input()
                if len( G.wordDict[word] ) < 3:
                    #print( G.wordDict[word] )
                    moveOn = True
                    break
            if moveOn:
                continue
            numLoops += 1
            if crossNum not in monorbigonLess:
                monorbigonLess[crossNum] = [loop]
            else:
                monorbigonLess[crossNum].append( loop )
            continue
            #print( loop )

            #assert( False )
            
            #print( regLabels )
                 #drawnpd = plinkPD( loop )
            drawnpd = plinkPD( loop )
            G = SurfaceGraphFromPD( drawnpd )
            fullRegList = list( G.wordDict.copy().keys() )
            regLabels = {}
            for reg in fullRegList:
                regLabels[reg] = len( G.wordDict[reg] )
            plinkFile = plinkImgFile( str(loop), drawnpd, G.adjDict, G.wordDict,\
                                      [],None,\
                                      regLabels, pdToComponents( drawnpd ), filename = "m_"+str(crossNum)+"_"+str(counter))
            counter += 1
            #monorbigonLess.append( loop )

            #snappy.Link( loop ).view()
    #print( len( monorbigonLess ) )
    
            #input()
    return monorbigonLess, numLoops

def fig1():
    """Plots some pinning sets for a single multiloop (snappy svg)."""
    loop =[[1, 7, 14, 8], [1, 13, 2, 12], [7, 10, 6, 9],\
           [14, 9, 13, 8], [2, 6, 3, 5], [12, 5, 11, 4],\
           [10, 4, 11, 3]]
    drawnpd = plinkPD( loop )
    #print( "drawnpd", drawnpd )
    #print( "multiloop components:", pdToComponents( drawnpd ) )
    #print( "Analyzing loop", counter, "of", len( links[key] ), "..." )
    #counter += 1
    pinSets = getPinSets( drawnpd )#, debug=debug )
    minDict = {}
    
    for elt in pinSets["minPinSets"]:
        if len( elt ) not in minDict:
            minDict[len(elt)] = [elt]
        else:
            minDict[len(elt)].append( elt )

    minlen = min( minDict )
    
    #print( type( pinSets["minPinSets"] ) )
    minsuboptimals = []
    optimals = []
    for elt in pinSets["minPinSets"]:
        if len( elt ) == minlen:
            optimals.append( elt )
        else:
            minsuboptimals.append( elt )
    
    #data[str(link)]["minDict"] = minDict
    #data[str(link)]["graph"] = graph
    
    numOptimal = len( minDict[minlen] )
    numMinimal = len( pinSets["minPinSets"] ) - numOptimal 
    pinSetColors = computeRGBColors( numOptimal, numMinimal )
    minPinSetDict = {}
    label = 1
    for pinset in pinSets["minPinSets"]:
        minPinSetDict[frozenset(pinset)] = {}

    regionLabels = {}
    regList = list( pinSets["fullRegSet"].copy() )
    regList.sort()
    for i in range( len( regList ) ):
        regionLabels[regList[i]] = ""# i+1         
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

        
    plinkFile = plinkImgFile( str(loop), drawnpd, pinSets["G"].adjDict,\
                                      pinSets["G"].wordDict,\
                                      optimals, minPinSetDict,\
                                      regionLabels, pdToComponents( drawnpd ), filename = "opts",\
                                      bufferFrac = 1/10, diamFrac = 1/4)

    plinkFile = plinkImgFile( str(loop), drawnpd, pinSets["G"].adjDict,\
                                      pinSets["G"].wordDict,\
                                      minsuboptimals, minPinSetDict,\
                                      regionLabels, pdToComponents( drawnpd ), filename = "subopts",
                                      bufferFrac = 1/10, diamFrac = 1/4)

    

def plantriCatalog( regmax, regmin, generatePDF = True, includeReflections = False, primeOnly = True, numComponents = "any",
                    multiloopPlotThreshold = None, dbMode = False, detailTables = False):
    #n = 5
    #includeReflections = False #False for UU
    #primeOnly = True
    #numComponents = 2
    n = regmax
    loops = {}
    numLoops = 0
    db = None
    cursor = None
    if dbMode:
        db = mysql.connector.connect( username=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PASS') )
        cursor = db.cursor()
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
            components INT
            )
        """
        
        cursor.execute(create_table)
        
    for k in range(regmin, n+1 ):
        loops[k] = []
        data, seq = generateMultiloops( k, numComponents = numComponents,\
                                        includeReflections = includeReflections, primeOnly = primeOnly,\
                                        db = db, cursor = cursor )
        for loop in data:
            #print( loop["pd"] )
            loops[k].append( loop )
            #break
            #return
        numLoops += len( loops[k] )
        if loops[k] == []:
            del loops[k]
    if generatePDF:
        if numComponents == "any":
            numComponents = "any number of components "
        if numComponents == 1:
            numComponents = "one component "
        else:
            numComponents = str(numComponents)+" components "
        input( "Ready to build catalog with "+str(numLoops)+" entries. Press any key to begin." )
        title = "Pinning set data for all irreducible, indecomposable spherimultiloops with "+numComponents+\
                " and at most "+str(n)+" regions"
        #title = "Weird pinning sets - applying the loop algorithm to multiloops"
        createCatalog( title , loops, oeisSeq=seq, plantriMode = True,\
                       multiloopPlotThreshold = multiloopPlotThreshold, detailTables=detailTables )
    
    
def generateMultiloops( regions, numComponents = 1, includeReflections = False, primeOnly = True, db = None, cursor = None ):
    """Uses the program plantri to generate PD codes of all
    multiloops in the sphere with n crossings, with certain parameters.
    path to plantri folder must be in PATH

    numComponents (positive integer or "any"): Set to 1 to restrict to loops, or 'any' to allow all multiloops

    includeReflections: True iff nonisotopic mirror images considered distinct

    prime: Whether or not to restrict to irreducible, indecomposable ("prime") multiloops (2-connected and no nugatory crossings)"""

    #call(["plantri", str(n+2), "-Goqc2m2d"])
    if numComponents == 1:
        allowMultiloops = False
    else:
        allowMultiloops = True

    case = 4*int( allowMultiloops )+2*int( includeReflections )+1*int( not primeOnly )

    if case == 0: #FFF - UU prime loops, should match https://oeis.org/A264759
        out = check_output(["knotshadow", str(regions), "-m2c2qGd"]).split(b'>>planar_code<<')[1]
        seq = "A264759"
        
    elif case == 1: #FFT - UU prime+composite loops, should match https://oeis.org/A008989
        out = check_output(["knotshadow", str(regions), "-QGd"]).split(b'>>planar_code<<')[1]
        seq = "A008989"
        #warnings.warn( "This case may need debugging - sigma might be wrong" ) # fixed, I think
        
    elif case == 2: #FTF - UO prime loops, should match https://oeis.org/A264760
        out = check_output(["knotshadow", str(regions), "-m2c2qGdo"]).split(b'>>planar_code<<')[1]
        seq = "A264760"
        
    elif case == 3: #FTT - UO prime+composite loops, should match https://oeis.org/A008987
        out = check_output(["knotshadow", str(regions), "-QGdo"]).split(b'>>planar_code<<')[1]
        warnings.warn( "This case may need debugging - sigma might be wrong" )
        seq = "A008987"
        
    elif case == 4: #TFF - UU prime multiloops, should match https://oeis.org/A113201
        out = check_output(["plantri", str(regions), "-Gqc2m2d"]).split(b'>>planar_code<<')[1]
        seq = "A113201"
        
    elif case == 5: #TFT - UU prime+composite multiloops
        out = check_output(["plantri", str(regions), "-Gqd"]).split(b'>>planar_code<<')[1]
        warnings.warn( "This option has not been verified to behave as expected." )
        seq = "unknown"
    
    elif case == 6: #TTF - UO prime multiloops, should match https://oeis.org/A113202
        out = check_output(["plantri", str(regions), "-Gqoc2m2d"]).split(b'>>planar_code<<')[1]
        seq = "A113202"
        
    elif case == 7: #TTT - UO prime+composite multiloops
        out = check_output(["plantri", str(regions), "-Gqdo"]).split(b'>>planar_code<<')[1]
        warnings.warn( "This option has not been verified to behave as expected." )
        seq = "unknown"
        #raise( "Not yet supported" )    
    
    #out = check_output(["plantri", str(n+2), "-Gqoc2m2d"]).split(b'>>planar_code<<')[1] #this get UO irr indecomp
    #out = check_output(["plantri", str(crossings+2), "-Gqc2m2d"]).split(b'>>planar_code<<')[1] #this gets UU irr indecomp
    #out = check_output(["plantri", str(n), "-c1"]).split(b'>>planar_code<<')[1] #this gets UU irr indecomp
    #print( out )
    blocks = out.split(b'\x00')[:-1]
    #print( blocks )
    graphs = []
    first = True
    graph = []
    for i in range( len( blocks ) ): 
        block = blocks[i]
        cycle = []
        if len( block ) == 5:
            if not first:
                graphs.append( graph )
            graph = []
            for byte in block[1:]:
                cycle.append( int( byte ) - 1  )
            graph.append( cycle )
            first = False
        if len( block ) == 4:
            for byte in block:
                cycle.append( int( byte ) - 1 )
            graph.append( cycle )
        if i == len( blocks ) - 1:
            graphs.append( graph )

    #for graph in graphs:
    #    print( graph )
    #return graphs
    # print( len( graphs ), "generated" )
    # return graphs

    multiloops = []
    #countLoops = 0
    
    
    
    #i = 0
    mloopStrings = []
    for graph in graphs:
        #data = planarData( graph, debug = False )
        multiloop = Spherimultiloop( graph )
        if numComponents == "any" or multiloop.components == numComponents:
            #ID = cursor.execute("SELECT LAST_INSERT_ID()")
            #if ID is None:
            #    ID = -1
            #insert_entry = """
            #INSERT INTO mloops (id, pc, pd, sigma, components)
            #VALUES
            mloopStrings.append( """("{}", "{}", "{}", {}),\n""".format(\
                    str( multiloop.plantriCode ), str( multiloop.pd ),\
                    str( multiloop.sigma ), multiloop.components ) )
            #print( insert_entry )
           
            multiloops.append( multiloop )
            #print( i )
            #i+=1
    if mloopStrings != [] and db is not None:        
        insert_entry="""
                INSERT INTO mloops (pc, pd, sigma, components)
                VALUES\n"""
        for mloop in mloopStrings:
            insert_entry += mloop

        print( insert_entry )

        insert_entry = insert_entry[:-2]
        cursor.execute(insert_entry)

    if db is not None:

        db.commit()
            #countLoops += 1
        #     multiloops.append( data )
        #multiloops.append(  )#, loopsOnly ) )
        #data = planarData( graph, loopsOnly )
        #print( graph )
        #print( data["pd"] )
        #print( data["sigma"] )
        #print( data["components"] )
        #if not loopsOnly or data["components"] == 1:
            #countLoops += 1
        #     multiloops.append( data )
        #print()
    #print( countLoops )

    return multiloops, seq
        
    """#print( len( block ) )
    #print( blocks )
    #return
    index= 0
    graphs = []
    while True:
        numVerts = index
        graph = []
        
    for byte in out:
        print( int( byte ) )
    #for g in str( out ).split(">>planar_code<<"):
    #    print( g )
    return
    #print( out )
    graphs = []
    for g in str( out )[2:-1].split("\\n")[:-1]:        
        strRep = g.split()[1].split(",")
        graph = []
        for cycle in strRep:
            toAdd = []
            for char in cycle:
                toAdd.append( ord( char )-97 )
            graph.append( toAdd )            
        graphs.append( graph )
    for g in graphs:
        print( g )"""

def planarData( graph, debug = False ):#, loopsOnly ):
    """Converts a plantri graph to sigma and pd code, and calculates the number of loop components.
       There may be ambiguity if parallel edges,
       so we note from plantri documentation:
       
      In case there are parallel edges, there might be more than one graph
      whose PLANAR CODE is the same up to rotation of the neighbour lists. 
      To resolve this ambiguity, plantri makes the following convention:
      for each vertex v except for the first vertex, if the least numbered
      vertex that has v as a neighbour is w, then the first w in the section
      for v represents the same edge as the first v in the section for w."""

    if graph == [[0,0,0,0]]: #lemniscate is an edge case
        return {"pd":[[1,2,2,1]], "sigma":[[-1,-2,2,1]], "components":1, "plantrigraph":graph}
    if graph == [[1, 1, 1, 1], [0, 0, 0, 0]]: #hopf link is an edge case
        return {"pd":[[1,4,2,3],[3,2,4,1]], "sigma":[[-1,-4,2,3],[-3,-2,4,1]], "components":2, "plantrigraph":graph}
    # this covers all cases of 4 parallel edges
    # but you might have to worry about other edge cases where there are 3 parallel edges
    # then again those may all be NOT irreducible indecomposible
    coordsVisited = 0
    startvert,startpos = 0,3
    curvert,curpos = startvert,startpos

    if debug:
        print( "graph", graph )
        print()

    pdcode = []
    sigma = []
    for i in range( len( graph ) ):
        pdcode.append( ([None]*4).copy() )
        sigma.append( ([None]*4).copy() )
    #sigma = pdcode.copy()

    numComponents = 1
    while True:
        while True:
            nextvert = graph[curvert][curpos]        
            outchoices = [curpos]
            inchoices = []
            for inchoice in range( len( graph[nextvert] ) ):
                if graph[nextvert][inchoice] == curvert:
                    inchoices.append( inchoice )
            if len( inchoices ) == 2:
                for outchoice in range( len( graph[curvert] ) ):
                    if graph[curvert][outchoice] == nextvert and outchoice not in outchoices:
                        outchoices.append( outchoice )
                assert( len( outchoices ) == 2 )
                outchoices.sort()
                inchoices.sort()
                
                lowestNeighborOfCurrent = min( graph[ curvert ] )
                lowestNeighborOfNext = min( graph[ nextvert ] )
                if (lowestNeighborOfCurrent != nextvert and lowestNeighborOfNext != curvert) or curvert==nextvert:#  and
                    #print( "reversing" )
                    inchoices.reverse()
                if outchoices[0] == curpos:
                    nextpos = (inchoices[0]+2)%4
                else:
                    nextpos = (inchoices[1]+2)%4
            else:
                if not ( len( inchoices ) == 1 ):
                    print( graph )
                    input()
                    assert( False )
                nextpos = (inchoices[0]+2)%4

            
            coordsVisited += 1
            pdcode[curvert][curpos] = coordsVisited
            pdcode[nextvert][(nextpos-2)%4] = coordsVisited
            sigma[curvert][curpos] = coordsVisited
            sigma[nextvert][(nextpos-2)%4] = -coordsVisited
            

            if debug:
                print( "curvert:", curvert )
                print( "nextvert:", nextvert )
                print( "inchoices:", inchoices )
                print( "outchoices:", outchoices )
                print( "curpos:", curpos )
                print( "nextpos:", nextpos )
                print( "(nextvert,nextpos)", nextvert, nextpos )
                print( "pd", pdcode )
                print( "sigma", sigma )
                input()
                
            
            curvert,curpos=nextvert,nextpos

            if (nextvert,nextpos) == (startvert,startpos):
                #if coordsVisited == 2*len( graph ):
                #    return {"pd":pdcode, "sigma":sigma, "components":1}
                #else:
                break
                #if loopsOnly:
                #    if coordsVisited == 2*len( graph ):
                #        return {"pd":pdcode, "sigma":sigma, "components":1}
                #    else:
                #        return {"pd":pdcode, "sigma":sigma, "components":-1}
                #else:
                #    break
        if coordsVisited == 2*len( graph ):
            break
        else:        
            found = False
            for i in range( len( pdcode ) ):
                for j in range( len( pdcode[i] ) ):
                    if pdcode[i][j] is None:
                        startvert,startpos = i,j
                        curvert,curpos = startvert,startpos
                        found = True
                        numComponents += 1
                        break
                if found:
                    break

    # to get a consistent pd code (first entry in cycle is always an understrand),
    # try shifting so every cycle starts with a negative
    
    for i in range( len( sigma ) ):
        for firstNegIndex in range( 4 ):
            if sigma[i][firstNegIndex] > 0:
                continue
            else:
                sigma[i] = sigma[i][firstNegIndex:]+sigma[i][:firstNegIndex]
                pdcode[i] = pdcode[i][firstNegIndex:]+pdcode[i][:firstNegIndex]
                break

    if debug:
        print( "pd", pdcode )
        print( "sigma", sigma )
        input()

    #print( "HIHIIHIH" )
    #assert( False )
            
        #for j in range( len( sigma ) ):
        #    if sigma[

    return {"pd":pdcode, "sigma":sigma, "components":numComponents, "plantrigraph":graph}

def pdToComponents( pdcode ):
    """Returns a list of lists of consecutive positive integers each of which
    corresponds to a component of the multiloop represented by pdcode."""
    #print( "pdcode", pdcode )
    coordsDict = coords( pdcode )
    startx,starty = 0,0
    x,y=startx,starty
    curStrand = pdcode[x][y]
    components = []
    visitedCoords = set()
    component = []
    for i in range( 2*len(pdcode) ):
        visitedCoords.add((x,y))
        component.append( curStrand )
        curStrand = pdcode[x][(y+2)%4]
        visitedCoords.add((x,(y+2)%4))
        for coord in coordsDict[curStrand]:
            if (coord[0],coord[1]) != (x,(y+2)%4):
                x,y=coord[0],coord[1]
                break
        if (x,y)==(startx,starty):
            components.append( component )
            component = []
            found = False
            for j in range( len( pdcode ) ):
                for k in range( 4 ):
                    if (j,k) not in visitedCoords:
                        startx,starty=j,k
                        x,y=startx,starty
                        curStrand = pdcode[x][y]
                        found = True
                        break
                if found:
                    break

    #print( "components:", components )

    return components        
        
def coords( pdcode ):
    """Returns a dictionary of coordinates of entries in a pd code."""
    coordsDict = {}
    for i in range( len( pdcode ) ):
        for j in range( 4 ):
            if pdcode[i][j] not in coordsDict:
                coordsDict[ pdcode[i][j] ] = [(i,j)]
            else:
                coordsDict[ pdcode[i][j] ].append((i,j))
    return coordsDict

def test15():
    n = 5
    codes = planarPDcodes( n=n )
    for i in range( len( codes ) ):
        if i in []:
            L = snappy.Link( codes[i] )
            L.view()
        print( codes[i] )

    print( len( codes ) )

    createCatalog( "$n="+str( n )+"$", codes )# skipTrivial = True )

    
def test14():
    n = 8
    for k in range( 1, n ):
        planarPDcodes( n=k )


    return
    
    for k in range( 1, n ):
        numPerfectMatchings = 1
        for i in range( 3, 2*k, 2 ):
            numPerfectMatchings *= i
        #print( numPerfectMatchings )
        num =  2**(k-1)*numPerfectMatchings
        denom = k
        assert( num%denom == 0 )
        #print( "num", num, "denom", denom )
        numpd= 2**(k-1)*numPerfectMatchings//k
        print( numpd )

 

def planarPDcodes( n=7, debug = False ):
    """Returns an exhaustive list of planar PD codes corresponding to
    loops with n crossings,
    each giving a distinct isotopy class. This computation is expensive.
    The computation of orbits under the dihedral group action
    becomes prohibitively slow at n = 7 (~1 minute)"""
    cyclicPerm = Permutation( list( range( 2, 2*n+1, 1 ) )+[1] )
    reflection = Permutation( list( range( 2*n, 0, -1 ) ) )
    D = PermutationGroup([cyclicPerm,reflection])
    #for elt in D:
    #    print( elt )
    #    print( Permutation( elt ).to_cycles() )
    #    print()

    # every perfect match of the complete graph on 2n vertices
    # gives rise to a sigma type
    # match <---> pair of consecutive strands forming a crossing
    # these types are equivalent up to action of the dihedral group on the entries
    # which corresponds to strand relabelings
    orbits = set()
    for match in PerfectMatchings( 2*n ): #matches are sorted lexographically
        # compute the orbit of this match by removing parenthesis,
        # applying the action of the dihedral group
        # adding back parentheses and then resorting
        #print( list( match ) )
        #matchlist = list( match )
        matchlist = []
        matchtuple = []
        for pair in list( match ):
            sortedPair = list( pair )
            sortedPair.sort()
            matchlist += sortedPair
            matchtuple.append( tuple( pair ) )
        matchtuple = tuple( matchtuple )

        orbit = set()

        #print( "Analyzing match:", matchtuple )
        #print( "matchlist:", matchlist )
        #print( "match:",  )
        
        for elt in D:
            perm = Permutation( elt )
            #print( perm )
            #actedOn = perm.action( matchlist )
            actedOn = []
            for item in matchlist:
                actedOn.append( perm( item ) )
            #print( perm.to_cycles(), actedOn )
            actedMatch = []
            for i in range( 0, 2*n, 2 ):
                pairToAdd = actedOn[i:i+2]
                pairToAdd.sort()
                actedMatch.append( tuple( pairToAdd ) )

            
                pass#actedMatch.a

            actedMatch.sort()
            #if tuple( actedMatch ) not in orbit:
            #    pass
            orbit.add( tuple( actedMatch ) )

        orbit = list( orbit )
        orbit.sort()
        orbit = tuple( orbit )

        #if orbit in orbits:
        #    print( "ORBIT FOUND ALREADY, SKIPPING!" )
        orbits.add( orbit )
 
            #assert( False )

        #if tuple( matchlist ) == (frozenset({1, 2}), frozenset({3, 4}), frozenset({5, 6})) or \
        #   tuple( matchlist ) == (frozenset({5, 6}), frozenset({1, 2}), frozenset({3, 4})):

       
        #print( "orbit:" )
        #for elt in orbit:          
        #    print( elt, "eq:", elt == matchtuple )
        #print()

        #print( matchlist )
        #print( type( matchlist ) )
        #print( type( matchlist[0] ) )
        
        #print( match )
        #print( type( match[0] ) )
        #print( type( match ) )
        #print()
        #print( cyclicPerm.action( match ) )

    #for orbit in orbitClasses:
        #print( orbit )
    elts = 0
    reps = []
    #choose one representative from each orbit
    for orbit in orbits:
        #print( "Orbit:" )
        for elt in orbit:
            reps.append( elt )
            #print( elt )
            break
            #print( elt )
        #print()
        elts += len( orbit )
    if debug:
        print( "Crossings (n) =", n )
        print( "Total distinct orbits", len( reps ) )
        print( "Number of elts", elts )
        print( "Expected sigma/PD codes", len( reps )*2**n )

    pddict = {}
    # each rep gives rise to 2**n sigma by choosing the framing at each crossing

    eps = ""
    for i in range( 2*n ):
        eps += str((i+1,4*n-i))
    epsilon = Permutation(eps)
                
    for rep in reps:
        #print( "HI" )
        
        #print()
        codes = []
        for binRep in range( 2**n ):
            pdcode = []
            #binStr = bin( binRep )
            #digits = len( binStr[2:] )
            #binRep = list( bin( binRep )[2:]) +['0']*(n-digits)
            #print( binRep )
            #print( bin( binRep ), end = " " )
            for i in range( n ):
                #print( binRep >> i, end=" " )
                pair=rep[i]
                pair0plus = (pair[0]+1)%(2*n)
                if pair0plus == 0:
                    pair0plus = 2*n
                pair1plus = (pair[1]+1)%(2*n)
                if pair1plus == 0:
                    pair1plus = 2*n
                if (binRep >> i)%2 == 0:                    
                    pdcode.append((pair[0],pair[1],pair0plus,pair1plus))
                else:
                    pdcode.append((pair[0],pair1plus,pair0plus,pair[1]))

            if pdcode in codes:
                #print( pdcode, "at index", codes.index( pdcode ) )
                #print( codes )
                assert( False )

            codes.append( pdcode )

            
            # now compute the ones which have euler characteristic 0 to get a list of all planar sigma

            coordsDict = {}
            for i in range( n ):
                for j in range( 4 ):
                    if pdcode[i][j] not in coordsDict:
                        coordsDict[ pdcode[i][j] ] = [(i,j)]
                    else:
                        coordsDict[ pdcode[i][j] ].append((i,j))

            curCoords = (0,0)

            sig = []
            for entry in pdcode:
                sig.append( list( entry ) )

            #print( "pd:",pdcode )

            while True:
                editCoords = (curCoords[0],(curCoords[1]+2)%4)
                nextEntry = abs( sig[editCoords[0]][editCoords[1]] )
                sig[editCoords[0]][editCoords[1]] *= -1
                if coordsDict[nextEntry][0] == editCoords:           
                    curCoords = coordsDict[nextEntry][1]
                else:
                    curCoords = coordsDict[nextEntry][0]
                #print( nextEntry, curCoords )
                if curCoords == (0,0):
                    break
                #print( sigma )
                #input()
            
            #print( "sig:", sig )

            sigstr = ""

            for i in range( n ):
                toAdd = []
                for j in range( 4 ):
                    if sig[i][j] > 0:
                        toAdd.append( sig[i][j] )
                        
                    else:
                        toAdd.append( sig[i][j]%(4*n)+1 )                        
                sigstr += str(tuple(toAdd))                


            #print( "sigma:",sigma )
            #print( "epsilon:", eps )

            sigma = Permutation(sigstr)
            

            #sigma = Permutation('(9,12,5,2)(7,10,1,4)(11,8,3,6)' )
            #epsilon = Permutation('(1,12)(2,11)(3,10)(4,9)(5,8)(6,7)' )
            phi = ( epsilon*sigma ).inverse()
            chi = len( sigma.to_cycles() ) - len( epsilon.to_cycles() ) + len( phi.to_cycles() )

            error = "None"
            if debug: #this will slow you down dramatically if n>4
                try:
                    snappy.Link( pdcode )
                    if chi != 2:
                        raise( "Snappy should have given an error for this PD code" )
                except ValueError as e: # snappy raises a value error if the link isn't planar
                    #print( e )
                    #traceback.print_exc()
                    #print( "pdcode:", pdcode )
                    #print( "sigma:", sigma.to_cycles() )
                    #print( "sig:", sig )
                    error = "nonplanar"
                    if chi == 2:
                        raise( e )
                    #raise( e )
                except RecursionError as e: # we get this sometimes, even with chi==2, not sure why
                    #print( e )
                    #traceback.print_exc()
                    #print( "pdcode:", pdcode )
                    #print( "sigma:", sigma.to_cycles() )
                    #print( "sig:", sig )
                    error = "recursion"
                    if chi == 2:
                        raise( e )

            #print( coordsDict )
            if debug:
                if chi not in pddict:
                    pddict[chi] = [{"pd":pdcode,"sigma":sigma.to_cycles(),"phi":phi.to_cycles(),\
                                    "epsilon":epsilon.to_cycles(), "sig":sig,"error":error}]
                else:
                    pddict[chi].append( {"pd":pdcode,"sigma":sigma.to_cycles(),"phi":phi.to_cycles(),\
                                    "epsilon":epsilon.to_cycles(), "sig":sig,"error":error} )
            else:
                if chi not in pddict:
                    pddict[chi] = [pdcode]
                else:
                    pddict[chi].append(pdcode)
                    

            #print( pdcode )
            #if pdcode == [(1, 3, 2, 4), (2, 4, 3, 1)] or pdcode == [(1, 4, 2, 3), (2, 4, 3, 1)] or\
            #   pdcode == [(1, 4, 2, 3), (2, 1, 3, 4)]:
            #    continue
            #try:
            #    snappy.Link( pdcode )
            #    pdcodes.append( pdcode )
            #except ValueError: # snappy raises a value error if the link isn't planar
            #    traceback.print_exc()
            #    pass
            
        #print()
        #print( "rep:", rep )
        #print( "pd codes for this rep:" )
        #for code in codes:
        #    print( code )
        #print()

    #print( "pd by euler char" )
    for chi in pddict:
        #print( "chi:", chi, "| num pd codes:", len( pddict[chi]  ) )
        #print( "-------------------------" )
        for pd in pddict[chi]:
            if debug:
                for key in ["sigma","epsilon","phi","pd","error"]:
                    print( " ", key, ":", pd[key] )
                    print()
            else:
                pass#print( pd )
        #print()
        #print( pd )

    return pddict[2]    
    
def test13( n = 1):
    perms = SymmetricGroup( 4*n )
    distinctPerms = set()
    for g in perms:
        rawlist = list( Permutation( g ) )
        #print( rawlist )
        cycString = ""
        for i in range( n ):
            cycString += "("
            cycString += str( rawlist[4*i:4*(i+1)] )[1:-1]
            cycString += ")"
        #print( cycString )
        distinctPerms.add( Permutation( cycString ) )
    print( "Distinct perms:", len( distinctPerms ) )
    for elt in distinctPerms:
        print( elt.to_cycles() )
    print( "Distinct isotopy classes:", len( distinctPerms )/(2*n) )
   
def test12():
    """Creating a catalog of some loops correpsonding to knot in
    the Rolfsen-Thistlethwaite tables"""
    numKnots = 100
    loops = []
    #indices=(0, 491327, 1)
    for K in snappy.AlternatingKnotExteriors( indices = (0,numKnots,1) ):
        name = ""
        for char in K.name():
            if char == "a":
                name += "_"
            else:
                name += char
        
        loops.append( name )

    #print( loops )
    
 
    #toDelete = []

    loops = []
    #loops += [monalisa]
    loops = [ "7_6",link9 , link8 ] #'8_3', '3_1', link8, monalisa, '4_1', '5_1', '9_24']  # the loops to go in the catalog

    skipped = createCatalog( "Test dataset", loops )
    print( "Skipped", skipped, "total knots out of", len(loops), ".")


####################### CREATING PINNING SET CATALOG ####################################

    

def createCatalog( title, links, oeisSeq = "unknown", skipTrivial = False,\
                   debug = False, plantriMode = False, regLabelMode = "none",
                   multiloopPlotThreshold = None, includeIntro = True, detailTables = False ):
    """Create the pdf catalog of loops, their minimal pinning sets, and their minimal join semilattice
    regLabelMode = "numeric" --> regions labeled by numbers
    regLabelMode = "gonality" --> regions labeled by gonality
    regLabelMode = "none" --> don't label regions

    multiloopPlotThreshold is a positive integer representing the max number of regions for which to plot
    including the pinning set data in the tex file (as opposed to simply including it as tabular data).
    If equal to None, tex every multiloop"""

    alldata = {}
    numOptimals = set()
    numMinimals = set()

    skipped = 0
    loopStrings = {}

    for key in links:
        loopStrings[key] = []
        data = {}
        print( "Analyzing", key, "region (multi)loops" )
        counter = 1
        for link in links[key]:
            
            if plantriMode:
                graph = link.plantriCode#["plantrigraph"]
                #data[str(link["pd"])]["graph"] = 
                link = link.pd#["pd"]
            if multiloopPlotThreshold is None\
               or key <= multiloopPlotThreshold:
                drawnpd = plinkPD( link )
            else:
                drawnpd = link
            print( "current link:", link )
            #print( sumCounterEx )
            #input()
            #while True:
            #    drawnpd = plinkPD( link )
            #    break #comment to test the one below
            #    if drawnpd == [(6,4,7,1),(8,2,5,3),(1,5,2,6),(3,7,4,8)]:
            #        break
            print( "drawnpd", drawnpd )
            print( "multiloop components:", pdToComponents( drawnpd ) )
            print( "Analyzing loop", counter, "of", len( links[key] ), "..." )
            counter += 1
            toAdd = getPinSets( drawnpd, debug=debug )        
            if skipTrivial and len( toAdd["minPinSets"] ) == 1:
                print( "Skipping ", link, "because it has a unique minimal pinning set" )
                skipped += 1
                continue
            data[str(link)] = toAdd
            minDict = {}
            for elt in data[str(link)]["minPinSets"]:
                if len( elt ) not in minDict:
                    minDict[len(elt)] = [elt]
                else:
                    minDict[len(elt)].append( elt )
            data[str(link)]["minDict"] = minDict
            if plantriMode:
                data[str(link)]["graph"] = graph
            else:
                data[str(link)]["graph"] = "-"
            minlen = min( minDict )
            numOptimal = len( minDict[minlen] )
            numOptimals.add( numOptimal  )
            numMinimals.add( len( data[str(link)]["minPinSets"] ) - numOptimal )

            pinDict = {}
            for elt in data[str(link)]["pinSets"]:
                if len( elt ) not in pinDict:
                    pinDict[len(elt)] = [elt]
                else:
                    pinDict[len(elt)].append( elt )
            data[str(link)]["pinDict"] = pinDict

            gonalityDict = {}
            regToGonality = {}
            for reg in data[str(link)]["fullRegSet"]:
                regToGonality[reg] = len( binSet( reg ) )
            for elt in data[str(link)]["pinSets"]:
                regs = list( elt )
                regs.sort()
                gonalities = []
                for reg in regs:
                    gonalities.append( regToGonality[reg] )
                isMinimal = ( elt in data[str(link)]["minPinSets"] )
                gonalityDict[frozenset(elt)]={"gons":gonalities,"min":isMinimal}
            data[str(link)]["gonalityDict"] = gonalityDict
            #data[str(link)]["drawnpd"] = drawnpd
        alldata[key] = data
                
    #compute the colors needed for labeling pinning sets
    pinSetColors = computeRGBColors( max( numOptimals ), max( numMinimals ) )

    # delete old image files
    imDir = "tex/img/" # BE CAREFUL, YOU ARE DELETING THIS FOLDER
    try:
        shutil.rmtree( imDir )
    except FileNotFoundError:
        pass
    finally:
        os.makedirs( imDir )

    avgStrings = {}
    data = None

    # dictionary which organizes data by pinning number
    # key = pinning number
    """value = {"count":number with this pinning number,
        "regions":list of crossing numbers,
        "percentagesNeedingPinPinnum:"
        "avgOptimalGonalitiesPinnum":
        "avgMinimalGonalitiesPinnum":
        "avgGonalitiesPinnum":
        """
    pinData = {}


    numloopsByRegion = []
    avgPinNumsByRegion = []
    avgsPercentageNeedingPinByRegion = []
    optgonsByRegion = []
    mingonsByRegion = []
    allgonsByRegion = []

    regTable = [["Number of regions", "Number of multiloops with this number of regions", "Average pinning number",\
                    "Average pinning number/number of regions", "Average optimal pinning set degree",\
                    "Average minimal pinning set degree","Average overall pinning set degree"]]

    pinNumTable = [["Pinning number", "Number of multiloops with this pinning number", "Average number of regions",\
                    "Average pinning number/number of regions", "Average optimal pinning set degree",\
                    "Average minimal pinning set degree","Average overall pinning set degree"]]

    for key in alldata:

        avgOptimalGonalities = []
        avgMinimalGonalities = []
        avgGonalities = []
        pinningNumbers = []
        percentagesNeedingPin = []
    
        for link in alldata[key]:
     
            # build the intro which describes this loop and gives overall stats

            if not "[" in link:
                linkstr = "$"
                for char in link:
                    if char == "_":
                        linkstr += "\\"
                    linkstr += char
                linkstr += "$"
            else:
                linkstr = link
            col1 = ""

            minlen = min( alldata[key][link]["minDict"] )
            numOptimal = len( alldata[key][link]["minDict"][minlen] )
            numMinimal = len( alldata[key][str(link)]["minPinSets"] ) - numOptimal

            col2 = ""
            col1 += "\\noindent\\textbf{Total optimal pinning sets:} "+str(numOptimal) +"\n\n"
            col1 += "\\noindent\\textbf{Total minimal pinning sets:} "+str(numOptimal+numMinimal) +"\n\n"
            col1 += "\\noindent\\textbf{Total pinning sets:} "+str( len( alldata[key][link]["pinSets"] ) )+"\n\n"
            
            
            col1 += "\\noindent\\textbf{Pinning number:} "+str( minlen )+"\n\n"


            numRegions = len( alldata[key][link]["fullRegSet"] )
             
            pinningNumbers.append( minlen )
            percentagesNeedingPin.append( minlen/numRegions )

            #### for organizing by pinning number
            if minlen not in pinData:
                pinData[minlen] = { "count":1,"regions":[key],"percentagesNeedingPinPinNum":[minlen/numRegions],\
                                    "avgOptimalGonalitiesPinNum":[],"avgMinimalGonalitiesPinNum":[],\
                                    "avgGonalitiesPinNum":[] }
            else:
                pinData[minlen]["count"]+=1
                pinData[minlen]["regions"].append(key)
                pinData[minlen]["percentagesNeedingPinPinNum"].append(minlen/numRegions)
            ##########
            
            
            minPinSetDict = {}
            label = 1
            for pinset in alldata[key][link]["minPinSets"]:
                minPinSetDict[frozenset(pinset)] = {}


            # build table of pinning sets and average gonality by cardinal
            rows = [[],[],[],[],[]]
            caption = "Pinning sets/average degree by cardinal"
            rows[0].append( "Cardinal" )
           

            for i in range( minlen, numRegions + 1):
                rows[0].append( str( i ) )
            rows[0].append( "Total" )
            
            rows[1].append( "Optimal pinning sets" )
            rows[1].append( str( numOptimal ) )
            for i in range( minlen+1, numRegions + 1 ):
                rows[1].append( "0" )
            rows[1].append( str( numOptimal ) )

            rows[2].append( "Minimal (suboptimal) pinning sets" )
            tot = 0
            for i in range( minlen, numRegions + 1 ):
                if i != minlen and i in alldata[key][link]["minDict"]:
                    add = len( alldata[key][link]["minDict"][i] )
                    tot += add
                    rows[2].append( str( add ) )
                else:
                    rows[2].append( "0" )
            rows[2].append( str( tot ) )

            rows[3].append( "Nonminimal pinning sets" )
            tot = 0

            for i in range( minlen, numRegions+1 ):
                if i in alldata[key][link]["minDict"]:
                    add = len( alldata[key][link]["pinDict"][i] ) - len( alldata[key][link]["minDict"][i] )
                    tot += add
                    rows[3].append( str( add ) )
                else:
                    add = len( alldata[key][link]["pinDict"][i] )
                    tot += add
                    rows[3].append( str( add ) )
            rows[3].append( str( tot ) )


            rows[4].append( "Average degree" )
            cardDict = {}
            tot = 0
            for elt in alldata[key][str(link)]["gonalityDict"]:
                leng = len( elt  )
                if leng not in cardDict:
                    cardDict[leng] = [alldata[key][str(link)]["gonalityDict"][elt]]
                else:
                    cardDict[leng].append(alldata[key][str(link)]["gonalityDict"][elt] )

            totSum = 0
            minSum = 0
            minCount = 0
            for i in range( minlen, numRegions+1 ):
                avgSum = 0
                for seq in cardDict[i]:
                    avgSum += sum( seq["gons"] )/len( seq["gons"] )
                    if seq["min"]:
                        minCount += 1
                        minSum += sum( seq["gons"] )/len( seq["gons"] )
                add = avgSum/len(cardDict[i])
                if i == minlen:
                    avgOptimalGonality = add
                totSum += avgSum

                rows[4].append( str( round( add, 2 ) ) )
            avgOverallGonality = totSum/len( alldata[key][link]["pinSets"] )
            rows[4].append( "" )
            avgMinGonality = minSum/len( alldata[key][str(link)]["minPinSets"] )
            avgOptimalGonalities.append( avgOptimalGonality )
            avgMinimalGonalities.append( avgMinGonality )
            avgGonalities.append( avgOverallGonality )

            #### for organizing by pinning number
            pinData[minlen]["avgOptimalGonalitiesPinNum"].append( avgOptimalGonality )
            pinData[minlen]["avgMinimalGonalitiesPinNum"].append( avgMinGonality )
            pinData[minlen]["avgGonalitiesPinNum"].append(avgOverallGonality)
            ##########
            
            col2 += "\\noindent\\textbf{Average optimal degree:} "+str( round( avgOptimalGonality, 2 ))+"\n\n"
            col2 += "\\noindent\\textbf{Average minimal degree:} "+str( round( avgMinGonality, 2 ))+"\n\n"
            col2 += "\\noindent\\textbf{Average overall degree:} "+str( round( avgOverallGonality, 2 ))+"\n\n"
            
            tablestrings = [tableString(rows=rows,caption=caption)]

            # build the table of minimal/optimal pinning sets
            rows = []
            caption = "Pinning set data"
            rows.append( ["Pinning set", "Pindicator","Regions","Card",\
                       "Degree seq", "Average degree"] )

            regionLabels = {}
            regList = list( alldata[key][link]["fullRegSet"].copy() )
            regList.sort()
            for i in range( len( regList ) ):
                regionLabels[regList[i]] =  i+1         
            j = 0
            
            col3 = ""
            col3 +=  "\\begin{enumerate}[A)]\n"
            letterLabel = 'A'
            firstTime = True
            sortedKeys = list( alldata[key][link]["minDict"] )
            sortedKeys.sort()
            for key1 in sortedKeys:
                for i in range( len( alldata[key][link]["minDict"][key1] ) ):
                    row = []
                    elt = frozenset( alldata[key][link]["minDict"][key1][i] )
                    #print( elt )
                    if key1 == minlen:
                        dictkey = "opts"
                        colorvar = i
                        numColors = numOptimal
                        specifier = " (optimal)"
                    else:
                        dictkey = "mins"
                        if firstTime:
                            col3 += "\\end{enumerate}\n"
                            col3 += "\\textbf{Minimal (suboptimal) pinning sets:}\n\n"
                            col3 += "\\begin{enumerate}[a)]\n"
                            #rows.append( ["Minimal pinning set","","","","",""] )
                            letterLabel = 'a'
                        firstTime = False
                        colorvar = j
                        numColors = numMinimal
                        specifier = " (minimal)"
                        #elt = data[link]["minPinSets"][i]
                    minPinSetDict[elt]["letterLabel"] = letterLabel
                    row.append( letterLabel+specifier )

                    numTotalColors = len( pinSetColors[dictkey] )    
                    colorIndex = int( colorvar*(numTotalColors/numColors) ) 
                                            
                    minPinSetDict[elt]["label"] = label
                    label += 1
                    minPinSetDict[elt]["color"] = pinSetColors[dictkey][colorIndex]["rgb"]  
                    col3 +=  "\\item{\\Huge\\textcolor{"+pinSetColors[dictkey][colorIndex]["label"]+\
                            "}{\\textbullet}}$\\{"

                    row.append( "{\\Huge\\textcolor{"+pinSetColors[dictkey][colorIndex]["label"]+\
                            "}{\\textbullet}}")

                    regStr = "$\\{"

                    regSort = list( elt )
                    regSort.sort()
                    for reg in regSort:
                        col3 += str( regionLabels[reg] ) +","
                        regStr += str( regionLabels[reg] ) +","

                    col3 = col3[:-1]
                    regStr = regStr[:-1]+"\\}$"
                    row.append( regStr )
                    row.append( str( len( regSort ) ) )
                    row.append( str( alldata[key][str(link)]["gonalityDict"][elt]["gons"] ) )
                    avgGonality = sum( alldata[key][str(link)]["gonalityDict"][elt]["gons"] )/\
                                  len( alldata[key][str(link)]["gonalityDict"][elt]["gons"] )
                    row.append( str( round( avgGonality, 2 ) ) )
                    


                    col3 += "\\}$\n\n"
      
                    if key1 != minlen:
                        j+=1
                    if letterLabel.isupper():
                        letterLabel = alphabet[ (alphabet.index( letterLabel.lower())+1)%len(alphabet) ].upper() # chr(ord(letterLabel) + 1)
                    else:
                        letterLabel = alphabet[ (alphabet.index( letterLabel)+1)%len(alphabet) ]
                    #letterLabel = chr(ord(letterLabel) + 1)
                    rows.append( row )
            col3 +=  "\\end{enumerate}\n"

            tablestrings.append( tableString(rows=rows,caption=caption ) )
            
            #tolerance = 0.0000001
            #print( "Calling saveloop with link=", link, "and drawnpd=", drawnpd, "and components=", pdToComponents( drawnpd ) )
            #input()

            #quick and dirty way to overwrite region labels and label by gonality
            if regLabelMode == "gonality":
                regionLabels = {}
                for reg in alldata[key][link]["fullRegSet"]:
                    regionLabels[reg] = len( alldata[key][link]["G"].wordDict[reg] )
            if regLabelMode == "none" and not detailTables:
                regionLabels = {}
                for reg in alldata[key][link]["fullRegSet"]:
                    regionLabels[reg] = ""
            
            #regionLabels = alldata[key][link]["gonalityDict"]
            #print( regionLabels )

            if multiloopPlotThreshold is None or\
               key <= multiloopPlotThreshold:
            
                plinkFile = plinkImgFile( link, alldata[key][link]["drawnpd"], alldata[key][link]["G"].adjDict,\
                                          alldata[key][link]["G"].wordDict,\
                                          alldata[key][link]["minPinSets"], minPinSetDict,\
                                          regionLabels, pdToComponents( alldata[key][link]["drawnpd"] ), filename = link, debug=debug )
                posetFile = drawLattice( alldata[key][link]["pinSets"], alldata[key][link]["minPinSets"],\
                                         alldata[key][link]["fullRegSet"], minPinSetDict, filename = link )
                if link == str(sumCounterEx):
                    print( "Setting poset file to none" )
                    input()
                    posetFile = None

                loopStrings[key].append( texPinSet(linkstr, col1, col2, tablestrings, plinkFile,\
                                              posetFile, sideBySide = True, imSepPage = True, drawnpd = alldata[key][link]["drawnpd"],\
                                            graph = alldata[key][link]["graph"], detailTable = detailTables  ) )        
    
        optgon = sum( avgOptimalGonalities )/len( alldata[key] )
        mingon = sum( avgMinimalGonalities )/len( alldata[key] )
        allgon = sum( avgGonalities )/len( alldata[key] )
        avgPinNum = sum( pinningNumbers )/len( alldata[key] )
        avgPercentageNeedingPin = sum( percentagesNeedingPin )/len( alldata[key] )

        numloopsByRegion.append( len( alldata[key] ) )
        avgPinNumsByRegion.append( avgPinNum )
        avgsPercentageNeedingPinByRegion.append( avgPercentageNeedingPin )
        optgonsByRegion.append( optgon )
        mingonsByRegion.append( mingon )
        allgonsByRegion.append( allgon )

        

        regTable.append( ["${}$".format( str(key) ), "${}$".format(str( len( alldata[key] ) )), "${:.6g}$".format( avgPinNum ),\
                            "${:.6g}$".format(avgPercentageNeedingPin ), "${:.6g}$".format( optgon ),\
                          "${:.6g}$".format( mingon ), "${:.6g}$".format( allgon ) ] )

        avgStrings[key] = ""
        avgStrings[key] += "\\noindent\\textbf{Number of multiloops with this number of regions in this dataset:} $"\
                           +str( len( alldata[key] ) )+"$\n\n"
        avgStrings[key] += "\\noindent\\textbf{Average pinning number:} $"+str( avgPinNum )+"$\n\n"
        avgStrings[key] += "\\noindent\\textbf{Average pinning number/number of regions:} $"\
                           +str( avgPercentageNeedingPin )+"$\n\n"
        avgStrings[key] += "\\noindent\\textbf{Average optimal pinning set degree:} $"+str( optgon )+"$\n\n"
        avgStrings[key] += "\\noindent\\textbf{Average minimal pinning set degree:} $"+str( mingon )+"$\n\n"
        avgStrings[key] += "\\noindent\\textbf{Average overall pinning set degree:} $"+str(  allgon )+"$\n\n"




    regTableStr = tableString(rows = regTable, caption = "Statistical overview by number of regions (decimals shown to at most $6$ significant figures).")
    
    regNumsSorted = list( alldata.keys() )
    regNumsSorted.sort()

    regNumsFigs = ""
    
    numLoopsFile = linePlot( {"Number of regions":regNumsSorted},\
                            {"Number of multiloops":{"color":"green","values":numloopsByRegion}},\
                             "numRegionsNumloops" )

    
    numRegionsFile = linePlot( {"Number of regions":regNumsSorted},\
                            {"Average pinning number":{"color":"green","values":avgPinNumsByRegion}},\
                             "numRegionsAvgPinNum" )

    percentRegionsFile = linePlot( {"Number of regions":regNumsSorted},\
                            {"Average pinning number/number of regions":\
                             {"color":"green","values":avgsPercentageNeedingPinByRegion}},\
                             "numRegionsAvgsPercentages" )

    #print( "hey" )
    
    gonsFile = linePlot( {"Number of regions":regNumsSorted},\
                            {"Average optimal pinning set degree":\
                             {"color":"red","values":optgonsByRegion},\
                             "Average minimal pinning set degree":\
                             {"color":"green","values":mingonsByRegion},\
                             "Average overall pinning set degree":\
                             {"color":"blue","values":allgonsByRegion}},\
                             "numRegionsGonalities" )


    regNumsFigs += "\\begin{multicols}{2}\n"
    regNumsFigs += "\\begin{figure}[H]\n"+\
           "\\centering\n"+\
           "\\scalebox{0.6}{\\input{"+numLoopsFile+"}}\n"+\
           "\\caption{Number of multiloops by number of regions.}\n"+\
           "\\label{fig:"+numLoopsFile+"}\n\\end{figure}\n"
    regNumsFigs += "\\columnbreak\n\n"
    regNumsFigs += "\\begin{figure}[H]\n"+\
           "\\centering\n"+\
           "\\scalebox{0.6}{\\input{"+numRegionsFile+"}}\n"+\
           "\\caption{Average pinning number by number of regions.}\n"+\
           "\\label{fig:"+numRegionsFile+"}\n\\end{figure}\n"
    regNumsFigs += "\\end{multicols}\n\n"
    regNumsFigs += "\\begin{multicols}{2}\n"
    regNumsFigs += "\\begin{figure}[H]\n"+\
           "\\centering\n"+\
           "\\scalebox{0.6}{\\input{"+percentRegionsFile+"}}\n"+\
           "\\caption{Average pinning number/number of regions by number of regions.}\n"+\
           "\\label{fig:"+percentRegionsFile+"}\n\\end{figure}\n"
    regNumsFigs += "\\columnbreak\n\n"
    regNumsFigs += "\\begin{figure}[H]\n"+\
           "\\centering\n"+\
           "\\scalebox{0.6}{\\input{"+gonsFile+"}}\n"+\
           "\\caption{Average pinning set degree data by number of regions.}\n"+\
           "\\label{fig:"+gonsFile+"}\n\\end{figure}\n"
    regNumsFigs += "\\end{multicols}\n\n"

    

    #### for organizing by pinning number

    #     pinData[minlen] = { "count":1,"crossings":[key],"percentagesNeedingPinPinNum":[minlen/numRegions],\
    #                                "avgOptimalGonalitiesPinNum":[],"avgMinimalGonalitiesPinNum":[],\
    #                                "avgGonalitiesPinNum":[] }

    avgStringsPinNum = {}
    pinNumsSorted = list( pinData.keys() )
    pinNumsSorted.sort()
    numloops = []
    optgons = []
    mingons = []
    allgons = []
    avgsRegions = []
    avgsPercentageNeedingPin = []
    for pinNum in pinNumsSorted:
        numloops.append( pinData[pinNum]["count"] )
        optgon = sum( pinData[pinNum]["avgOptimalGonalitiesPinNum"] )/pinData[pinNum]["count"]
        optgons.append( optgon )
        mingon = sum( pinData[pinNum]["avgMinimalGonalitiesPinNum"] )/pinData[pinNum]["count"]
        mingons.append( mingon )
        allgon = sum( pinData[pinNum]["avgGonalitiesPinNum"] )/pinData[pinNum]["count"]
        allgons.append( allgon )
        avgRegions = sum( pinData[pinNum]["regions"] )/pinData[pinNum]["count"]
        avgsRegions.append( avgRegions )
        avgPercentageNeedingPin = sum( pinData[pinNum]["percentagesNeedingPinPinNum"] )/pinData[pinNum]["count"]
        avgsPercentageNeedingPin.append( avgPercentageNeedingPin )
        avgStringsPinNum[pinNum] = ""
        avgStringsPinNum[pinNum] += "\\noindent\\textbf{Number of multiloops with this pinning number in this dataset:} $"\
                                    +str( pinData[pinNum]["count"] )+"$\n\n"
        avgStringsPinNum[pinNum] += "\\noindent\\textbf{Average number of regions:} $"+str( avgRegions )+"$\n\n"
        avgStringsPinNum[pinNum] += "\\noindent\\textbf{Average pinning number/number of regions:} $"+str( avgPercentageNeedingPin )+"$\n\n"
        avgStringsPinNum[pinNum] += "\\noindent\\textbf{Average optimal pinning set degree:} $"+str( optgon )+"$\n\n"
        avgStringsPinNum[pinNum] += "\\noindent\\textbf{Average minimal pinning set degree:} $"+str( mingon )+"$\n\n"
        avgStringsPinNum[pinNum] += "\\noindent\\textbf{Average overall pinning set degree:} $"+str( allgon )+"$\n\n"

        pinNumTable.append( ["${}$".format( pinNum ), "${}$".format(pinData[pinNum]["count"]), "${:.6g}$".format( avgRegions ),\
                            "${:.6g}$".format(avgPercentageNeedingPin ), "${:.6g}$".format( optgon ),\
                          "${:.6g}$".format( mingon ), "${:.6g}$".format( allgon ) ] )
    pinNumTableStr = tableString(rows = pinNumTable, caption = "Statistical overview by pinning number (decimals shown to at most $6$ significant figures).")

    pinNumsFigs = ""
    
    numLoopsFile = linePlot( {"Pinning number":pinNumsSorted},\
                            {"Number of multiloops":{"color":"green","values":numloops}},\
                             "pinNumsNumloops" )

    
    numRegionsFile = linePlot( {"Pinning number":pinNumsSorted},\
                            {"Average number of regions":{"color":"green","values":avgsRegions}},\
                             "pinNumsAvgsRegions" )

    percentRegionsFile = linePlot( {"Pinning number":pinNumsSorted},\
                            {"Average pinning number/number of regions":\
                             {"color":"green","values":avgsPercentageNeedingPin}},\
                             "pinNumsAvgsPercentages" )

    #print( "hey" )
    
    gonsFile = linePlot( {"Pinning number":pinNumsSorted},\
                            {"Average optimal pinning set degree":\
                             {"color":"red","values":optgons},\
                             "Average minimal pinning set degree":\
                             {"color":"green","values":mingons},\
                             "Average overall pinning set degree":\
                             {"color":"blue","values":allgons}},\
                             "pinNumsGonalities" )

    #print( "hi" )
    pinNumsFigs += "\\begin{multicols}{2}\n"
    pinNumsFigs += "\\begin{figure}[H]\n"+\
           "\\centering\n"+\
           "\\scalebox{0.6}{\\input{"+numLoopsFile+"}}\n"+\
           "\\caption{Number of multiloops by pinning number.}\n"+\
           "\\label{fig:"+numLoopsFile+"}\n\\end{figure}\n"
    pinNumsFigs += "\\columnbreak\n\n"
    pinNumsFigs += "\\begin{figure}[H]\n"+\
           "\\centering\n"+\
           "\\scalebox{0.6}{\\input{"+numRegionsFile+"}}\n"+\
           "\\caption{Average number of regions by pinning number.}\n"+\
           "\\label{fig:"+numRegionsFile+"}\n\\end{figure}\n"
    pinNumsFigs += "\\end{multicols}\n\n"
    pinNumsFigs += "\\begin{multicols}{2}\n"
    pinNumsFigs += "\\begin{figure}[H]\n"+\
           "\\centering\n"+\
           "\\scalebox{0.6}{\\input{"+percentRegionsFile+"}}\n"+\
           "\\caption{Average pinning number/number of regions by pinning number.}\n"+\
           "\\label{fig:"+percentRegionsFile+"}\n\\end{figure}\n"
    pinNumsFigs += "\\columnbreak\n\n"
    pinNumsFigs += "\\begin{figure}[H]\n"+\
           "\\centering\n"+\
           "\\scalebox{0.6}{\\input{"+gonsFile+"}}\n"+\
           "\\caption{Average pinning set degree data by pinning number.}\n"+\
           "\\label{fig:"+gonsFile+"}\n\\end{figure}\n"
    pinNumsFigs += "\\end{multicols}\n\n"
    
    makeTex( title, oeisSeq, avgStrings, regTableStr, avgStringsPinNum, pinNumTableStr,\
             regNumsFigs, pinNumsFigs, loopStrings, pinSetColors, multiloopPlotThreshold, includeIntro )

    #print( "yo" )

    return skipped

def tableString( rows = None, caption = None, num_headers = 1 ):
    
    multi_column_size = []
    c_line = False
    caption = caption
    num_headers = num_headers
    caption_above = True        
    
    return utils.draw_latex(rows, 
                num_headers=num_headers,
                multi_column_size=multi_column_size,
                caption=caption,
                caption_above=caption_above,
                c_line=c_line)

def computeRGBColors( range1, range2 ):

    colors = {"opts":{},"mins":{}}

    startHue = 1
    endHue = 0.2
    step1 = (endHue-startHue)/(range1)
    if range2 != 0:
        step2 = (endHue-startHue)/(range2)
    lightness = 0 # 0 lightest, 1 darkest
    
    for i in range( 0,range1 ):
        colors["opts"][i] = {"label": "red"+str(i),"rgb":(startHue+i*step1,lightness,lightness)}
    for i in range( 0,range2 ):
        colors["mins"][i] = {"label": "green"+str(i), "rgb":(lightness,startHue+i*step2,lightness)}
    return colors    

def makeTex( title, oeisSeq, avgStrings, regTableStr, avgStringsPinNum,\
             pinNumTableStr, regNumsFigs, pinNumsFigs, loopStrings, colors, multiloopPlotThreshold, includeIntro ):
    filename = "tex/pinSets"
    try: # delete old files 
        os.remove(filename+".tex")
        os.remove(filename+".pdf")
    except FileNotFoundError:
        pass
    f = open( filename+".tex", 'w' )
    preamble = "\\documentclass{article}%\n"+\
               "\\usepackage[T1]{fontenc}%\n"+\
               "\\usepackage[utf8]{inputenc}%\n"+\
               "\\usepackage{lmodern}%\n"+\
               "\\usepackage{textcomp}%\n"+\
               "\\usepackage{lastpage}%\n"+\
               "\\usepackage{geometry}%\n"+\
               "\\usepackage{tabularx}%\n"+\
               "\\usepackage{booktabs}%\n"+\
               "\\usepackage[dvipsnames]{xcolor}\n"+\
               "\\usepackage{tikz}\n"+\
               "\\usepackage{tkz-graph}\n"+\
               "\\usepackage{tkz-berge}\n"+\
               "\\usetikzlibrary{arrows,shapes}\n"+\
               "\\usepackage[matrix,arrow,curve,cmtip]{xy}\n"+\
               "\\usepackage{svg}\n"+\
               "\\usepackage{multicol}\n"+\
               "\\usepackage{float}\n"+\
               "\\usepackage{graphicx}\n"+\
               "\\usepackage[shortlabels]{enumitem}\n"+\
               "\\usepackage{hyperref}\n"+\
               "\\usepackage[nottoc,numbib]{tocbibind}\n"+\
               "\\geometry{tmargin=2cm,lmargin=2cm,rmargin=2cm,bmargin=2cm}%\n"+\
               "%\n%\n%\n"
    for color in colors:
        for key in colors[color]:
            preamble += "\\definecolor{"+colors[color][key]["label"]+"}{rgb}{"\
                        +str( colors[color][key]["rgb"][0] ) +\
                        ","+str( colors[color][key]["rgb"][1] )+","+\
                        str( colors[color][key]["rgb"][2] )+"}\n"
    #"\\usepackage{biblatex}\n"+\
    #"\\addbibresource{catalog_ref.bib}\n"+\
    preamble += "%\n%\n%\n"
    preamble += "\\pdfsuppresswarningpagegroup=1\n\n" #surpresses annoying pagegroup warning which triggers on every page of the catalog
    preamble += "\\setcounter{tocdepth}{2}\n\n"
    preamble += "\\title{"+title+"}\n\n"
    preamble += "\\author{Christopher-Lloyd Simon and Ben Stucky}\n\n"
    doc = preamble + "\\begin{document}%\n\n"

    if includeIntro:
        doc += "\\maketitle\n\n"
        intro = open( "tex/catalogIntro.txt", 'r' )
        doc += intro.read().format( title.lower(), oeisSeq, multiloopPlotThreshold ) +"\n\n"
        intro.close()

        doc += "\\tableofcontents\n\n\\newpage\n\n"

        doc += "\n\n\\bibliographystyle{alpha}\n\\bibliography{tex/catalog_ref}\n\n"

        doc += "\\small\n\n"#note the font size change

        doc += "\\newpage\n\n\\section{Statistical overview}\n\\label{sec:stats}\n\n"

        doc += "\\subsection{By number of regions - tabular data}\n\\label{sec:byRegions}\n\n"
        #for key in loopStrings:        
        #    doc += "\\subsection{$"+str(key)+"$ regions}\n\n"+avgStrings[key]+"\n\n"

        doc += regTableStr+"\n\n"

        doc += "\\newpage\n\n\\subsection{By pinning number - tabular data}\n\\label{sec:byPinning}\n\n"

        doc += pinNumTableStr+"\n\n"    

        doc += "\\newpage\n\n\\subsection{By number of regions - graphical data}\n\\label{sec:byNumRegionsGraph}\n\n"\
               + regNumsFigs+"\n\n"    

        #for pinnum in avgStringsPinNum:        
        #    doc += "\\subsection{Pinning number $"+str(pinnum)+"$}\n\n"+avgStringsPinNum[pinnum]+"\n\n"

        doc += "\\newpage\n\n\\subsection{By pinning number - graphical data}\n\\label{sec:byPinningGraph}\n\n"\
               + pinNumsFigs+"\n\n"
            
        doc += "\\newpage\n\n\\section{Spherimultiloops}\n\\label{sec:multiloops}\n\n"

    else:
        doc += "\\section{"+title+"}\n\n"
    for key in loopStrings:
        if includeIntro and ( multiloopPlotThreshold is None or key <= multiloopPlotThreshold ):
            doc += "\\subsection{$"+str(key)+"$ regions}\n\n"
        for loopstring in loopStrings[key]:
            doc += loopstring

    doc += "\n\\end{document}"
    f.write( doc )
    f.close()
    call(['pdflatex', '--shell-escape', '-halt-on-error', '-output-directory', filename.split("/")[0], filename+".tex"])
    #call twice to fix references
    call(['bibtex',filename])
    call(['pdflatex', '--shell-escape', '-halt-on-error', '-output-directory', filename.split("/")[0], filename+".tex"])
    call(['pdflatex', '--shell-escape', '-halt-on-error', '-output-directory', filename.split("/")[0], filename+".tex"]) 
    try:
        #os.remove(filename+".aux")
        #os.remove(filename+".log")
        #os.remove(filename+".toc")
        shutil.rmtree( "svg-inkscape/" )
    except FileNotFoundError:
        pass
    return    

def texPinSet(linkstr, col1, col2, tableStrings, plinkImg, posetImg, sideBySide = True, imSepPage = True, drawnpd = None, graph = None, detailTable = False):
    """Generating and viewing a TeX file illustrating pinning sets"""
    

    doc = "\\subsubsection{"+linkstr+"}\n\n"

    if drawnpd is not None:
        doc += "{\\small\\noindent PD code drawn by \\texttt{SnapPy}: "+str( drawnpd )+"}\n\n"

    if graph is not None:
        doc += "{\\small\\noindent Planar representation generated by \\texttt{plantri}: "+str( graph )+"}\n\n"

    doc += "\\begin{multicols}{2}\n"
    doc += "{\\normalsize "+col1+"}\n"
    doc += "\\columnbreak\n\n"
    doc += "{\\normalsize "+col2+"}\n"
    doc += "\\end{multicols}\n\n"

    doc += tableStrings[0]+"\n\n"
    
    #from sage.misc.latex import latex_examples     
    #foo = latex_examples.diagram()
    #doc += "\n\n"+latex( foo )
    #doc += "\\begin{sdfj}" #deal with a compilation error
    #doc += "\\includesvg[width=30pt]{"+plinkImg+"}\n\n"

    # "\\def\\svgscale{0.7}\n"+\
    
    # "\\input{"+posetImg+"}\n"+\

    if imSepPage:
        pass#doc += "\\newpage\n\n"
    #doc += "\\newpage\n\n"
    #inkscapelatex=false makes it respect the tkinter font size
    #"\\includegraphics[scale=.9]{"+posetImg+"}\n"+\
    if sideBySide:
        doc += "\\begin{multicols}{2}\n"
    doc += "\\begin{figure}[H]\n"+\
           "\\centering\n"+\
           "\\includesvg[inkscapelatex=false,width=250pt]{"+plinkImg+"}\n"+\
           "\\caption{\\texttt{SnapPy} multiloop plot.}\n"+\
           "\\label{fig:"+plinkImg+"}\n\\end{figure}\n"
    if sideBySide:
        doc += "\\columnbreak\n\n"
    if posetImg is not None:
        doc += "\\begin{figure}[H]\n"+\
               "\\centering\n"+\
               "\\scalebox{0.8}{\\input{"+posetImg+"}}\n"+\
               "\\caption{Minimal join sub-semi-lattice of minimal pinning sets.}\n"+\
               "\\label{fig:"+posetImg+"}\n\\end{figure}\n"
    else:
        doc += "The minimal join sub-semi lattice of minimal pinning sets is too large to display."
    if sideBySide:
        doc += "\\end{multicols}\n\n"
   

    

    doc += "\\newpage\n\n"

    if detailTable:     
        doc += tableStrings[1]+"\n\n"
        doc += "\\newpage\n\n"

    return doc

def getUnusedFileName( ext, directory = "./" ):
    """Gets a filename in the specified directory (current directory by default)
    that is not in use with the extension ext"""
    assert( type( ext ) == str )
    assert( type( directory ) == str and directory[-1]=="/" )
    while True:
        filename = directory+str( random() )+"temp."+ext
        try:
            f = open( filename, 'r' )
            f.close()
        except FileNotFoundError:
            break
    return filename

####################### CREATING LATEX LINE PLOTS WITH MATPLOTLIB ####################################
def linePlot( xdata, ydata, filename ):
    """Create latex line graph to be imported with pgf package.
    Uses matplotlib.pyplot
    Assumes xdata = {label:[values]} (has 1 key)
    and ydata = {label:{'color':c,'values':[values]}} (can have many keys)"""
    if filename is None:
        filename = getUnusedFileName( "pgf", "tex/img/" )
    else:
        filename = "tex/img/"+filename[:200]+".pgf"
    plt.rcParams.update({"pgf.texsystem": "pdflatex"})
    fig = plt.figure()
    ax = fig.add_subplot(111)
    #ax2 = plt.figure().gca()
    ax.xaxis.get_major_locator().set_params(integer=True)
    ax.yaxis.get_major_locator().set_params(integer=True)
    
    xkey = getKey(xdata)
    ax.set_xlabel(xkey)
    counter = 0
    ms = 4
    lw = 2
    for key in ydata:        
        counter += 1
        #print( xdata[xkey] )
        #print( ydata[key]['values'] )
        ax.plot(xdata[xkey], ydata[key]['values'], color = ydata[key]['color'],\
                marker = 'o', linestyle ='--', label = key, linewidth=lw, markersize=ms)
        lw *= 0.8
        ms *= 0.8
        #print( counter, key )
    #ax.plot([4,5,6,7,8,9], [8,7,6,5,4,3], 'ro--', label = "Average optimal gonality", linewidth=2, markersize=12)
    #print( "sup2" )
    if len( ydata.keys() ) > 1:
        ax.legend()
    else:
        ax.set_ylabel(getKey(ydata))
    #print( "sup3" )
    plt.savefig(filename, backend='pgf') # save as PGF file which can be used in your document via `\input`
    plt.close()
    return filename


####################### CREATING PINNING POSET WITH SAGE ####################################


def posetPlot( sageObject, heights, colors, vertlabels, edgeColors, filename ):
    """Create latex figure of poset for use with pgf package"""
    p = sageObject.plot( layout = "ranked",\
                         vertex_colors = colors, edge_thickness = 2,
                         edge_style = "-", heights = heights, vertex_labels = vertlabels,
                         edge_colors = edgeColors)
    if filename is None:
        filename = getUnusedFileName( "pgf", "tex/img/" )
    else:
        filename = "tex/img/"+filename[:200]+".pgf"
    #print( filename )

    f = open( filename, 'w' )
    f.write( latex( p ) )
    f.close()
    return filename

    
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg

#trying to convert to tikz
#from matplotlib.backends.backend_pgf import _tex_escape as mpl_common_texification
#import tikzplotlib # fails due to known issue, see https://github.com/nschloe/tikzplotlib/issues/559
#alse see https://stackoverflow.com/questions/52979322/matplotlib-3-0-0-cannot-import-name-get-backend-from-matplotlib
#i haven't tried downgrading matplotlib to 3.6 because I'm afraid it could be break sage
#nevermind i downgraded so the import at works, but it's not doing anything i want it to

"""def posetPlotOld( sageObject, heights, colors, vertlabels, edgeColors, filename ):
    #A workaround function for getting a sage object to show via matplotlib
    #since sageObject.plot() does not produce visible output when run from script
    p = sageObject.plot( layout = "ranked",\
                         vertex_colors = colors, edge_thickness = 2,
                         edge_style = "-", heights = heights, vertex_labels = vertlabels,
                         edge_colors = edgeColors)
    if filename is None:
        filename = getUnusedFileName( "png", "tex/img/" )
    else:
        filename = "tex/img/"+filename+".png"
    #print( filename )

    print( latex( p ) )
    
    p.save( filename )
    img = mpimg.imread( filename )
    plt.imshow(img)
    plt.plot()
    #p.matplotlib()
    #import tikzplotlib
    #print( tikzplotlib.get_tikz_code() )
    #tikzplotlib.save( "test.tex" )
    plt.close()
    #mpl.rcParams.update(mpl.rcParamsDefault)
    #os.remove(filename)
    return filename"""

def drawLattice( pinSets, minPinSets, fullRegSet, minPinSetDict, filename = None ):
    elts, top = minJoinSemilatticeContaining( minPinSets )
    numElts = len( elts )
    #topInd = None
    fullIncluded = ( top == fullRegSet )
    if not fullIncluded:
        eltsDict = {numElts:fullRegSet}
    else:
        eltsDict = {}
    rels = []
    for subset in elts:
        ind = elts.index( subset )
        eltsDict[ind] = frozenset(subset)
        if subset == top and not fullIncluded:
            rels.append([ind,numElts])
    for i in range( numElts-1):
        for j in range( i+1, numElts ):
            if eltsDict[i].issubset( eltsDict[j] ):
                rels.append([i,j])
            if eltsDict[j].issubset( eltsDict[i] ):
                rels.append([j,i])

    #print( eltsDict, rels )

    M = JoinSemilattice((eltsDict, rels))
    #print( M )

    heightsDict = {}
    for elt in M.list():
        try:
            heightsDict[len( eltsDict[elt] )].append( elt )
        except KeyError:
            heightsDict[len( eltsDict[elt] )] = [elt]
    defaultColor = (0.7,0.7,1)
    vertColorsDict = {defaultColor:[]}
    for elt in M.list():
        if eltsDict[elt] in minPinSets:
            if minPinSetDict[eltsDict[elt]]["color"] not in vertColorsDict:
                vertColorsDict[minPinSetDict[eltsDict[elt]]["color"]] = [ elt ]
            else:
                vertColorsDict[minPinSetDict[eltsDict[elt]]["color"]].append( elt )
            #vertColorsDict[minColor].append( elt )
        else:
            vertColorsDict[defaultColor].append( elt )
        
    vertLabels = {}
    lengthsEncountered = set()
    revList = M.list() # reversing to print the cardinality on the rightmost vertex
    revList.reverse()
    for elt in revList:
        leng = len( eltsDict[elt] )
        if leng not in lengthsEncountered:
            vertLabels[elt]=str( leng )
            lengthsEncountered.add( leng )
        
    edgeColorsDict = {}
    #for rel in rels:
    #    pass
    #print( M.hasse_diagram() )
    G = DiGraph( M.hasse_diagram() )

    edgeColors = {}
    #A dictionary specifying edge colors:
    #    each key is a color recognized by matplotlib, and each corresponding value is a list of edges.
    diffs = {0}
    
    for edge in G.edges():
        diff = len( eltsDict[edge[1]] )-len( eltsDict[edge[0]] )
        if diff not in diffs:
            diffs.add( diff )

    #print( diffs )

    maxdiff = max(diffs)

    for edge in G.edges():
        
        diff = len( eltsDict[edge[1]] )-len( eltsDict[edge[0]] )
        #print( edge, eltsDict[edge[1]], eltsDict[edge[0]], diff )
        #print( diff, maxdiff )
        hue = (diff-1)/maxdiff
        rgb = (hue,hue,hue)
        if rgb == (1,1,1):
            raise( "White is a bad color for edges" )
        try:
            edgeColors[rgb].append( edge )
        except KeyError:
            edgeColors[rgb] = [edge]
        
        
        #G.set_edge_label(edge[0], edge[1], "green")
        #edge = (edge[0], edge[1], "blue" )
        #edge[2] = "blue"

    #print( G.edges( labels=True) )

    G = Graph( G )
               
    return posetPlot( G, heightsDict, vertColorsDict, vertLabels, edgeColors, filename=filename )

def minJoinSemilatticeContaining( subsets ):
    """This function takes a set of subsets and computes unions
    to find the minimal join semilattice containing it"""

    fullUnion = set()
    for elt in subsets:
        fullUnion = fullUnion.union( elt )
    #fullIntersection = fullUnion.copy()
    #for elt in subsets:
    #    fullIntersection = fullIntersection.intersection( elt )    

    #print( fullUnion )
    #print( fullIntersection )
    #rels = []

    #def downSets( sets, atoms ):
        #print( "downsets sets:", sets )
    #    if sets == [fullIntersection]:
    #        return None
    #    else:
    #        setsD = []
    #        for elt1 in sets:
    #            for elt2 in atoms:
    #                cap = elt1.intersection( elt2 )
    #                if cap not in setsD:
    #                    setsD.append( cap )
    #        if setsD == sets:
    #            return None
    #        else:
    #            return setsD

    def upSets( sets, atoms ):
        if sets == [fullUnion]:
            return None
        else:
            setsU = []
            for elt1 in sets:
                for elt2 in atoms:
                    cup = elt1.union( elt2 )
                    if cup not in setsU:
                        setsU.append( cup )
            if setsU == sets:
                return None
            else:
                return setsU

    allsets = subsets.copy()
    #nextD = subsets
    nextU = subsets
    while True:        
        #if not (nextD is None):            
        #    for elt in nextD:
        #        if not elt in allsets:
        #            allsets.append( elt )
        #    nextD = downSets( nextD, subsets )
        if not (nextU is None):            
            for elt in nextU:
                if not elt in allsets:
                    allsets.append( elt )
            nextU = upSets( nextU, subsets )
        else:
            break

    return allsets, fullUnion
    
####################### COMPUTING PINSETS ####################################
def testSi( link, pinSet, treeBase = 0, rewriteFrom = 0, verbose = False):
    """Returns si(gamma) relative to all pins, and si(gamma) relative to the pins in pinSet
    using a spanning tree from treeBase and rewriting rule from rewriteFrom"""
    if type( link ) == list:
        G = SurfaceGraphFromPD( link )
    else:
        G = SurfaceGraphFromPD( plinkPD( link ) )
    #print( set( G.wordDict.keys() ) )
    T = G.spanningTree( treeBase )
    T.createCyclicGenOrder()
    gamma = T.genProd()
    unPinSet = set( T.wordDict.copy().keys() ).difference( pinSet )
    rep, newRewriteFrom = T.reducedWordRep( gamma, unPinSet, source = rewriteFrom )
    return {"gamma.si( T.orderDict )":gamma.si( T.orderDict ), \
            "rep.si( T.orderDict )":rep.si( T.orderDict, verbose = verbose ), \
           "rep":rep, "newRewriteFrom":newRewriteFrom, \
            "gamma":gamma, "T.orderDict":T.orderDict, "T.order":T.order}

def getPinSets( link, minOnly = True, debug = False, treeBase = None, rewriteFrom = 0 ):
    """Returns the minimal pinning sets of a link"""

   
    
    if debug:
        #treeBase = 33410
        print( "treeBase:", treeBase )
    
    if type( link ) == list:
        
        G = SurfaceGraphFromPD( link )
        
        pd = link
    else:
        warnings.warn( "Careful..." )
        input()
        pd = plinkPD( link )
        G = SurfaceGraphFromPD( pd )

    

    if debug:
        print( "G:", G )
    
    T = G.spanningTree( baseRegion = treeBase )

    #print( T )

    
    T.createCyclicGenOrder()


    #OLD
    gamma = T.genProd()

    
    
    #print( gamma )
    n = gamma.si( T.orderDict )


    #NEW

    gammaListUnpruned = pdToComponents( pd )
    #print( gammaListUnpruned )
    gammalist = []
    for elt in gammaListUnpruned:
        gamma = []
        for gen in elt:
            if gen in T.adjDict:
                gamma.append( gen )
        gammalist.append( Word( gamma ) )
        #print( gammalist[-1] )
    #print( gammalist )

    intNumbers = {}
    for i in range( len( gammalist ) ):
        for j in range( i, len( gammalist ) ):
            if i == j:
                intNumbers[(i,j)] = gammalist[i].si( T.orderDict )
            else:
                intNumbers[(i,j)] = gammalist[i].I( gammalist[j], T.orderDict )
            if debug:
                print( gammaListUnpruned[i], gammaListUnpruned[j], intNumbers[(i,j)] )

    #print()

    #print( n )
    if debug:
        print( "T:", T )
        print()
    #plink( link )
    #print( T.wordDict )

    fullRegList = list( T.wordDict.copy().keys() )
    #fullRegList.sort()
    #fullRegDict = {}
    monorBigonSet = set()
    if len( pd ) != 1 and not debug: # the lemniscate has a bigon which is not part of pinning set
        # otherwise every monorbigon is part of every pinning set.
        for key in T.wordDict:
            if len( G.wordDict[key] ) <= 2:
                monorBigonSet.add( key )
                #print( "monorbigon found" )
    #print( monorBigonSet )
    #return
    #i=0
    #for key in T.wordDict:
    #    fullRegDict[key]=i
    #    i+=1
    fullRegSet = set( fullRegList )
    numRegions = len( fullRegSet )
        
    #print( fullRegList )
    #print( type( fullRegSet ) )  

    def isPinning( regSet ):
        testRegSet = None
        #testRegSet = {4112,258,33792}
        nonlocal rewriteFrom
        bad = False
        for i in range( len( gammalist ) ):
            for j in range( i, len( gammalist ) ):
                rep1 = T.reducedWordRep( gammalist[i], fullRegSet.difference( regSet ), source = rewriteFrom )[0]
                if i != j:
                    rep2 = T.reducedWordRep( gammalist[j], fullRegSet.difference( regSet ), source = rewriteFrom )[0]
                    intNum = rep1.I( rep2, T.orderDict )
                else:
                    intNum = rep1.si( T.orderDict )
                if debug and regSet == testRegSet:
                    print( "(i,j):", (i,j) )
                    print( "(gamma[i],gamma[j]:", (str(gammalist[i]), str(gammalist[j])) )
                    print( "I(gamma[i],gamma[j]):", intNumbers[(i,j)] )
                    print( "I(gamma[i],gamma[j]) rel testRegSet:", intNum )
                if intNum != intNumbers[(i,j)]:
                    if debug:
                        bad = True
                    else:
                        return False
        if bad:
            return False
        return True
                
        #rep = T.reducedWordRep( gamma, fullRegSet.difference( regSet ), source = rewriteFrom )[0]
        #return rep.si( T.orderDict ) == n        

    pinSets = []
    minPinSets = []
    #numPinSets = 0
    falseMins = {"superset":0,"subset":0 }

    def getPinSetsWithin( regSet, minIndex = 0):
        nonlocal pinSets
        nonlocal minPinSets
        #nonlocal numPinSets
        #nonlocal baseRegion
        #print( regSet, minIndex )
        #print( fullRegSet )
        if regSet != fullRegSet and not isPinning( regSet ):
            return False
        else:
            minimal = True
            nextSet = regSet.copy()
            for i in range( minIndex, numRegions ):
                if fullRegList[i] in monorBigonSet:
                    continue
                nextSet.remove( fullRegList[i] )
                if getPinSetsWithin( nextSet, minIndex = i+1 ):
                    minimal = False
                nextSet.add( fullRegList[i] )
            if minimal:
                superset = False
                #subsetIndices = set()
                newPinsets = []
                for i in range( len( pinSets ) ):
                    if pinSets[i].issubset( nextSet ):
                        superset = True
                        falseMins["superset"] += 1 #just for benchmarking purposes
                        break
                    if debug:
                        #experimentally, this is not needed:
                        if not nextSet.issubset( pinSets[i] ):
                            newPinsets.append( pinSets[i] )

                #experimentally, this is not needed:
                if debug:
                    if len( newPinsets ) != len( pinSets ) and not superset:
                        falseMins["subset"] += 1 #just for benchmarking purposes
                        pinSets = newPinsets                
                
                if not superset:# or not minOnly:
                    #print( "Adding", nextSet )
                    minPinSets.append( nextSet )
            pinSets.append( nextSet )
            #numPinSets += 1
            return True

    """def getPinSetsWithinOld( regSet, minOnly = True, minIndex = 0):
        #print( "hi" )
        print( regSet, minIndex )
        #print( fullRegSet )
        if regSet != fullRegSet and not isPinning( regSet ):
            return set()
        else:
            minsWithin = []
            nextSet = regSet.copy()
            for i in range( minIndex, numRegions ):
                nextSet.remove( fullRegList[i] )
                curmin = getPinSetsWithin( nextSet, minOnly = minOnly, minIndex = i+1 )
                nextSet.add( fullRegList[i] )
                if not curmin:
                    continue

                
                #print( "curmin:", curmin )
                #print()
                
                minimal = True
                for elt in minsWithin:
                    if elt.issubset( curmin ):
                        print( elt, curmin )
                        minimal = False
                if minimal:
                    #print( "Adding", curmin )
                    minsWithin.append( curmin )

                #print( "HELLLOOOO", minsWithin )

            if minsWithin == []:
                print( "regSet", regSet, "is minimal" )
                pinSets.append( nextSet )
                return regSet
            else:
                return minsWithin[0]"""

    def powerSetCheck( powerset ):
        nonlocal rewriteFrom
        """Naive O(exp) function for debugging purposes"""
        pinsets = []
        
        i = 0
        for subset in powerset( fullRegSet ):
            s = set( subset )
            if s == fullRegSet:
                continue
            #rep = T.reducedWordRep( gamma, s, source = rewriteFrom )[0]
            if s != fullRegSet and isPinning( fullRegSet.difference( s ) ):#rep.si( T.orderDict ) == n:
                pinsets.append( fullRegSet.difference( s ) )
            i+=1
        #print( "Total number of subsets:", i )
        return pinsets

    getPinSetsWithin( fullRegSet )#, minOnly = minOnly )

    naivePinSets = None

    if debug:# and not minOnly:
        #getPinSetsWithin( fullRegSet, minOnly = False )
        naivePinSets = powerSetCheck( powerset )
        print( "naivePinSets:", len( naivePinSets ) )
        print( "recursivePinsets:", len( pinSets ) )
        print( "#Naive\\Recursive=", len( difference( naivePinSets, pinSets ) ) )
        print( "#Recursive\\Naive=", len( difference( pinSets, naivePinSets ) ) )
        
        for elt in naivePinSets:        
            assert( elt in pinSets )
            if elt not in pinSets:
                print( elt, "is a naive pinning set but not computed recursively" )
        for elt in pinSets:
            assert( elt in naivePinSets )
            if elt not in naivePinSets:
                print( elt, "is a recursive pinning set but not computed naively" )
        assert( fullRegSet in pinSets )
    #if debug and minOnly:
        print( "Minimal Pinsets:", len( minPinSets ) )
        for i in range( len( minPinSets ) ):
            for j in range( len( minPinSets ) ):
                if i != j:
                    assert( not minPinSets[i].issubset( minPinSets[j] ) )
        #getPinSetsWithin( fullRegSet, minOnly = minOnly )
        #print( "minPinsets:", len( pinSets ) )

    #print( pinSets )
    #print( "False minimals sets:", falseMins )  
            
    #print( pinSets )
    #print()
    #print( naivePinSets )
    #if debug:# and not minOnly:
    #    return pinSets, naivePinSets, minPinSets

    return {"pinSets":pinSets, "naivePinSets":naivePinSets,\
            "minPinSets":minPinSets, "fullRegSet":fullRegSet,\
            "regInfo":G.regionInfo(), "G":G, "drawnpd":pd }
    

####################### DATA STRUCTURES ####################################

class Spherimultiloop:
    """Keeps track of all the data associated to a loop in the sphere,
    given as a PD code or plantri embedding."""

    def __init__( self, plantriCode ):
        self.plantriCode = plantriCode
        self.pd, self.sigma, self.components = self.planarData()
        
    #def __init__( self, pdCode ):
    #    # getting sigma from the pdCode is basically done in Surface Graph
    #    # so that code can be moved here
    #    pass

    def planarData( self ):
        """Converts a plantri graph to sigma and pd code, and calculates the number of loop components.
           There may be ambiguity if parallel edges,
           so we note from plantri documentation:
           
          In case there are parallel edges, there might be more than one graph
          whose PLANAR CODE is the same up to rotation of the neighbour lists. 
          To resolve this ambiguity, plantri makes the following convention:
          for each vertex v except for the first vertex, if the least numbered
          vertex that has v as a neighbour is w, then the first w in the section
          for v represents the same edge as the first v in the section for w."""

        if self.plantriCode == [[0,0,0,0]]: #lemniscate is an edge case
            return [[1,2,2,1]], [[-1,-2,2,1]], 1
        if self.plantriCode == [[1, 1, 1, 1], [0, 0, 0, 0]]: #hopf link is an edge case
            return [[1,4,2,3],[3,2,4,1]], [[-1,-4,2,3],[-3,-2,4,1]], 2
        # this covers all cases of 4 parallel edges
        # but you might have to worry about other edge cases where there are 3 parallel edges
        # then again those may all be NOT irreducible indecomposible
        coordsVisited = 0
        startvert,startpos = 0,3
        curvert,curpos = startvert,startpos


        pdcode = []
        sigma = []
        graph = self.plantriCode
        for i in range( len( graph ) ):
            pdcode.append( ([None]*4).copy() )
            sigma.append( ([None]*4).copy() )
        #sigma = pdcode.copy()

        numComponents = 1
        while True:
            while True:
                nextvert = graph[curvert][curpos]        
                outchoices = [curpos]
                inchoices = []
                for inchoice in range( len( graph[nextvert] ) ):
                    if graph[nextvert][inchoice] == curvert:
                        inchoices.append( inchoice )
                if len( inchoices ) == 2:
                    for outchoice in range( len( graph[curvert] ) ):
                        if graph[curvert][outchoice] == nextvert and outchoice not in outchoices:
                            outchoices.append( outchoice )
                    assert( len( outchoices ) == 2 )
                    outchoices.sort()
                    inchoices.sort()
                    
                    lowestNeighborOfCurrent = min( graph[ curvert ] )
                    lowestNeighborOfNext = min( graph[ nextvert ] )
                    if (lowestNeighborOfCurrent != nextvert and lowestNeighborOfNext != curvert) or curvert==nextvert:#  and
                        #print( "reversing" )
                        inchoices.reverse()
                    if outchoices[0] == curpos:
                        nextpos = (inchoices[0]+2)%4
                    else:
                        nextpos = (inchoices[1]+2)%4
                else:
                    if not ( len( inchoices ) == 1 ):
                        #print( graph )
                        #input()
                        assert( False )
                    nextpos = (inchoices[0]+2)%4

                
                coordsVisited += 1
                pdcode[curvert][curpos] = coordsVisited
                pdcode[nextvert][(nextpos-2)%4] = coordsVisited
                sigma[curvert][curpos] = coordsVisited
                sigma[nextvert][(nextpos-2)%4] = -coordsVisited
                    
                
                curvert,curpos=nextvert,nextpos

                if (nextvert,nextpos) == (startvert,startpos):
                    break
            if coordsVisited == 2*len( graph ):
                break
            else:        
                found = False
                for i in range( len( pdcode ) ):
                    for j in range( len( pdcode[i] ) ):
                        if pdcode[i][j] is None:
                            startvert,startpos = i,j
                            curvert,curpos = startvert,startpos
                            found = True
                            numComponents += 1
                            break
                    if found:
                        break

        # to get a consistent pd code (first entry in cycle is always an understrand),
        # try shifting so every cycle starts with a negative
        for i in range( len( sigma ) ):
            for firstNegIndex in range( 4 ):
                if sigma[i][firstNegIndex] > 0:
                    continue
                else:
                    sigma[i] = sigma[i][firstNegIndex:]+sigma[i][:firstNegIndex]
                    pdcode[i] = pdcode[i][firstNegIndex:]+pdcode[i][:firstNegIndex]
                    break

        return pdcode, sigma, numComponents


class SurfaceGraph:
    """Encodes a local embedding of an ideal graph in a punctured surface S
    via local order of edges around each puncture.
    Methods expect that the graph's edges connect punctures in S
    and that the complement is a disk."""
    
    
    def __init__( self, wordDict, adjDict = None ):
        """Assumes wordDict is dict of integers that can be cast to Words.
        Each Word specifies a cyclic order
        of edge labels encountered around the vertex (key) 
        In case wordDict data comes from a spanning tree of a dual graph to a loop in the plane,
        Raises an assertion error if the there are any isolated vertices.
        If wordDict is a list, will create a dictionary with keys corresponding to list
        indices."""

        # if wordDict is a list, cast to dictionary
        if type( wordDict ) == list:
            wordDict = listToDict( wordDict )
            
        # Create dictionary whose keys are positive indices corresponding to edge labels
        # and values are vertex labels [left, right] encountered when crossing this
        # edge in the positive direction (for orientable surfaces, left is index 0 and right is index 1)
        # For nonorientable surface, this choice is not well-defined, but adjDict still contains the
        # adjacency information

        if adjDict is None:
            self.adjDict = {}
        else:
            self.adjDict = adjDict        
        
        self.wordDict = {}        

        for key in wordDict:
            w = Word( wordDict[ key ] )
            w.cycReduce() # Cyclically reducing all words
            assert( len( w ) > 0 ) # Ruling out isolated vertices
            if adjDict is None:
                for letter in w.seq:
                    try:
                        self.adjDict[ abs( letter ) ] # check if key error
                    except KeyError:
                        self.adjDict[ abs( letter ) ] = [ None, None ]
                    finally:

                        # if this is a new label, put this vertex on left or right according to sign
                        if self.adjDict[ abs( letter ) ] == [ None, None ]:                        
                            self.adjDict[ abs( letter ) ][ not (sign( 0, letter)+1)//2  ] = key

                            # otherwise put it in the left over slot
                        elif self.adjDict[ abs( letter ) ][0] is None:
                            self.adjDict[ abs( letter ) ][0] = key
                        elif self.adjDict[ abs( letter ) ][1] is None:
                            self.adjDict[ abs( letter ) ][1] = key

                            # unless you've seen it twice already
                        else:
                            raise( "An edge label occured more than twice" )
                    
            self.wordDict[key]= w

        # Make sure the adjDict has no remaining None labels:
        for key in self.adjDict:
            assert( self.adjDict[key][0] is not None and self.adjDict[key][1] is not None ) # otherwise you've got hanging edges

        # These attributes are used to store a global cyclic order on generators and their inverses
        # How this is calculated depends on the topology of the graph
        self.order = None
        self.orderDict = None

    def spanningTree( self, baseRegion = None ):
        """Returns a new SurfaceGraph formed from a spanning tree of self.
        Computes tree via dfs from baseRegion"""
       
        if baseRegion is None:
            baseRegion = getKey( self.wordDict )

        #print( baseRegion )

        edgesToKeep = {}

        for edge, vert in self.dfs( curVert = baseRegion, spanningTree = True ):
            edgesToKeep[edge]=None

        adjDict = {}
        for key in self.adjDict:
            try:
                edgesToKeep[key]
                adjDict[key]=self.adjDict[key]
            except KeyError:
                pass

        wordDict = {}
        for key in self.wordDict:
            newWord = []
            for letter in self.wordDict[key].seq:
                try:
                    edgesToKeep[abs(letter)]
                    newWord.append( letter )
                except KeyError:
                    pass
            wordDict[key] = newWord

        return SurfaceGraph( wordDict, adjDict = adjDict )

    def genProd( self ):
        """Returns the word which is the product of all generators
        in the order they are stored in self.adjDict"""
        return Word( list( self.adjDict.keys() ) )       

    def createCyclicGenOrder( self ):
        """This function computes a consistent cyclic order on the set
        of generators and their inverses, if possible.
        Right now it only works as expected in case the graph is a tree
        with a planar embedding whose cyclic orientations at each vertex are consistent with the data given
        (all clockwise or all anticlockwise; else we risk value error or other unexpected behavior at (*) )
        And in this case the cyclic order is found by 'walking around the tree and reading edge labels' """

        order = []
        startVert = getKey( self.wordDict )
        #print( binSet( startVert ) )
        curVert = startVert
        curEdge = self.wordDict[ curVert ].seq[0]
        #while True:
        for i in range( len( self.adjDict )*2 ):
            order.append( curEdge )
            curVert = self.adjDict[ abs( curEdge )  ][ (sign( 0, curEdge )+1)//2 ]
            curWord = self.wordDict[ curVert ].seq
            #print( "curVert:", binSet( curVert ) )
            #print( "curWord:", curWord )
            curEdge = curWord[ ( curWord.index( -curEdge ) + 1 ) % len( curWord ) ] # (*)
            #print( "curorder:", order )
            #print()
            #input()
            #if curVert == startVert:
            #    break

        # Check that we hit every edge twice to know if we are in a tree
        # If graph is disconnected or contains cycles, this is false
        assert( len( order ) == len( self.adjDict )*2 ) # Otherwise this isn't a tree

        #order.reverse() # walking around the tree clockwise vs anticlockwise shouldn't change si
        self.order = order
                
        # to optimize cross function, we create a dictionary that allows us to get the index
        # of an edge or its inverse in O(1) (the information we need to pass to the cross function)
        orderDict = {}
        for i in range( len( self.order ) ):
            orderDict[order[i]]=i
            
        self.orderDict = orderDict

    def reducedWordRep( self, w, filledPunctures, source = 0 ):
        """Given a word w representing a loop in the punctured surface S carrying self
        (so that w is a "cutting sequence" of edges), this method computes a canonical
        reduced representative of w relative to a vertex source in the surface
        with all punctures in the set filledPunctures filled in. The vertex source must not be an element
        of filledPunctures and is taken to be a random such vertex by default.
        Each filled-in puncture gives rise to a simple rewriting rule which eliminates
        one generator (the one corresponding to the edge which is 'upstream' from the vertex
        relative to the source), and the reduced representative is unique up to this choice."""

        assert( type( w ) == Word )
        assert( type( source ) == int )
        #assert( source >= 0 )
        #assert( source < len( self.wordList ) )
        assert( type( filledPunctures ) == set )
        #fillDict = {}
        for puncture in filledPunctures:
            assert( type( puncture ) == int )
            #assert( puncture >= 0 )
            #assert( puncture < len( self.wordList ) )
            #assert( w.seq != puncture )
            #fillDict[ puncture ] = None

        # make sure the source is a key in wordDict
        # but is not in filledPunctures
        choices = set( self.wordDict.keys() ).difference( filledPunctures )
        assert( choices != set() )
        if source not in choices:
            source = getKey( choices )

        #print( "Searching from:", source )
        
        #try:
        #    self.wordDict[source]
        #    print( "0 is a vertex" )
        #except KeyError:
        #    choices = set( self.wordDict.keys() ).difference( filledPunctures )
        #    assert( choices != set() )
        #    source = getKey( choices )
        #print( "hi" )
            

        copyword = w.copy()
        
        for edge, vert in self.dfs( curVert = source ):
            
            if vert in filledPunctures:
                #filledPunctures[ vert ] # skip if KeyError; puncture unfilled
                currWord = self.wordDict[ vert ]           
            
                currInv = ~currWord
                try:
                    ind = currWord.seq.index( edge )
                    word = currWord
                except ValueError:
                    ind = currInv.seq.index( edge )
                    word = currInv

                replWord = ~word.wslice( 0,ind ) / word.wslice( ind+1, len(word) )

                copyword = copyword.simpleRewrite( edge, replWord )
               
            #except KeyError:
            #    pass

        #copyword.freeReduce()
        copyword.cycReduce()
        return copyword, source
    
    def dfs( self, curVert=0, spanningTree = True ):
        """Recursively generates a list of (edge, downsteam vertex) pairs via depth first search from a source vertex,
        where downstream vertex is the endpoint farther from the source,
        visited is a dictionary whose keys are edges that have already been visited, and values
        are terminal vertices to search from. curVert is the current vertex to search from.
        All edges in the resulting list are positive
        Unless spanningTree is set to to False, only returns pairs with edges
        from a spanningTree"""
    
        pairList = []

        try:
            self.wordDict[curVert]
        except KeyError:
            curvert = getKey( self.wordDict )

        def dfsHelper( data, curVert, visitedV, visitedE, spanningTree ):                
            for edge in data.wordDict[ curVert ].seq:
                try:
                    e = abs( edge )
                    visitedE[ e ]
                    # If you made it here, you have seen this edge already
                    # so do nothing
                    continue
                except KeyError:
                    # get the other vertex of e:         
                    otherVert = data.adjDict[ e ][ not data.adjDict[ e ].index( curVert ) ]
                    # if in spanningTree mode, only add the pair
                    # and make a recursive call if the other vertex isn't seen
                    if spanningTree:
                        try:
                            visitedV[ otherVert ]
                            # if you made it here, add this edge
                            # to prevent infinite loop and go next
                            # no recursive call
                            visitedE[ e ] =  None
                            continue                            
                        except KeyError:
                            visitedV[ otherVert ] = None
                            pairList.append(( e, otherVert))
                    else: # otherwise, add the pair unconditionally
                        visitedE[ e ] =  None
                        visitedV[ otherVert ] = None
                        pairList.append(( e, otherVert))
                    # make a recursive call if appropriate
                    dfsHelper( data, otherVert, visitedV, visitedE, spanningTree )
        dfsHelper( self, curVert, {curVert:None}, {}, spanningTree )

        return pairList

    def regionInfo( self ):
        toRet = ""
        for key in self.wordDict:
            toRet += "\\{"+str( binSet(key) )+ "\\} <-----> "+str(key)+"\n\n"
        return toRet
        

    def __str__( self ):
        
        toRet = "Local words around each vertex: \n"
        for key in self.wordDict:
            toRet += str( binSet(key) ) + " ("+str(key)+"): "\
                     + str( self.wordDict[ key ] ) + "\n"
        

        toRet += "\nEdge to [left,right] vertices: {"
        for key in self.adjDict:
            toRet += str( ALPHABET[ key - 1] )+ ": [" \
                + str( binSet( self.adjDict[ key ][0] ) )+", " \
                + str( binSet( self.adjDict[ key ][1] ) )+"], "
        toRet = toRet[:-2]+"}\n\nGlobal cyclic edge order: "
        if self.order is not None:
            toRet += str(Word( self.order ) )
            return toRet
        return toRet + "None computed"             

class Word:
    def __init__( self, seq ):
        """seq is a list nonzero integers.
        The absolute value is the index of the generator and the sign indicates
        \\pm 1 in the exponent"""
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
        """Returns the inverse word (call with ~self)"""
        revseq = []
        for i in range( len( self.seq ) - 1, -1, -1 ):
            revseq.append( -self.seq[i] )
        return Word( revseq ) 

    def __pow__( self, n):
        """Returns self**n"""
        assert( type( n ) == int )
        seq = []
        for i in range( abs( n ) ):
            if n > 0:
                seq += self.seq
            else:
                seq += ~self.seq
        return Word( seq )            

    def wslice( self, i, j, wrap = False ):
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
        return self.wslice( i, i, wrap = True )
    
    def naivePrimitiveRoot( self ):
        """Returns the pair (w, n) such that self = w^n AS FREE WORDS and n is maximal.
        In particular will not find the root of gw^ng^(-1) for nontrivial g"""
        for i in range( 1, len( self )//2+1 ):
            if len( self )%i == 0:
                seg = self.wslice(0,i)
                power = len( self )//i
                if pow( seg, power )==self:
                    return seg, power
        return self.copy(), 1
    
    def si( self, order, bypassCycReduce = True, verbose = False ):
        """Counts self intersections of self with respect to a global cylic order
        EXPECTS INPUT TO BE CYCLICALLY REDUCED
        set bypassCycReduce to True to skip this check"""
        rootself, powself = self.naivePrimitiveRoot()
        I = rootself.I( rootself, order, bypassCycReduce = bypassCycReduce, assumePrimitive = False, verbose = verbose )
        return powself**2*I//2+powself-1
    
    def I( self, other, order, bypassCycReduce = False, assumePrimitive = False, verbose = False ):
        """ Computes the geometric self intersection between self and other relative to
        a global cyclic order on generators and their inverses occuring in the word
        EXPECTS WORDS TO BE CYCLICALLY REDUCED
        set bypassCycReduce to True to skip this check"""        
        # could stand to add more preconditions
        assert( type( order) == dict )
        
        if not bypassCycReduce:
            self.cycReduce()
            other.cycReduce()
        else:
            #warnings.warn( "WARNING: input may not be cyclically reduced")
            pass

        # compute primitive roots by default
        if not assumePrimitive:            
            rootself, powself = self.naivePrimitiveRoot()
            rootother, powother = other.naivePrimitiveRoot()
        else:
            rootself, powself = self, 1
            rootother, powother = other, 1
            warnings.warn( "WARNING: input may not be primitive" )

        if verbose:
            print( "Computing cross/val for each shift of", self, "along", other )
            print( "(powself=", powself, ", powother=", powother, ")" )
            print()
        
        # count intersections of primitive roots
        # can make this faster by skipping ahead if fellow travel is encountered
        # crossValDict = {}
        #indexDict = {}
        primCrossCount = 0
        shiftCount = 0
        i = 0
        while i < len( rootself ):
            j=0
            while j < len( rootother ):
                cross, valplus, valminus = rootself.crossval( rootother, order, i=i, j=j, verbose = verbose)
                val = abs( valplus ) + abs( valminus )
                #indexDict[(i,j)]={"cross":abs(cross),"valplus":abs(valplus),"valminus":abs(valminus)}
                #crossValDict[((i-abs(valminus))%len(rootself),(j-abs(valminus))%len(rootother),\
                #              (i+abs(valplus))%len(rootself),(j+abs(valplus))%len(rootother))] = abs( cross )
                if verbose:
                    print( " cross:", cross, "val:", val )
                    print()
                shiftCount += 1
                primCrossCount += abs( cross )/(1 + val)
                j+= 1#abs( val ) + 1
            i+=1

        if verbose:
            print( "Number of shifts for this computation:", shiftCount )
            print( "primCrossCount=", primCrossCount )
            print()
                
        return round( primCrossCount )*powself*powother

        # Experimenting with skipping ahead to avoid relying on
        # floating point division and get a speedup. It's not working so far.
        # I really don't understand why the crossValDict method here doesn't work
        #count = 0
        #for key in crossValDict:
        #    count += crossValDict[key]

        #return count*powself*powother

        #a smarter attempt (This one should actually be faster, but it's also not working):
            
        for key in indexDict.copy():
            if key in indexDict:
                for i in range( 1, indexDict[key]["valminus"]+1 ):
                    try:
                        del indexDict[((key[0]-i)%len(rootself),(key[1]-i)%len(rootother))]
                    except KeyError:
                        break #continue
                for i in range( 1, indexDict[key]["valplus"]+1 ):
                    try:
                        del indexDict[((key[0]+i)%len(rootself),(key[1]+i)%len(rootother))]
                    except KeyError:
                        break #continue
                if indexDict[key]["cross"] == 0:
                    del indexDict[key]

        count = 0
        for key in indexDict:
            count += indexDict[key]["cross"]

        #return count*powself*powother
        #return len( indexDict.keys() )*powself*powother

        #indexSet = {}
        #for i in range( len( rootself ) ):
        #    for j in range( len( rootother ) ):
        #        try:
                    
        #        indexSet[ (i,j) ] = None       
    
    def crossval( self, other, order, i=0, j=0, verbose = False ):
        """ Words must be cyclically reduced and positive length
        WORDS MUST BE CYCLICALLY REDUCED
        returns (cross, valplus, valminus) triple where cross is -1,0 or 1 (right hand rule from self+ to other+)
        and valplus, valminus are signed lengths of fellow traveling in forward/backward directions
        for convenience, (valplus,valminus) is set to (0,0) if periodisations are identical up to inverses """
        
        assert( len( self ) > 0 and len( other ) > 0 )
        
        # could make this marginally faster by not slicing unless i, j != 0?
        w1plus = self.shift( i )
        w1minus = ~w1plus

        w2plus = other.shift( j )
        w2minus = ~w2plus
        
        # define letters that are relevant to consider, p for positive and n for negative
        p1 = w1plus.seq[0]
        p2 = w2plus.seq[0]
        n1 = w1minus.seq[0]
        n2 = w2minus.seq[0]

        if verbose:
            print( "w1plus:", w1plus, "w1minus:", w1minus )
            print( "w2plus:", w2plus, "w2minus:", w2minus )        

        assert( p1 != n1 and p2 != n2 ) # this would contradict cyclic reduction
        
        initcross1 = cord( order[n1], order[n2], order[p1] )
        initcross2 = cord( order[n1], order[p2], order[p1] )
        initcross = initcross2 - initcross1
        
        if abs( initcross ) == 2: #cross is \pm 1; no fellow traveling
            return sign( 0, initcross ), 0, 0
        
        # otherwise check for fellow traveling
        if p1 == p2 or n1 == n2: # val>0
            plusdata = w1plus.initinfo( w2plus )
            minusdata = w1minus.initinfo( w2minus )
            initcross1 = cord( order[plusdata[1]], order[plusdata[2]], order[plusdata[3]] )
            if initcross1 == 0: #equal periodisations at these indices
                return 0, 0, 0
            #print( "Nontrivial fellow travel" )
            initcross2 = cord( order[minusdata[1]], order[minusdata[2]], order[minusdata[3]] )
            assert( initcross2 != 0 )
            return int( initcross1 == initcross2 ), plusdata[0], minusdata[0]
        if p1==n2 or p2==n1:
        #else: # p1==n2 or p2==n1 #val <0
            plusdata = w1plus.initinfo( w2minus )
            minusdata = w1minus.initinfo( w2plus )
            initcross1 = cord( order[plusdata[1]], order[plusdata[2]], order[plusdata[3]] )
            if initcross1 == 0: #inverse periodisations at these indices
                return 0, 0, 0
            #print( "Nontrivial fellow travel" )
            initcross2 = cord( order[minusdata[1]], order[minusdata[2]], order[minusdata[3]] )
            assert( initcross2 != 0 )
            return -int( initcross1 == initcross2 ), -plusdata[0], -minusdata[0]

        # if here, there is no fellow traveling, and they don't cross
        return 0, 0, 0        
            
    def initinfo( self, other ):
        """given two words, returns data about common initial segments of their periodisations
        as a quadruple (dist, letter1, letter2, letterprev)"""
        
        assert( len( self ) > 0 and len( other ) > 0 ) 
        
        threshold = len( self )+len( other )
        letter1 = self.seq[0]
        letter2 = other.seq[0]
        letterprev = -self.seq[-1] #ensures you return the right thing from crossval
        # if there is no fellow traveling in this direction, but there is in the opposite direction
        length = 0
        
        while letter1 == letter2:
            letterprev = -letter1
            letter1 = self.seq[ (length+1)%len( self ) ]
            letter2 = other.seq[ (length+1)%len( other ) ]
            length += 1
            if length > threshold: # These words share a root, 
                break # letter1 and letter2 will be equal so cross will be 0
        
        return length, letterprev, letter1, letter2

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

    def __eq__( self, other ):
        return self.seq == other.seq

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

####################### SNAPPY PD CODE WORKAROUNDS ####################################

# These functions are failing to capture the general behavior of how snappy messes with PD codes
# I can't figure out the exact relationship between input PD and output PD
def rawPDtoPlinkPD( link ):
    """Gets the PD code for a snappy link that is displayed when
    drawing the link using snappy.plink.
    Input can be a string or a list"""
    #assert( type( link ) == str )
    pd_in = snappy.Link( link ).PD_code()
    edgeLength = len(pd_in)*2
    pd_out = []
    for i in range( len( pd_in ) ):
        cycle = []
        for j in pd_in[i]:
            if j == 1:
                cycle.append( edgeLength )
            else:
                cycle.append( (j-1)%edgeLength )
        pd_out.append( cycle )
    return pd_out

def plinkPDtoRawPD( link ):
    """Gets the raw PD code associated to a plink PD (inverse of function above)"""
    #pd_in = snappy.Link( link ).PD_code()
    assert( type( link ) == list )
    edgeLength = len( link )*2
    pd_out = []
    for i in range( len( link ) ):
        cycle = []
        for j in link[i]:
            if j == edgeLength - 2:
                cycle.append( edgeLength )
            else:
                cycle.append( (j+2)%edgeLength )
        pd_out.append( cycle )
    return pd_out

def plinkPD( link ):
    """This function is a workaround to get the output PD code when plotting links
    with snappy from an input PD code. The reason it does external scripting
    and file I/O is a workaround for a known multithreading issue with snappy."""
    return eval( check_output(['python3', 'plinkpd2.py', str(link) ]) )
    #filename = getUnusedFileName( "txt" )
    #call(['python3', 'plinkpd.py', str(link), filename]) 
    #f = open( filename, 'r' ) # can wait here if plinkpd.py doesn't have enough time to write to file
    #code = eval( f.read() )
    #f.close()
    #os.remove( filename )
    #return code

# The functions below experiment with multithreading rather than subprocess.call
# to deal with the snappy multithreading issue
#from threading import Thread
#from queue import Queue
def plinkPDOld( link ):
    que = Queue()
    thread = Thread( target=lambda q, arg1: q.put( plinkPDHelper( arg1 ) ), args=(que, link ))
    thread.start()
    thread.join()
    code = que.get()
    return code
    #LE = snappy.Link( link ).view()
    #code = LE.PD_code()
    #LE.done()
    #return code

def plinkPDHelper( link ):
    LE = snappy.Link( link ).view()
    code = LE.PD_code()
    #LE.done()
    return code

def plinkFromStr( link ):
    assert( type( link ) == str )
    snappy.Link( link ).view()

def plinkFromPD( link ):
    assert( type( link ) == list )
    snappy.Link( link ).view()

def plinkImgFile( link, drawnpd, adjDict, wordDict, minPinSets,\
                 minPinSetDict, regionLabels, components, tolerance = 0.0000001,\
                  bufferFrac = None, diamFrac = None, filename = None, debug = False ):
    if filename is None:
        filename = getUnusedFileName( "svg", "tex/img/" )
    else:
        filename = "tex/img/"+filename[:200] +".svg"
    words = {}
    for key in wordDict:
        words[key] = wordDict[key].seq
    data = {"link":link,"drawnpd":drawnpd,"adjDict":adjDict,"regWords":words,"minPinSets":minPinSets,\
            "tolerance":tolerance,"minPinSetDict":minPinSetDict,"regionLabels":regionLabels,\
            "components":components,"filename":filename,"debug":debug,\
            "bufferFrac":bufferFrac,"diamFrac":diamFrac}
    call(['python3', 'saveLoop.py', str(data), "padding", "padding", "padding"])
    return filename

# Experimenting with drawing a loop and getting a PD code
# Silly multithreading nonsense makes what's below not work as intended
# Could still experiment with outsourcing to a separate script
#
def drawLoop():
    M = snappy.Manifold()
    #while str( M ) == "Empty Triangulation":
    input( "Draw loop and send to snappy. Press any key when finished." )
    # M.getPDcode() only works in Ben's custom snappy install (modified source code)
    return M.getPDcode()

####################### DATABASE/TRANSLATION FUNCTIONS ####################################

def SurfaceGraphFromPD( pd ):

    #print( pd )
    sigma = pd
    coordsDict = {}
    for i in range( len( sigma ) ):
        for j in range( len( sigma[i] ) ):
            try:
                coordsDict[ sigma[i][j] ].append( [i,j] )
            except KeyError:
                coordsDict[ sigma[i][j] ] = []
                coordsDict[ sigma[i][j] ].append( [i,j] )

    def regionFromCoords( coords ):
        startEdge = sigma[coords[0]][coords[1]]
        reg = [startEdge]
        #print( sigma[coords[0]][coords[1]] )
        while True:
            # depending on PD code convention, may need to
            # subtract or add from index here
            # to match clockwise/counterclockwise convention
            #print( "reg", reg )
            #input()
            curCoords = [(coords[0]),(coords[1]-1)%4]
            nextEdge = sigma[coords[0]][(coords[1]-1)%4 ]
            if nextEdge == startEdge:
                break
            reg.append( nextEdge )
            for cordChoice in coordsDict[nextEdge]:
                #if coords[0] != cordChoice[0]:
                #    coords = cordChoice
                #    break
                if cordChoice != curCoords:
                    coords = cordChoice
                    break
        return reg   

    #create dual graph 
    edgeDict = {}

    #print( pd )
    #print() 
    #print( coordsDict )

    # define left and right relative to the first segment
    # The first left coordinate should be the one which has 2 following in the slot two ahead

    #OLD

    #if coordsDict[1][0][0] == coordsDict[2][0][0] or coordsDict[1][0][0] == coordsDict[2][1][0]:
    #    curLeftCoords = coordsDict[1][0] 
    #    curRightCoords = coordsDict[1][1]
    #else:
    #    curLeftCoords = coordsDict[1][1] 
    #    curRightCoords = coordsDict[1][0]

    #NEW

    comps = pdToComponents( pd )
    regDict = {}
    indexDict = {}

    for comp in comps:
        firstLabel = comp[0]
        secondLabel = comp[1]
        firstOne = coordsDict[firstLabel][0]
        secondOne = coordsDict[firstLabel][1]
        firstTwo = coordsDict[secondLabel][0]
        secondTwo = coordsDict[secondLabel][1]

        if (firstOne[0] == firstTwo[0] and \
             firstOne[1] == (firstTwo[1]+2)%4 ) or \
             ( firstOne[0] == secondTwo[0] and \
               firstOne[1] == (secondTwo[1]+2)%4 ):
            curLeftCoords = firstOne
            curRightCoords = secondOne
        else:
            curLeftCoords = secondOne
            curRightCoords = firstOne

        curLabel = firstLabel

        #print( "First left coordinates:", curLeftCoords )
        #print( "First right coordinates:", curRightCoords )
        #curLeftCoords, curRightCoords = curRightCoords, curLeftCoords
        
        

        for i in range( 1, len( comp )+1 ): # this is the number of segments in the loop component
            # we must check whether regions on left and right of this edge exist yet
            # make a choice for left and right based on the previous

           
            curLeftRegion = regionFromCoords( curLeftCoords )

            
            #print( "hi" )

            #print( "coordsDict:", coordsDict )
            #print( "curLeftCoords:", curLeftCoords )
            
            #print( "curLeftRegion:", curLeftRegion )
            #print()
            #print( "curRighCoords:", curRightCoords )

            curRightRegion = regionFromCoords( curRightCoords )

            #print( "bye" )

            
            leftkey = binHash( curLeftRegion )
            rightkey = binHash( curRightRegion )
            
            try:
                regDict[leftkey]
            except KeyError:
                eltToIndex = {}
                for j in range( len(curLeftRegion) ):
                    eltToIndex[curLeftRegion[j]] = j
                regDict[leftkey] = curLeftRegion
                indexDict[leftkey] = eltToIndex

            try:
                regDict[rightkey][indexDict[rightkey][curLabel]] *= -1 # right region sees this edge negative
            except KeyError:
                eltToIndex = {}
                for j in range( len(curRightRegion) ):
                    eltToIndex[curRightRegion[j]] = j
                regDict[rightkey] = curRightRegion
                indexDict[rightkey] = eltToIndex
                regDict[rightkey][indexDict[rightkey][curLabel]] *= -1
            edgeDict[curLabel] = [ leftkey , rightkey ]

            

            if i == len( comp ):
                break

            #print( "sigma:", sigma )
            #print( "i:", i )
            #print( "[left,right]", [curLeftRegion,curRightRegion] )
            #print( "curLeftCoords:", curLeftCoords )
            #print( "curRighCoords:", curRightCoords )
            #print( "nextfirst:", coordsDict[i+1][1] )
            #print( "nextsecond:", coordsDict[i+1][0] )
            #print("HI")
            #input()
            curLabel = comp[i]
            nextfirst = coordsDict[curLabel][1]
            nextSecond = coordsDict[curLabel][0]

            # OLD        
            #if sigma[curLeftCoords[0]] == sigma[ coordsDict[i+1][1][0] ] or sigma[curRightCoords[0]] == sigma[ coordsDict[i+1][0][0] ]:
            #    curLeftCoords, curRightCoords = coordsDict[i+1][0], coordsDict[i+1][1]
            #else:
            #    curLeftCoords, curRightCoords = coordsDict[i+1][1], coordsDict[i+1][0]

            #NEW
            if ( curLeftCoords[0] == nextfirst[0] and \
                 curLeftCoords[1] == (nextfirst[1]+2)%4 ) or \
                 ( curRightCoords[0] == nextSecond[0] and \
                 curRightCoords[1] == (nextSecond[1]+2)%4 ):
                # sigma[curRightCoords[0]] == sigma[ coordsDict[i+1][0][0] ]:
                curLeftCoords, curRightCoords = nextSecond, nextfirst
            else:
                curLeftCoords, curRightCoords = nextfirst, nextSecond

    return SurfaceGraph( regDict, adjDict = edgeDict )
    
def readPlanarDiagram( knot ):
    """returns the planar diagram presentation of a knot with
    at most 11 crossings from Rolfsen/Hoste/Thistlethwaite tables.
    Knots under eleven crossings should be of the form 'x_y' for integers x
    and y. Knots with eleven crossings should be of the form 'Kxay' or Kxny'
    where the n or a stands for alternating or non-alternating."""
    
    assert( type( knot ) == str )
    notfound = "Knot '"+knot+"' not found in database."
    if ( len( knot ) < 3 ): #could pattern match here to save more time
        warnings.warn( notfound )
        return None 
    try:
        firstLetter = int( knot[0] )
    except ValueError:
        firstLetter = knot[0]
        if firstLetter != 'K': #could pattern match here to save more time
            warnings.warn( notfound )
            return None

    if type( firstLetter ) == int:
        file = 'knotdata/Rolfsen.rdf'
    else:
        file = 'knotdata/Knots11.rdf'

    f = open( file, 'r' )
    key = "<knot:"+knot+">"
    for line in f.readlines():
        data = line.split()[:2]
        if data[0]==key and data[1] == "<invariant:PD_Presentation>":
            f.close()
            data = line.split( "\"")[1].split("sub")
            sigma = []
            for i in range( 1, len( data ), 2 ):
                data[i] = data[i][1:-2]
                if "," in data[i]:
                    toAdd = []
                    for elt in data[i].split( "," ): 
                        toAdd.append( int( elt ) )
                    assert( len( toAdd ) == 4 )
                    sigma.append( toAdd )
                else:
                    toAdd = []
                    for elt in data[i]:
                        toAdd.append( int( elt ) )
                    assert( len( toAdd ) == 4 )
                    sigma.append( toAdd )
            
            return sigma
    f.close()
    warnings.warn( notfound )
    return None

####################### OTHER GENERALLY USEFUL FUNCTIONS ####################################

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

def binHash( distinctNatList ):
    """Given a list A of distinct nonnegative integers, computes a large integer
    which encodes the elements present and serves as a hash key for the
    corresponding set of naturals+0
    WILL NOT WORK PROPERLY IF GIVEN LISTS OF NONDISTINCT INTEGERS."""

    hashkey = 0
    for elt in distinctNatList:
        hashkey += 2**elt
    return hashkey

def binSet( num ):
    """Returns set of indices where a binary number is nonzero"""
    indexSet = set()
    i = 0
    while num != 0:
        if num%2 != 0:
            indexSet.add( i )
        i += 1
        num >>= 1
    return indexSet    

def listToDict( a ):
    """Converts list to dictionary"""
    toRet = {}
    for i in range( len( a ) ):
        toRet[i] = a[i]
    return toRet

def getKey( a ):
    """Returns some key from a dictionary/set, or None if the dict/set is empty"""
    for key in a:
        return key
    return None

####################### FUNCTIONS WHICH SHOULD ONLY BE USED FOR DEBUGGING ####################################

def intersection( list1, list2 ):
    """Returns a list of all elements from list1 and list2"""
    toReturn = []
    for elt in list1:
        if elt in list2 and not elt in toReturn:
            toReturn.append( elt )
    return toReturn

def union( list1, list2 ):
    """Returns a list of elements from list1 or list2"""
    toReturn = []
    for elt in list1:
        if not elt in toReturn:
            toReturn.append( elt )
    for elt in list2:
        if not elt in toReturn:
            toReturn.append( elt )
    return toReturn
    

def difference( list1, list2 ):
    """Returns a list of all elements in list1 and not in list2"""
    toReturn = []
    for elt in list1:
        if not elt in list2 and not elt in toReturn:
            toReturn.append( elt )
    return toReturn

def isSubset( list1, list2 ):
    """Returns True if and only if every element of list1 is in list2"""
    return len( difference( list2, list1 ) ) == len( list2 ) - len( list1 )

from itertools import chain, combinations
def powerset(iterable):
    """
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    stolen from https://stackoverflow.com/questions/374626/how-can-i-find-all-the-subsets-of-a-set-with-exactly-n-elements
    for a 'naive check' of the pinset function
    """
    xs = list(iterable)
    # note we return an iterator rather than a list
    return chain.from_iterable(combinations(xs,n) for n in range(len(xs)+1))

####################### OLD/COMPLETED TESTS ####################################
def test10():
    """Another function to compute pinning sets of drawn loops"""

    #link = 'K14a4'
    #mona lisa loop:
    link = [(24, 6, 1, 5), (3, 10, 4, 11), (1, 13, 2, 12), \
            (6, 14, 7, 13), (2, 17, 3, 18), (8, 15, 9, 16), \
            (11, 19, 12, 18), (4, 20, 5, 19), (7, 23, 8, 22),\
            (9, 20, 10, 21), (14, 24, 15, 23), (16, 21, 17, 22)]
    # 8 crossing loop with no embedded monorbigons
    #link = [(1, 7, 2, 6), (3, 8, 4, 9), (5, 11, 6, 10), (16, 12, 1, 11), \
    #        (2, 13, 3, 14), (4, 16, 5, 15), (7, 12, 8, 13), (9, 15, 10, 14)]
    # another equivalent one:
    #link = [(11,16,12,1),(13,3,14,2),(8,4,9,3),(15,4,16,5),(10,5,11,6),(1,7,2,6),(12,8,13,7),(9,15,10,14)]

    # a 9 crossing example; cycle 0, 1 and 4 times to see small discrepancy
    #link = [(1, 7, 2, 6), (4, 9, 5, 10), (2, 12, 3, 11),\
    #        (7, 13, 8, 12), (18, 13, 1, 14), (3, 17, 4, 16),\
    #        (5, 14, 6, 15), (8, 18, 9, 17), (10, 15, 11, 16)]

    drawnpd = plinkPD( link )
    
    # do this cycling to make sure pinset behavior is preserved for different PD codes
    offset = 0
    for i in range( offset ):
        link = drawnpd
        drawnpd = plinkPD( drawnpd )

    minOnly = True
    debug = True
    pinsets = pinSets( drawnpd, debug = debug, minOnly = minOnly )
    if minOnly:
        print( "Minimal pinning sets:" )
    minlen = len( pinsets[0] )
    for elt in pinsets[0]:
        if minOnly or debug:
            print( elt )
        if len( elt ) < minlen:
            minlen = len( elt )
    #print( "MinOnly:", minOnly )
    print()
    if minOnly:
        print( "Number of minimal pinning sets:", len( pinsets[0] ) )
    print( "Number of total pinning sets:", pinsets[1] )
    print( "Pinning number:", minlen )
    print()
    print( "Input PD:", link )
    print( "Drawn PD:", drawnpd )
    #plinkFromPD( link )

def test9():
    """Debugging the 9-crossing loop having different behavior for different spanning trees"""
    # a 9 crossing example; cycle 0, 1 and 4 times to see small discrepancy
    link = [(1, 7, 2, 6), (4, 9, 5, 10), (2, 12, 3, 11),\
            (7, 13, 8, 12), (18, 13, 1, 14), (3, 17, 4, 16),\
            (5, 14, 6, 15), (8, 18, 9, 17), (10, 15, 11, 16)]
    drawnpd = plinkPD( link )

    print( "Input PD:", link )
    print( "Drawn PD:", drawnpd )

    # For debugging 9-crossing monorbigon-free example with PD_offset 0
    # toggle between baseRegion = 16898 ( naivePinSets: 374, recursivePinsets: 347 )
    # and baseRegion = 270864 ( naivePinSets: 395, recursivePinsets: 395 )
    base1 = 16898
    base2 = 270864
    # base2 is the infinite region, so we always try to rewrite from there
    # however the answer should not depend on spanning tree (specified by treeBase)
    print( "All pinsets rel treeBase=", base1, ":" )
    allpinsets1, naive1 = pinSets( drawnpd, debug = True, minOnly = False, treeBase = base1, rewriteFrom = base2 )
    print()
    
    print( "All pinsets rel treeBase=", base2, ":" )
    allpinsets2, naive2 = pinSets( drawnpd, debug = True, minOnly = False, treeBase = base2, rewriteFrom = base2 )
    print()
    
    print( "Min pinsets rel treeBase=", base1, ":" )
    minpinsets1 = pinSets( drawnpd, debug = True, minOnly = True, treeBase = base1, rewriteFrom = base2 )[0]
    print()
    
    print( "Min pinsets rel treeBase=", base2, ":" )
    minpinsets2 = pinSets( drawnpd, debug = True, minOnly = True, treeBase = base2, rewriteFrom = base2 )[0]
    print()

    print( "Min1 is subset All1?", isSubset( minpinsets1, allpinsets1 ) )
    print( "Min2 is subset All2?", isSubset( minpinsets2, allpinsets2 ) )
    print( "All1 is subset Naive1?", isSubset( allpinsets1, naive1 ) )
    print( "All2 is subset Naive2?", isSubset( allpinsets2, naive2 ) )
    print( "All1 cap Min2 is a subset of Min1", isSubset( intersection( allpinsets1, minpinsets2), minpinsets1 ) )
    print( "#Naive1\\(Min2 cup All1)", len( difference( naive1, union( minpinsets2, allpinsets1 ) ) ) )
    print( "#All1\\Naive1", len( difference( allpinsets1, naive1 ) ) )
    print( "#Naive1\\All1", len( difference( naive1, allpinsets1 ) ) )
    print( "#Min1\\#Min2:", len( difference( minpinsets1, minpinsets2 ) ) )
    print( "#Min2\\#Min1:", len( difference( minpinsets2, minpinsets1 ) ) )
    print( "#Min2\\#All1:", len( difference( minpinsets2, allpinsets1 ) ) )
    print( "#Min2\\#Naive1:", len( difference( minpinsets2, naive1 ) ) ) 

    print( "Discrepancies follow..." )
    print()

    badcount = 0
    for elt in naive2:
        # base2 is the infinite region, so we always try to rewrite from there
        dataBase1 = testSi( drawnpd, elt, treeBase = base1, rewriteFrom = base2 )
        dataBase2 = testSi( drawnpd, elt, treeBase = base2, rewriteFrom = base2 )
        #return {"gamma.si( T.orderDict )":gamma.si( T.orderDict ), \
        #    "rep.si( T.orderDict )":rep.si( T.orderDict ), \
        #   "rep":rep, "newRewriteFrom":newRewriteFrom, \
        #    "gamma":gamma, "T.orderDict":T.orderDict, "T.order":T.order}
        if dataBase1["gamma.si( T.orderDict )"] != dataBase1["rep.si( T.orderDict )"]\
           or dataBase2["gamma.si( T.orderDict )"] != dataBase2["rep.si( T.orderDict )"]:
            testSi( drawnpd, elt, treeBase = base1, rewriteFrom = base2, verbose = True )
            testSi( drawnpd, elt, treeBase = base2, rewriteFrom = base2, verbose = True )

            
            print( "Considering pinset:", elt, "(size", len(elt), ")" )
            print()
            print( "  Relative to treeBase=", base1, " and rewriteFrom=", dataBase1["newRewriteFrom"], " we have:" )
            print( "  gamma=", dataBase1["gamma"] )
            print( "  gamma(pinset,rewriteFrom)=", dataBase1["rep"] )
            print( "  si(gamma,{},rewriteFrom)=", dataBase1["gamma.si( T.orderDict )"],\
                   ",\tsi(gamma,pinset,rewriteFrom)=", dataBase1["rep.si( T.orderDict )"] )
            print( "  T(treeBase).orderDict=", dataBase1["T.orderDict"] )
            print( "  T(treeBase).order=", Word(dataBase1["T.order"]) )
            
            if base2 != dataBase1["newRewriteFrom"]:
                print( "  rewriteFrom=", base2, "was to be filled, so it was modified as above." )
    
            print()
            print( "  Relative to treeBase=", base2, " and rewriteFrom=", dataBase2["newRewriteFrom"], " we have:" )
            print( "  gamma=", dataBase2["gamma"] )
            print( "  gamma(pinset,rewriteFrom)=", dataBase2["rep"] )
            print( "  si(gamma,{},rewriteFrom)=", dataBase2["gamma.si( T.orderDict )"],\
                   ",\tsi(gamma,pinset,rewriteFrom)=", dataBase2["rep.si( T.orderDict )"] )
            print( "  T(treeBase).orderDict=", dataBase2["T.orderDict"] )
            print( "  T(treeBase).order=", Word(dataBase2["T.order"]) )
            if base2 != dataBase2["newRewriteFrom"]:
                print( "  rewriteFrom=", base2, "was to be filled, so it was modified as above." )
            
            print()
            badcount += 1
       
        #if :
        #    print( "Considering pinset:", elt )
            
        #    print()
        #    badcount += 1
    print( "Total discrepancies:", badcount )
    #print( "\nPinning sets in second not in first:" )
    #for elt in difference( pinsets2, pinsets1 ):
    #    print( "Considering pinset:", elt )
    #    print( "Relative to", base1, "we have", testSi( drawnpd, elt, baseRegion = base1 ) )
    #    print( "Relative to", base2, "we have", testSi( drawnpd, elt, baseRegion = base2 ) )
    #    print()

    return
    
    print( "Pinning sets in first not in second:" )
    for elt in difference( pinsets1, pinsets2 ):
        print( "Considering pinset:", elt )
        print( "Relative to", base1, "we have", testSi( drawnpd, elt, baseRegion = base1 ) )
        print( "Relative to", base2, "we have", testSi( drawnpd, elt, baseRegion = base2 ) )
        print()
    print( "\nPinning sets in second not in first:" )
    for elt in difference( pinsets2, pinsets1 ):
        print( "Considering pinset:", elt )
        print( "Relative to", base1, "we have", testSi( drawnpd, elt, baseRegion = base1 ) )
        print( "Relative to", base2, "we have", testSi( drawnpd, elt, baseRegion = base2 ) )
        print()

    # grab the pinset of size 4 that pins loop 2 but not loop 1
    #special = difference( pinsets2, pinsets1 )[1]
    #print(  )

    # double check that it doesnt pin loop1

def test8():
    """Demonstrates/tests for PD code discrepancy (originally with the Mona Lisa loop and 9 crossing loop.)
    Also illustrates 'correct' use of which PD to feed to snappy
    vs our algorithm"""


    #link = 'K14a4'
    #mona lisa loop:
    link = [(24, 6, 1, 5), (3, 10, 4, 11), (1, 13, 2, 12), \
            (6, 14, 7, 13), (2, 17, 3, 18), (8, 15, 9, 16), \
            (11, 19, 12, 18), (4, 20, 5, 19), (7, 23, 8, 22),\
            (9, 20, 10, 21), (14, 24, 15, 23), (16, 21, 17, 22)]
    # 8 crossing loop with no embedded monorbigons
    link = [(1, 7, 2, 6), (3, 8, 4, 9), (5, 11, 6, 10), (16, 12, 1, 11), \
            (2, 13, 3, 14), (4, 16, 5, 15), (7, 12, 8, 13), (9, 15, 10, 14)]
    # another equivalent one:
    #link = [(11,16,12,1),(13,3,14,2),(8,4,9,3),(15,4,16,5),(10,5,11,6),(1,7,2,6),(12,8,13,7),(9,15,10,14)]
    # The algorithm is finding a consistent pinning poset for this loop
    #link= rawPDtoPlinkPD( link )

    # a 9 crossing example; cycle 0, 1 and 4 times to see small discrepancy
    link = [(1, 7, 2, 6), (4, 9, 5, 10), (2, 12, 3, 11),\
            (7, 13, 8, 12), (18, 13, 1, 14), (3, 17, 4, 16),\
            (5, 14, 6, 15), (8, 18, 9, 17), (10, 15, 11, 16)]

    
   
    drawnpd = plinkPD( link )
    #link.sort()
    #print( "original:", link )
    #print()

    #link1 = plinkPD( link )
    
    # do this cycling to make sure pinset behavior is preserved for different PD codes
    offset = 0
    for i in range( 2 ):
        link = drawnpd
        drawnpd = plinkPD( drawnpd )
        
        #link.sort()
        #print( i, ":", link )
    #   print()
       
    #return
    #print( rawPDtoPlinkPD( plinkPDtoRawPD( link ) ) )
    #print( plinkPDtoRawPD( rawPDtoPlinkPD( link ) ) )
    #print( plinkPDtoRawPD( plinkPDtoRawPD( rawPDtoPlinkPD( link ) ) ) )
    #print( rawPDtoPlinkPD( link ) )
    #print( rawPDtoPlinkPD( link ) )
    #plinkFromPD( link )
    #print( hackyPD( link ) )
    #plink( link1 )
    #return
    #link = '6_1'
    
    # the tests below all go faster than before
    #link = 'K14n1'
    #link = '10_24' # not showing minimal pinsets only? is computing ALL pinsets correctly by naive check
    #link = 'K11a340' #takes about 30 seconds to run
    #link = 'K11n100' #takes about a minute to run
    #pinSets( link, debug = True )

    # For debugging 9-crossing monorbigon-free example with PD_offset 0
    # toggle between baseRegion = 16898 ( naivePinSets: 374, recursivePinsets: 347 )
    # and baseRegion = 270864 ( naivePinSets: 395, recursivePinsets: 395 )
    
        pinsets = pinSets( drawnpd, debug = False )[0]#, treeBase = 270864 )#, rewriteFrom = 270864 )
        #print( pinsets )
        pinSetDict = {}
        minlen = len( pinsets[0] )
        print( "Minimal pinning sets:" )
        for elt in pinsets:
            try:
                pinSetDict[len(elt)]+=1
            except KeyError:
                pinSetDict[len(elt)] = 1
            print( elt )
            if len( elt ) < minlen:
                minlen = len( elt )
        print()
        print( "Number of minimal pinning sets:", len( pinsets ) )
        print( "Pinning number:", minlen )
        keys = list( pinSetDict.keys() )
        keys.sort()
        print( "Minimal pining sets by size:" )
        for key in keys:
           print( " Number of minimal pinning sets of size", key, ":", pinSetDict[key] )
        print()
        print( "PD_code offset:", i )
        print( "Input PD:", link )
        print( "Drawn PD:", drawnpd )
        print()

    #plinkFromPD( link )

def test7():
    link = '9_24'
    link = 'K11a340'
    G = SurfaceGraphFromPD( plinkPD( link ) )
    print()
    #print( G )
    T = G.spanningTree()
    T.createCyclicGenOrder()
    print( T )
    print()

    loop = T.genProd()

    print( "gamma", loop )
    print( "si(gamma):", loop.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564] )
    
    print( "gamma_{2564}", loop1) 
    print( "si(gamma_{2564}):", loop1.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564,18754] )    
    print( "gamma_{2564,18754}", loop1) 
    print( "si(gamma_{2564,18754}):", loop1.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564,18754,70152] )    
    print( "gamma_{2564,18754,70152}", loop1) 
    print( "si(gamma_{2564,18754,70152}):", loop1.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564,18754,70152,132138] )    
    print( "gamma_{2564,18754,70152,132138}", loop1) 
    print( "si(gamma_{2564,18754,70152,132138}):", loop1.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564,18754,70152,132138,37120] )    
    print( "gamma_{2564,18754,70152,132138,37120}", loop1) 
    print( "si(gamma_{2564,18754,70152,132138,37120}):", loop1.si( T.orderDict ) )
    print()

    loop1 = T.reducedWordRep( loop, [2564,18754,70152,132138,37120,41088] )    
    print( "gamma_{2564,18754,70152,132138,37120,41088}", loop1) 
    print( "si(gamma_{2564,18754,70152,132138,37120,41088}):", loop1.si( T.orderDict ) )
    print()
    
    #snappy.Link( link ).exterior().plink()
    plink( link )
    print(  "PD code from the hacky function:", plinkPD( link ) )
    print()
    print( "PD code that snappy returns:", snappy.Link( link ).PD_code() )
    print()
    print( "PD code from rolfsen tables:", readPlanarDiagram( link ) )

def test6():
    #snappy sample usage
    #draw link from PD code (note that the PD code generated by snappy is different from this one)
    #M = snappy.Link( [[4, 2, 5, 1], [8, 3, 9, 4], [10, 6, 11, 5], [14, 7, 15, 8],
    #                  [2, 9, 3, 10], [16, 12, 17, 11], [20, 14, 21, 13], [6, 15, 7, 16],
    #                  [22, 18, 1, 17], [12, 20, 13, 19], [18, 22, 19, 21]] ).exterior().plink()
    #draw link from standard identifier string

    
    # get link from standard identifier string
    L = snappy.Link( '8_3' )

    # draw link ( can be annotated with PD code )    
    M = L.exterior()
    M.plink()
    
    #store and print PD_code
    pd = L.PD_code()
    print( pd )

    # can convert from manifold to link as follows:
    L1 = M.exterior_to_link()
    



def test5():
    

    diagram = readPlanarDiagram( "0_1" )
    print( diagram )
    diagram = readPlanarDiagram( "3_1" )
    print( diagram )
    diagram = readPlanarDiagram( "K11a1")
    PlaneTreeFromPlanarDiagram( diagram )
    return
    print( diagram )
    diagram = readPlanarDiagram( "8_3")
    print( diagram )
    PlaneTreeFromPlanarDiagram( diagram )
    return
    diagram = readPlanarDiagram( "K11a368" )
    print( diagram )


def test4():
    
    trefoil = SurfaceGraph( [[-1],[-3,1],[4,3,2],[-2],[-4]] )
    trefoil.createCyclicGenOrder()
    print( trefoil )
    w=Word( [1,2,3,4] ) #represents the trefoil loop
    w2 = Word( list( range( 1, 25 ))*3 )
    print( w2.naivePrimitiveRoot()[0], w2.naivePrimitiveRoot()[1] )
    #return
    w1 = trefoil.reducedWordRep( w, [] )
    print( pow(w1,4).I(pow( w1, 4 ),trefoil.orderDict ) )
    print( pow(w1,4).si( trefoil.orderDict ) )
    return
    w = Word( [1,4])
    v = Word( [3,1])
    
    print( w.crossval(v,trefoil.orderDict) )
                           

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
        print( w.wslice( 3, 0 ) )
        print( w.shift( i ) )

    w = randomWord( 10, 5, s="hit7t4yyy" )
    print( "w= ", w )
    print( "w( a-->BCdc )",w.simpleRewrite( 1, Word( [-2, -3, 4, 3 ] ) ) )
    print( "w( A-->BCdc )",w.simpleRewrite( -1, Word( [-2, -3, 4, 3 ] ) ) )

####################### RUN MAIN ####################################

if __name__ == "__main__":
    main()
