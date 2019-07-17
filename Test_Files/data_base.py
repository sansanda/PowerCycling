'''
Created on 15 jul. 2019

@author: mespower
'''

#Data base


import pyodbc
from pyodbc import Error
 
def sql_connection(_db_path):
 
    try:
        
        conn_str = (
            'DRIVER={Microsoft Access Driver (*.mdb)};'
            +'DBQ='
            +str(_db_path)
            +';'
            )
        conn = pyodbc.connect(conn_str)
        return conn
 
    except Error:
        
         print(Error)
         
         
        
def create_table(_conn,_db_name,_table_name,_camps_names):
    cursorObj = _conn.cursor()
    s = "CREATE TABLE "+str(_table_name)+" (ncicle integer PRIMARY KEY, semi_cicle varchar(3), tStamp long";
    #print(s)
    for campName in _camps_names:
        s = s + ", " +campName+" double"
    s = s + ")"
    cursorObj.execute(s)
 
    _conn.commit()


def delete_table(_conn,_db_name,_table_name):
    cursorObj = _conn.cursor() 
    s = "DROP TABLE "+str(_table_name)+";"
    cursorObj.execute(s)
    _conn.commit()

def insertRowInTable(_conn,_db_name,_table_name,_rowValues):
    cursorObj = conn.cursor()
    s = "INSERT INTO " + str(_table_name) + " VALUES("
    for rowValue in _rowValues:
        s = s + rowValue + ","
    s = s[0:len(s)-1]
    s = s +")"     
    print(s)
    cursorObj.execute(s)
    conn.commit()


#def create_table(table_columns):
 #   nchannels = table_columns.len - 3
    
    #table_columns[0]
db_name = "power_cycling_results"
db_path = ".\\bbdd\\" + str(db_name)+".mdb" 
new_table_name = "table10"
existing_table_name = "table6"
newRowValues = ["1","ON","234235234","1","2","3"]
channelsList = ["nchannel1","nchannel2","nchannel3"]

conn = sql_connection(db_path)
#create_table(conn,db_name,new_table_name,channelsList)
delete_table(conn, db_name, existing_table_name)
#insertRowInTable(conn, db_name, existing_table_name,newRowValues)
conn.close()    

