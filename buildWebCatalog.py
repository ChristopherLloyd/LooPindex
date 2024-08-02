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
    print( getFieldByName( "drawnpd", "12_361^1"  ) )

def createDatabase( maxRegions = 12 ):    
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
   
    #print( pinSets )
    setFieldByName( "minPinSets", pinSets["minPinSets"], name)
    #printRow( name )
    
####################### RUN MAIN ####################################

if __name__ == "__main__":
    main()