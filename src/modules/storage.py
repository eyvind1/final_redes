import psycopg2
import logging
import logger
import atexit
from config import config 

dataFd = None
errorFd = None
word=""
def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()
 
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
 
        # create a cursor
        cur = conn.cursor()
        
 # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
 
        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
       
     # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
 
def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE vendors (
            vendor_id SERIAL PRIMARY KEY,
            vendor_name VARCHAR(255) 
        )
        """,
        """ CREATE TABLE parts (
                part_id SERIAL PRIMARY KEY,
                part_name VARCHAR(255) NOT NULL
                )
        """,
        """
        CREATE TABLE part_drawings (
                part_id INTEGER PRIMARY KEY,
                file_extension VARCHAR(5) NOT NULL,
                drawing_data BYTEA NOT NULL,
                FOREIGN KEY (part_id)
                REFERENCES parts (part_id)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE vendor_parts (
                vendor_id INTEGER NOT NULL,
                part_id INTEGER NOT NULL,
                PRIMARY KEY (vendor_id , part_id),
                FOREIGN KEY (vendor_id)
                    REFERENCES vendors (vendor_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (part_id)
                    REFERENCES parts (part_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
        )
        """)
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
 

def insert_table(vendor_list):
    """ insert multiple vendors into the vendors table  """
    sql = "INSERT INTO vendors(vendor_name) VALUES(%s)"
    conn = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.executemany(sql,vendor_list)
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def insert_one(vendor_name):
    """ insert a new vendor into the vendors table """
    sql = """INSERT INTO vendors(vendor_name)
             VALUES(%s) RETURNING vendor_id;"""
    conn = None
    #vendor_id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (vendor_name))
        # get the generated id back
        vendor_id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    """finally:
        if conn is not None:
            conn.close()"""

def writeToFile(session, container):
    global dataFd, errorFd
    try:
        if (not session.failed):
            if dataFd is None:
                
                dataFd = open('output.txt', 'w')
            
            dataFd.write(str(container.author).replace(",","") + "," + str(container.title).replace(",","") + "," + session.url +"\n")
        elif session.failed:
            if errorFd is None:
                errorFd = open('error.txt', 'w')
            errorFd.write(str(session.returnCode).replace(",","") + "," + str(session.errorMsg).replace(",","") + "." + session.url.replace(",","") + "\n")
        #else:
        #    raise Exception("..")
    except:
        logger.log(logging.ERROR, "Unhandled exception in storage.py")

def writeToDb(session, container):
    #conn = psycopg2.connect("dbname=crawler")
    try:
        if (not session.failed):
            #insert_one(session.url)
            
            sql = """INSERT INTO url(url_name)
             VALUES(%s);"""
            conn = None
            try:
                # read database configuration
                params = config()
                # connect to the PostgreSQL database
                conn = psycopg2.connect(**params)
                # create a new cursor
                cur = conn.cursor()
                # execute the INSERT statement
                cur.execute(sql, (session.url,))
                # commit the changes to the database
                #conn.commit()
                # close communication with the database
                cur.close()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
            print "ez"
            
        elif session.failed:
            insert_one(session.url.replace)
        #else:
        #    raise Exception("..")
    except:
        logger.log(logging.ERROR, "Unhandled exception in storage.py")




def atexitfct():
    """Cleanly closes file objects"""
    if dataFd is not None:
        dataFd.close()
    if errorFd is not None:
        errorFd.close()

atexit.register(atexitfct)
"""
if __name__ == '__main__':
    #connect()
    #create_tables()
    print word
    #insert_one(word)
"""