from config import TIME_TO_DELETE
from datetime import datetime, timezone


def unix_time_now(UTC:bool)->int:
    if UTC:
        dt_utc_aware = datetime.now(timezone.utc)
        return dt_utc_aware.timestamp()
    else:
        return datetime.now().timestamp()

def DB_timer(DB, Coollection:str)->bool:
    data = DB.find(Coollection, False, {"tg_id":111})["orders"]
    for i in range(len(data)):
        if data[i]["date"]+TIME_TO_DELETE <= unix_time_now():
            new = data.pop[i]
            DB.collection.update(dict({"tg_id":111, "orders":data}), 
            dict({"$set":{f"orders.{i}":new}}))
    return True