from flask import Flask, request, jsonify, send_from_directory, session
from pymongo import MongoClient
from flask_cors import CORS
from bson import ObjectId
import datetime
import os

app = Flask(__name__)
CORS(app)
app.secret_key = 'petrosync_secret'

# Setup MongoDB
# Default to localhost if no connection string is provided
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['petrosync']

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(path):
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')

# -----------------
# INITIAL SEEDING
# -----------------
def seed_db():
    if db.users.count_documents({}) == 0:
        db.users.insert_many([
            {"username": "admin", "password": "admin123", "role": "admin", "name": "Admin"},
            {"username": "manager", "password": "manager123", "role": "manager", "name": "Manager"}
        ])
    if db.pumps.count_documents({}) == 0:
        db.pumps.insert_many([
            {"num": 1, "fuel": "Petrol", "status": "active", "operator": "Ravi", "sales": 450, "rev": 43500},
            {"num": 2, "fuel": "Diesel", "status": "active", "operator": "Suresh", "sales": 320, "rev": 28600},
            {"num": 3, "fuel": "Petrol", "status": "idle", "operator": "unassigned", "sales": 150, "rev": 14500},
            {"num": 4, "fuel": "Diesel", "status": "maintenance", "operator": "unassigned", "sales": 0, "rev": 0},
        ])
    if db.employees.count_documents({}) == 0:
        db.employees.insert_many([
            {"name": "Ravi Kumar", "role": "Pump Operator", "phone": "9876543210", "pump": 1, "status": "on_duty"},
            {"name": "Suresh Babu", "role": "Pump Operator", "phone": "9876543211", "pump": 2, "status": "on_duty"}
        ])
    if db.stock.count_documents({}) == 0:
        db.stock.insert_many([
            {"fuel": "Petrol", "qty": 2500, "threshold": 500, "price": 96.72, "supplier": "BPCL"},
            {"fuel": "Diesel", "qty": 3000, "threshold": 500, "price": 89.62, "supplier": "HPCL"},
            {"fuel": "CNG", "qty": 140, "threshold": 500, "price": 85.00, "supplier": "BPCL"},
            {"fuel": "EV", "qty": 4, "threshold": 0, "price": 12.00, "supplier": "BESCOM"}
        ])
    if db.alerts.count_documents({}) == 0:
        db.alerts.insert_many([
            {"message": "CNG stock critically low — 140 Kg remaining. Threshold: 500 Kg. Contact BPCL for immediate supply.", "type": "critical"}
        ])

seed_db()

# -----------------
# API ENDPOINTS
# -----------------

def serialize(doc):
    doc['_id'] = str(doc['_id'])
    return doc

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = db.users.find_one({"username": data.get("username"), "password": data.get("password")})
    if user:
        resp = {"success": True, "role": user.get("role"), "name": user.get("name")}
        if user.get("role") == "customer":
            resp["points"] = user.get("points", 0)
            raw_vehicles = user.get("vehicles", [])
            resp["vehicles"] = [{"number": v} if isinstance(v, str) else v for v in raw_vehicles]
            resp["username"] = user.get("username")
            feedbacks = list(db.feedback.find({"name": user.get("name")}).sort("_id", -1))
            for f in feedbacks:
                f['_id'] = str(f['_id'])
            resp["feedbacks"] = feedbacks
        return jsonify(resp)
    return jsonify({"success": False}), 401

@app.route('/api/pumps', methods=['GET', 'POST'])
def pumps():
    if request.method == 'GET':
        return jsonify([serialize(p) for p in db.pumps.find()])
    elif request.method == 'POST':
        data = request.json
        data['sales'] = 0
        data['rev'] = 0
        res = db.pumps.insert_one(data)
        data['_id'] = str(res.inserted_id)
        return jsonify(data)


