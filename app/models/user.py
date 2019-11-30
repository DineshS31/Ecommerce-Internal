from app import db
from bson.objectid import ObjectId


class UserEntries:
    def add_user(self,payload):
        data = {}
        data['_id'] = str(ObjectId())
        data['first_name'] = payload['first_name']
        data['last_name'] = payload['last_name']
        data['emai'] = payload['email']
        data['recently_logged_on'] = payload['login_time']
        tb = db.users.insert_one(data)
        return tb.inserted_id


    def retrieve_user_using_email(self, email):
        user_info = db.users.find_one({"email": email})
        return user_info if user_info else {}
