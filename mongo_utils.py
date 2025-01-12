import pymongo
import gridfs

class DBClient:
    def __init__(self, client_ref:str, db:str, bucket_name=None):
        self.client_ref = client_ref
        self.db = db
        self.db_client = pymongo.MongoClient(client_ref, connect=False)
        self.db_instance = self.db_client[db]
        self.fs = None
        self.bucket_name = bucket_name
        if bucket_name != None:
            self.fs = gridfs.GridFSBucket(self.db_instance, bucket_name=bucket_name)
        else:
            self.fs = gridfs.GridFSBucket(self.db_instance)  


    def insert(self, collection:str, data:dict|list, all:bool) -> int:
         match all:
              case True:
                    return  self.db_instance[collection].insert_many(data).inserted_ids
              case False:                  
                    return self.db_instance[collection].insert_one(data).inserted_id     
                        
    
    def find(self, collection:str, all:bool, query:dict) -> dict|list:
        cursor = self.db_instance[collection].find(query)
        match all:
            case True:
                    return list(cursor)
            case False:
                    try:
                        return next(cursor)
                    except StopIteration:
                        return None

    def update(self, collection:str, query:dict, new_values:dict|list, all:bool) -> int:
            match all:
              case True:
                        return self.db_instance[collection].update_many(query, new_values).modified_count
              case False:
                        return self.db_instance[collection].delete_one(query).deleted_count
    
    def delete(self, collection:str, query:dict, all:bool) -> int:
         
         match all:
              case True:
                        return self.db_instance[collection].delete_many(query).deleted_count
              case False: 
                        return self.db_instance[collection].delete_one(query).deleted_count
               
    def fs_upload(self, fp:str|list, fn:str|list,  size_bytes:int, many:bool=False, metadata:dict=None) -> bool:
        if many:
            try:
                i=0
                while i < len(fp):
                    f= self.fs.open_upload_stream(fn[i], size_bytes, metadata=metadata) 
                    f.write(open(fp[i], "rb").read())
                    f.close()
                    i+=1
                return True
            except Exception as e:
                print("execpt ", e)
                return e
        else:
            try:
                with self.fs.open_upload_stream(fn, size_bytes, metadata=metadata) as f:
                    f.write(open(fp, "rb").read())
                    f.close()
                    return True
            except Exception as e:
                print("execpt ", e)
                return e
                           

    def fs_find(self, file_name:str=None,  sort:dict=None)-> bytes:
        #sort example {uploadDate:"", limit:1}
        data=None
        if sort == None and file_name !=None:
            for grid_data in self.fs.find({"filename": file_name}):
                data = grid_data.read()
        else:
            data=self.fs.find().sort(sort["uploadDate"], -1).limit(sort["limit"])
        return data
    
    def fs_download(self, fp:str, fn:str) ->str:
        file = self.fs.open_download_stream_by_name(fn)
        data = file.read()
        with open(fp, "wb") as f:
            f.write(data)
            f.close()
        return fp

    def fs_delete(self, fn:str|list=None, object_id:str|list=None, many:bool=False):
        if object_id == None and many==False:
            object_id = self.find(self.bucket_name+".files", False, {"filename":fn})["_id"]
            self.fs.delete(object_id)
        elif object_id ==None and many ==True:
            for i in range(len(fn)):
                object_id = self.find(self.bucket_name+".files", False, {"filename":fn[i]})["_id"]
                self.fs.delete(object_id)
        elif object_id != None and many ==False:
            self.fs.delete(object_id)
        elif object_id != None and many == True:
             for i in range(len(i)):
                self.fs.delete(object_id[i])          