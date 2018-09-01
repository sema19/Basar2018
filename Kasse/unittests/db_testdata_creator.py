'''
Created on Aug 26, 2018

@author: sedlmeier
'''
import datetime
import LocalStorage
import uuid
from datetime import datetime
import random
from LocalStorage import LocalStorage


def insertVals(table, headersList, valsList):
    valstxt=""
    comma=""
    headerstxt=",".join(headersList)
    for vals in valsList:
        valstxt+=comma+"("+','.join(vals)+")"
        comma=','
    stmt=['''INSERT INTO %table (%s) VALUES (%s);'''%(table, headerstxt,valstxt)]
    runStatementList(stmt)    
    
def runStatementList(stmtList):
    ls=LocalStorage.LocalStorage(LocalStorage.getDatabaseFilepath())          
    for stmt in stmtList:
        ls.dbWrite(stmt)

_firstnames_=['Hans','Peter','Franz','Frank','Theodor','Herbert','Martin','Georg','Walburga','Maria','Erika','Anna','Josef']
_lastnames_=['Meier','Huber','Schmid','Schmidt','Mayer','Müller','Sonne','Baum','Wald','Mond','Bauer','Plank','Stadler','Wirt']
_providers_=['t-online.de','gmx.de','gmail.com','1und1.de','webhoster.com']
_articles_=[('Jeans','164'),('T-Shirt','xs'),('Playmobil Figur',''),('Lego Feuerwehr','groß'),('BobbyCar','klein'),('Hemd','152-134'),('Hose','123'),('Socken','42'),('Schafkopfkarten','32'),('Mähdrescher','original Groesse'),('Mischmaschine',''),('Buch','Taschenbuch')]

def defaultSet1_users(cnt=10,start=150):
    users=[];
    for userid in range(start,start+cnt+1):
        tnow=str(datetime.datetime())    
        firstname=random.choice(_firstnames_)
        lastname=random.choice(_lastnames_)
        tel="0"+str(random.randint(1000,9999))+' '+random.randint(100,99999)
        email = firstname + '.'+lastname+'@'+random.choice(_providers_)
        users.add([userid,firstname,lastname,tel,tnow,email])
    return users
    
def defaultSet1_items(users, cnt=50,start=1000, minPerUser=1, maxPerUser=10):
    items=[]
    userItemMax=0
    userItemCurrent=0
    userCurrent=0
    userid=0
    for itemid in range(start,start+cnt+1):        
        if userItemCurrent == userItemMax:
            userItemMax=random.randint(minPerUser,maxPerUser)
            userid=users[userCurrent][0]
            userCurrent+=1
            userItemCurrent=0
        tnow=datetime.datetime()
        userid=users[userCurrent][0]
        nummer=str(userItemCurrent+1)
        barcode=0
        article=random.choice(_articles_)
        bezeichnung=article[0]
        groesse=article[1]
        preis=(float)(random.randint(150))
        if random.randint(100)%2==0:
            preis+=(float)0.5            
        created=tnow
        modified=tnow
        items.add([userid,nummer,barcode,bezeichnung,groesse,preis,tnow,tnow])
    return items
        
        
        
        
        
        
        
        
    
def createArticles():
    stmt=[]
    stmt+=['''DROP TABLE IF EXISTS articles''']
    stmt+=['''CREATE TABLE articles ( barcode INTEGER, cartId INTEGER, pos INTEGER, status TEXT, PRIMARY KEY (barcode, cartId) );''']
    runStatementList(stmt)    

def insertArticles(articleList):
    stmt=[]    
    stmt='''INSERT INTO articles ( barcode, cartId, pos, status) VALUES (%s);'''
    runStatementList(stmt)
    

def createItems():
    # Example: "10908"    "192"    "1"    "13010181"    "Something"    "164"    "7.0"    "2017-08-14 11:46:07"    "2017-09-06 09:19:33"
    stmt=[]
    stmt+='''DROP TABLE IF EXISTS items'''
    stmt+='''CREATE TABLE items (id INTEGER PRIMARY KEY, user_id INTEGER, nummer INTEGER, barcode INTEGER, bezeichnung TEXT, groesse TEXT , preis FLOAT, created DATETIME, modified DATETIME );'''
    runStatementList(stmt)
    
    
def insertItems(itemsList):
    stmt=[]
    stmt+='''INSERT INTO items ( id, user_id, nummer, barcode, bezeichnung, groesse, preis, created, modified) VALUES (%s);'''
    runStatementList(stmt)
    

def createUsers():
    stmt=[]
    stmt='''DROP TABLE IF EXISTS users'''
    stmt='''CREATE TABLE users (id INTEGER PRIMARY KEY, number TEXT, code TEXT, vorname TEXT, nachname TEXT, tel TEXT, created DATETIME , email TEXT );'''
    runStatementList(stmt)
        
def insertUsers(usersList=([]), usersHeader=["number", "code", "vorname", "nachname", "tel", "created", "email"]):
    insertVals("users",usersHeader,usersList)

def createLocalPaydesk():
    ls=LocalStorage.LocalStorage(LocalStorage.getDatabaseFilepath())
    tnow=str(datetime.now())
    ret = ls.getLocalPaydesk()
    if ret==[] or ret==None:                
        paydeskId=uuid.uuid4()      
        ls.createLocalPaydesk("TestLocalKasse",
                               "127.0.0.1",
                               9799)

    
def createRemotePaydesk():
    ls=LocalStorage.LocalStorage(LocalStorage.getDatabaseFilepath())
    tnow=str(datetime.now())
    ret = ls.getRemotePaydesks()
    if ret==[] or ret==None:                
        paydeskId=uuid.uuid4()      
        ls.createRemotePaydesk(paydeskId,
                               "TestRemoteKasse",
                               tnow,
                               tnow,
                               "127.0.0.1",
                               9798)
    
    
    
    