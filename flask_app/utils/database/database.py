import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow
from dotenv import load_dotenv
import os

load_dotenv()

class database:

    def __init__(self, purge = False):

        # Grab information from environment variables
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password = os.getenv('PASSWORD')
        self.tables = ['users', 'boards', 'userboards', 'lists', 'cards']

        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption = {
            'oneway': {
                'salt': os.getenv('ENCRYPTION_ONEWAY_SALT').encode('utf-8'),
                'n': int(os.getenv('ENCRYPTION_ONEWAY_N')),
                'r': int(os.getenv('ENCRYPTION_ONEWAY_R')),
                'p': int(os.getenv('ENCRYPTION_ONEWAY_P'))
            },
            'reversible': {
                'key': os.getenv('ENCRYPTION_REVERSIBLE_KEY')
            }
        }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        ''' FILL ME IN WITH CODE THAT CREATES YOUR DATABASE TABLES.'''

        #should be in order or creation - this matters if you are using forign keys.
         
        if purge:
            for table in self.tables[::-1]:
                self.query(f"""DROP TABLE IF EXISTS {table}""")
            
        # Execute all SQL queries in the /database/create_tables directory.
        for table in self.tables:
            
            #Create each table using the .sql file in /database/create_tables directory.
            with open(data_path + f"create_tables/{table}.sql") as read_file:
                create_statement = read_file.read()
            self.query(create_statement)



    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        
        # Check if there are multiple rows present in the parameters
        has_multiple_rows = any(isinstance(el, list) for el in parameters)
        keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
        # Construct the query we will execute to insert the row(s)
        query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        if has_multiple_rows:
            for p in parameters:
                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))
        else:
            query += f"""({values}) """                      
        insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']         
        return insert_id
    
    def getBoards(self, user):
        board_names = []
        user_id = self.query(f"""SELECT user_id FROM `users` WHERE email = \'{user}\'""")
        temp = user_id[0]['user_id']
        board_ids = self.query(f"""SELECT board_id FROM `userboards` WHERE user_id = \'{temp}\'""")
        for board in board_ids:
            id = board['board_id']
            board_name = self.query(f"""SELECT name FROM `boards` WHERE board_id = \'{id}\'""")
            board_names.append([id,board_name[0]['name']])
        return board_names

    def get_board(self, id):
        # Pulls data from the database to genereate data like this:
        board = {}
        boards = self.query(f"""SELECT * FROM `boards` WHERE board_id = {id}""")
        lists = self.query(f"""SELECT * FROM `lists` WHERE board_id = {id} """)
        cards = self.query(f"""SELECT * FROM `cards` WHERE board_id = {id}""")

        for i in range(len(boards)):
            board[boards[0]['name']] = {}
            for j in range(len(lists)):
                board[boards[0]['name']][lists[j]['list_id']] = lists[j]
                board[boards[0]['name']][lists[j]['list_id']]['cards'] = {}
                for k in range(len(cards)):
                    board[boards[0]['name']][lists[j]['list_id']]['cards'][cards[k]['card_id']] = cards[k]
        
        return board
    
    def get_user_id(self,email):
        res = self.query(f"""SELECT user_id FROM `users` WHERE email = \'{email}\'""")
        id = res[0]['user_id']
        if id:
            return id
        else:
            return 0 

    
#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email='me@email.com', password='password', role='user'):        
        try:
            query = f"""
                    SELECT email
                    FROM `users`
                    WHERE email = \'{email}\';
                    """
            exists = self.query(query)
            if exists:
                return  {'success' : 0}
            encrypted_Pass = self.onewayEncrypt(password)
            parameters = [[role,email,encrypted_Pass]]
            columns = ['role','email','password']
            self.insertRows('users', columns, parameters)
            return {'success': 1}
        except:
            return {'success' : 0}

    def createBoard(self, user_id, name):
        try:
            query = f"""
                    SELECT name
                    FROM `boards`
                    WHERE name = \'{name}\';
                    """
            exists = self.query(query)
            if exists:
                return  {'success' : 0}
            
            parameters = [[name]]
            columns = ['name']
            board_id = self.insertRows('boards', columns, parameters)
            self.insertRows('userboards',['board_id','user_id'], [[board_id,user_id]] )
            l1 = self.insertRows('lists',['board_id','name'], [[board_id,'To Do']] )
            l2 = self.insertRows('lists',['board_id','name'], [[board_id,'Doing']] )
            l3 = self.insertRows('lists',['board_id','name'], [[board_id,'Completed']])
            return {'success': 1, 'board_id' : board_id}
        except:
            return {'success' : 0}
        
    def addMember(self, user_id, board_id):
        self.insertRows('userboards',['board_id','user_id'], [[board_id,user_id]] )  

    def AddCard(self, board_id, list_id):
        blank = 'click EDIT to edit'
        c_id = self.insertRows('cards',['board_id','list_id', 'content'], [[board_id,list_id,blank]] )  
        return c_id

    def DeleteCard(self, board_id, card_id):
        del_query = f"DELETE FROM `cards` WHERE card_id = \'{card_id}\'"
        self.query(del_query)

    def EditCard(self,card_id, edits):
        print("##################################")
        edit_query = f"""UPDATE `cards`
            SET content = \'{edits}\'
            WHERE card_id = \'{card_id}\';"""
        self.query(edit_query)

    def authenticate(self, email='me@email.com', password='password'):
        encrypted_pass = self.onewayEncrypt(password)
        encrypted_email = self.onewayEncrypt(email)
        query = f"""
                    SELECT email
                    FROM `users`
                    WHERE email = \'{email}\'
                    AND password = \'{encrypted_pass}\';
                    """
        exists = self.query(query)
        if exists:
            return {'success': 1}
        else:
            return {'success' : 0}

    def isOwner(self, email='me@email.com'):
        encrypted_email = self.onewayEncrypt(email)
        query = f"""
                    SELECT email
                    FROM `users`
                    WHERE email = \'{email}\'
                    AND role = 'owner';
                    """
        exists = self.query(query)
        if exists:
            return True
        else:
            return False

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message