@app.route('/api/pumps/<id>/status', methods=['PUT'])
def toggle_pump(id):
    data = request.json
    db.pumps.update_one({"_id": ObjectId(id)}, {"$set": {"status": data.get("status")}})
    return jsonify({"success": True})

@app.route('/api/customer/vehicle', methods=['POST'])
def add_vehicle():
    data = request.json
    db.users.update_one({"username": data.get("username")}, {"$push": {"vehicles": data.get("vehicle")}})
    return jsonify({"success": True})

@app.route('/api/pumps/adjust', methods=['PUT'])
def adjust_pump():
    data = request.json
    pump_id = data.get('id')
    sales = float(data.get('sales', 0))
    rev = float(data.get('rev', 0))
    db.pumps.update_one({"_id": ObjectId(pump_id)}, {"$set": {"sales": sales, "rev": rev}})
    return jsonify({"success": True})

@app.route('/api/pumps/<id>', methods=['DELETE'])
def delete_pump(id):
    db.pumps.delete_one({"_id": ObjectId(id)})
    return jsonify({"success": True})

@app.route('/api/employees', methods=['GET', 'POST'])
def employees():
    if request.method == 'GET':
        role_filter = request.args.get("role")
        query = {}
        if role_filter and role_filter != "all":
            if role_filter == "manager":
                query["role"] = "Manager"
            elif role_filter == "workers":
                query["role"] = {"$ne": "Manager"}
            elif role_filter == "on_duty":
                query["status"] = "on_duty"
        
        # Searching by pump
        pump_search = request.args.get("pump")
        if pump_search:
            try:
                query["pump"] = int(pump_search)
            except:
                pass

        return jsonify([serialize(e) for e in db.employees.find(query)])
    elif request.method == 'POST':
        data = request.json
        res = db.employees.insert_one(data)
        data['_id'] = str(res.inserted_id)
        return jsonify(data)

@app.route('/api/employees/<id>/duty', methods=['PUT'])
def toggle_duty(id):
    emp = db.employees.find_one({"_id": ObjectId(id)})
    if not emp: return jsonify({"success": False}), 404
    new_status = "on_duty" if emp.get("status") != "on_duty" else "off_duty"
    db.employees.update_one({"_id": ObjectId(id)}, {"$set": {"status": new_status}})
    return jsonify({"success": True, "status": new_status})

@app.route('/api/sales', methods=['GET', 'POST'])
def sales():
    if request.method == 'GET':
        payment_filter = request.args.get("payment")
        query = {}
        if payment_filter and payment_filter != "all":
            query["payment"] = payment_filter
        return jsonify([serialize(s) for s in db.sales.find(query).sort("_id", -1)])
    elif request.method == 'POST':
        data = request.json
        data['time'] = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
        res = db.sales.insert_one(data)
        data['_id'] = str(res.inserted_id)
        
        # Deduct stock
        db.stock.update_one({"fuel": data['fuel']}, {"$inc": {"qty": -float(data['qty'])}})
        
        # Add to pump sales
        db.pumps.update_one({"num": int(data['pump'])}, {"$inc": {"sales": float(data['qty']), "rev": float(data['amount'])}})
        
        return jsonify(data)

@app.route('/api/stock', methods=['GET'])
def get_stock():
    return jsonify([serialize(s) for s in db.stock.find()])

