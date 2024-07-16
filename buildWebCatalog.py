from planeloop import *
import mysql.connector
import os

def main():
    createDatabase()

def createDatabase( maxRegions = 12 ):
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
        components INT,
        epsilon VARCHAR(500),
        drawnpd VARCHAR(500),        
        numRegions INT,
        name VARCHAR(20),
        next VARCHAR(20),
        prev VARCHAR(20)
        )
    """
    cursor.execute(create_table)
    for k in range( 4, maxRegions+1):
        generateMultiloops( k, numComponents = "any" ,includeReflections = False, primeOnly = True, db = db, cursor = cursor )

####################### RUN MAIN ####################################

if __name__ == "__main__":
    main()