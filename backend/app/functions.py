 #!/usr/bin/python3


#################################################################################################################################################
#                                                    CLASSES CONTAINING ALL THE APP FUNCTIONS                                                                                                    #
#################################################################################################################################################



class DB:

    def __init__(self,Config):

        from math import floor
        from os import getcwd
        from os.path import join
        from json import loads, dumps, dump
        from datetime import timedelta, datetime, timezone 
        from pymongo import MongoClient , errors, ReturnDocument
        from urllib import parse
        from urllib.request import  urlopen 
        from bson.objectid import ObjectId  
       
      
        self.Config                         = Config
        self.getcwd                         = getcwd
        self.join                           = join 
        self.floor                      	= floor 
        self.loads                      	= loads
        self.dumps                      	= dumps
        self.dump                       	= dump  
        self.datetime                       = datetime
        self.ObjectId                       = ObjectId 
        self.server			                = Config.DB_SERVER
        self.port			                = Config.DB_PORT
        self.username                   	= parse.quote_plus(Config.DB_USERNAME)
        self.password                   	= parse.quote_plus(Config.DB_PASSWORD)
        self.remoteMongo                	= MongoClient
        self.ReturnDocument                 = ReturnDocument
        self.PyMongoError               	= errors.PyMongoError
        self.BulkWriteError             	= errors.BulkWriteError  
        self.tls                            = False # MUST SET TO TRUE IN PRODUCTION


    def __del__(self):
            # Delete class instance to free resources
            pass
 


    ####################
    # LAB 4 FUNCTIONS  #
    ####################
    
    # 1. CREATE FUNCTION TO INSERT DATA IN TO THE RADAR COLLECTION
    def insertData(self, data):
        ''' Insert data into the radar collection '''
        try:
            # Insert data into the radar collection

            remotedb = self.remoteMongo('mongodb://%s:%s@%s:%s' % (self.username, self.password,self.server,self.port), tls=self.tls)
            result = remotedb.ELET2415.radar.insert_one(data)
        except Exception as e:
            msg = str(e)
            print("insertData Error: ", msg)    
        else:
            return result

    
    # 2. CREATE FUNCTION TO RETRIEVE ALL DOCUMENTS FROM RADAR COLLECT BETWEEN SPECIFIED DATE RANGE. MUST RETURN A LIST OF DOCUMENTS
    def retrieve_radar(self, start, end):
        '''Retrieves all documents from the 'radar' collection between specified date range'''
        try:
            start = int(start)
            end = int(end)

            remotedb 	= self.remoteMongo('mongodb://%s:%s@%s:%s' % (self.username, self.password,self.server,self.port), tls=self.tls)
            result      = remotedb.ELET2415.radar.find({"timestamp": {"$gte": start, "$lte": end}, "reserve": {"$exists": True}},{"_id":0, "timestamp":1, "reserve":1, "waterheight":1})
        except Exception as e:
            print(f"retrieve_radar() error: {e}")
            return False
        else:
            return result


    # 3. CREATE A FUNCTION TO COMPUTE THE ARITHMETIC AVERAGE ON THE 'reserve' FEILED/VARIABLE, USING ALL DOCUMENTS FOUND BETWEEN SPECIFIED START AND END TIMESTAMPS. RETURNS A LIST WITH A SINGLE OBJECT INSIDE
    def average_radar(self, start, end):
        '''Computes the arithmetic average on the 'reserve' field/variable, using all documents found between specified start and end timestamps'''
        try:
            start = int(start)
            end = int(end)

            remotedb 	= self.remoteMongo('mongodb://%s:%s@%s:%s' % (self.username, self.password,self.server,self.port), tls=self.tls)
            result      = result = remotedb.ELET2415.radar.aggregate([{"$match": {"timestamp": {"$gte": start, "$lte": end}}},{"$group": {"_id": None, "average": {"$avg": "$reserve"}}},{"$project": {"_id": 0, "average": 1}}])

        except Exception as e:
            print(f"average_radar() error: {e}")
            return False
        else:
            return result
    
    
    # 4. CREATE A FUNCTION THAT INSERT/UPDATE A SINGLE DOCUMENT IN THE 'code' COLLECTION WITH THE PROVIDED PASSCODE
    def setPass(self, passcode):
        ''' Update the document in the 'code' collection with the new passcode '''
        passcode = str(passcode)
        try:
            # Update the document in the 'code' collection with the new passcode
            remotedb = self.remoteMongo('mongodb://%s:%s@%s:%s' % (self.username, self.password,self.server,self.port), tls=self.tls)
            item = remotedb.ELET2415.code.find_one_and_update({}, { '$set': {'code': passcode}}, upsert=True, projection={'_id': False})
        except Exception as e:
            msg = str(e)
            print("setPwd Error: ", msg)
        else:
            return item 
             
 
   
    
    # 5. CREATE A FUNCTION THAT RETURNS A COUNT, OF THE NUMBER OF DOCUMENTS FOUND IN THE 'code' COLLECTION WHERE THE 'code' FEILD EQUALS TO THE PROVIDED PASSCODE.
    #    REMEMBER, THE SCHEMA FOR THE SINGLE DOCUMENT IN THE 'code' COLLECTION IS {"type":"passcode","code":"0070"}
        
    def count_passcodes(self,passcode):
        '''Returns the number of passcodes found in the 'code' collection'''
        try:
            passcode = str(passcode)

            remotedb 	= self.remoteMongo('mongodb://%s:%s@%s:%s' % (self.username, self.password,self.server,self.port), tls=self.tls)
            result      = remotedb.ELET2415.code.count_documents({"code":passcode})
        except Exception as e:
            print(f"count_passcodes() error: {e}")
            return False
        else:
            return result


   



def main():
    from config import Config
    from time import time, ctime, sleep
    from math import floor
    from datetime import datetime, timedelta
    one = DB(Config)
 
 
    start = time() 
    end = time()
    print(f"completed in: {end - start} seconds")
    
if __name__ == '__main__':
    main()


    