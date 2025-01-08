import pymongo

class DBClient:
    def __init__(self, client_ref:str, db:str):
        self.client_ref = client_ref
        self.db = db
        self.db_client = pymongo.MongoClient(client_ref, connect=False)
        self.db_instance = self.db_client[db]


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