@app.route('/api/stock/refill', methods=['POST'])
def refill_stock():
    data = request.json
    # data: {fuel, qty, supplier, invoice}
    db.stock.update_one(
        {"fuel": data['fuel']}, 
        {"$inc": {"qty": float(data['qty'])}, "$set": {"supplier": data['supplier'], "last_invoice": data['invoice'], "last_refill": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")}}
    )
    
    # Save to history
    history_entry = {
        "type": "refill",
        "fuel": data['fuel'],
        "qty": float(data['qty']),
        "supplier": data['supplier'],
        "invoice": data['invoice'],
        "time": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    }
    db.stock_history.insert_one(history_entry)
    
    # Auto-resolve low stock alerts for this fuel
    db.alerts.delete_many({"message": {"$regex": data['fuel'], "$options": "i"}})
    
    return jsonify({"success": True})

@app.route('/api/stock/history', methods=['GET'])
def get_stock_history():
    history_type = request.args.get("type", "all")
    query = {}
    if history_type != "all":
        query["type"] = history_type
    return jsonify([serialize(s) for s in db.stock_history.find(query).sort("_id", -1)])

@app.route('/api/stock/price', methods=['PUT'])
def update_stock_price():
    data = request.json
    now_str = datetime.datetime.now().strftime("%I:%M %p, %d %b")
    for fuel, price in data.items():
        db.stock.update_one({"fuel": fuel}, {"$set": {"price": float(price), "last_refill": now_str}})
    return jsonify({"success": True})

@app.route('/api/stock/adjust', methods=['PUT'])
def adjust_stock():
    data = request.json
    fuel = data.get('fuel')
    qty = float(data.get('qty', 0))
    threshold = float(data.get('threshold', 0))
    db.stock.update_one({"fuel": fuel}, {"$set": {"qty": qty, "threshold": threshold}})
    return jsonify({"success": True})

@app.route('/api/alerts', methods=['GET', 'DELETE'])
def get_alerts():
    if request.method == 'GET':
        return jsonify([serialize(a) for a in db.alerts.find()])

@app.route('/api/alerts/<id>', methods=['DELETE'])
def delete_alert(id):
    db.alerts.delete_one({"_id": ObjectId(id)})
    return jsonify({"success": True})

@app.route('/api/customer/register', methods=['POST'])
def register_customer():
    data = request.json
    data['role'] = 'customer'
    data['points'] = 0
    data['vehicles'] = [v.strip() for v in data.get('vehicles', '').split(',') if v.strip()]
    res = db.users.insert_one(data)
    data['_id'] = str(res.inserted_id)
    return jsonify(data)

@app.route('/api/customer/redeem', methods=['POST'])
def redeem_points():
    data = request.json
    username = data.get('username')
    points = int(data.get('points'))
    
    user = db.users.find_one({"username": username})
    if user and user.get("points", 0) >= points:
        db.users.update_one({"username": username}, {"$inc": {"points": -points}})
        return jsonify({"success": True, "new_points": user.get("points", 0) - points})
    return jsonify({"success": False, "error": "Insufficient points"}), 400

@app.route('/api/admin/create', methods=['POST'])
def create_admin():
    data = request.json
    res = db.users.insert_one(data)
    data['_id'] = str(res.inserted_id)
    return jsonify(data)

@app.route('/api/feedback', methods=['POST', 'GET'])
def feedback():
    if request.method == 'POST':
        data = request.json
        data['time'] = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
        db.feedback.insert_one(data)
        return jsonify({"success": True})
    else:
        return jsonify([serialize(f) for f in db.feedback.find().sort("_id", -1)])


@app.route('/api/customer/sales/<username>', methods=['GET'])
def get_customer_sales(username):
    user = db.users.find_one({"username": username})
    if not user: return jsonify([])
    vehicles = [v.get("number", "") if isinstance(v, dict) else v for v in user.get("vehicles", [])]
    if not vehicles: return jsonify([])
    sales = list(db.sales.find({"veh": {"$in": vehicles}}).sort("_id", -1))
    return jsonify([serialize(s) for s in sales])

@app.route('/api/customer/sales', methods=['POST'])
def add_customer_sale():
    data = request.json
    data['time'] = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    # Add points to customer
    amount = float(data.get('amount', 0))
    pts_earned = int(amount // 100) # 1 point per 100 Rs
    db.users.update_one({"username": data.get("username")}, {"$inc": {"points": pts_earned}})
    
    del data['username'] # don't need username in sales collection
    res = db.sales.insert_one(data)
    data['_id'] = str(res.inserted_id)
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=8000, debug=True)
