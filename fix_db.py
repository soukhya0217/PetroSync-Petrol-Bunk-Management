from pymongo import MongoClient
db = MongoClient('mongodb://localhost:27017/').petrosync
db.users.update_one({'username': 'admin'}, {'$set': {'password': 'admin123'}})
db.users.update_one({'username': 'manager'}, {'$set': {'password': 'manager123'}})
print("Passwords fixed.")
