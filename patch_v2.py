import re

# ==========================================
# 1. UPDATE index.html
# ==========================================
html = open('index.html', 'r', encoding='utf-8').read()

# Fix Pump Modal IDs
html = re.sub(r'<div class="fg"><label>Pump Name</label><input type="text" placeholder="e.g. Pump 9"/></div><div class="fg"><label>Fuel Type</label><select><option>Petrol</option><option>Diesel</option><option>CNG</option><option>EV</option></select></div>', 
              r'<div class="fg"><label>Pump Name</label><input type="text" id="new-pump-name" placeholder="e.g. Pump 9"/></div><div class="fg"><label>Fuel Type</label><select id="new-pump-fuel"><option>Petrol</option><option>Diesel</option><option>CNG</option><option>EV</option></select></div>', html)

# Fix Stock Modal IDs
html = re.sub(r'<div class="fg"><label>Fuel Type</label><select><option>Petrol</option><option>Diesel</option><option>CNG</option></select></div><div class="fg"><label>Quantity \(L or Kg\)</label><input type="number" placeholder="0"/></div>',
              r'<div class="fg"><label>Fuel Type</label><select id="new-stock-fuel"><option>Petrol</option><option>Diesel</option><option>CNG</option></select></div><div class="fg"><label>Quantity (L or Kg)</label><input type="number" id="new-stock-qty" placeholder="0"/></div>', html)
html = re.sub(r'<div class="fg"><label>Supplier</label><select id="new-stock-sup">', r'<div class="fg"><label>Supplier</label><select id="new-stock-supplier">', html)

# Fix Price Modal IDs
html = re.sub(r'<div class="fg"><label><i class="fas fa-droplet" style="color:var\(--accent\)"></i> Petrol \(₹/L\)</label><input type="number" value="96.72" step="0.01"/></div>',
              r'<div class="fg"><label><i class="fas fa-droplet" style="color:var(--accent)"></i> Petrol (₹/L)</label><input type="number" id="upd-price-petrol" value="96.72" step="0.01"/></div>', html)
html = re.sub(r'<div class="fg"><label><i class="fas fa-oil-can" style="color:var\(--blue\)"></i> Diesel \(₹/L\)</label><input type="number" value="89.62" step="0.01"/></div>',
              r'<div class="fg"><label><i class="fas fa-oil-can" style="color:var(--blue)"></i> Diesel (₹/L)</label><input type="number" id="upd-price-diesel" value="89.62" step="0.01"/></div>', html)
html = re.sub(r'<div class="form-actions"><button class="btn btn-pr" onclick="closeM\(\'m-price\'\)"><i class="fas fa-check"></i> Update Prices</button>',
              r'<div class="form-actions"><button class="btn btn-pr" onclick="updatePrices()"><i class="fas fa-check"></i> Update Prices</button>', html)

# Fix Customer Vehicle Modal
cust_veh = """<div class="fg"><label>Vehicle Number</label><input type="text" id="new-cust-veh" placeholder="KA01AB1234"/></div>
      <div class="form-grid">
        <div class="fg"><label>Vehicle Type</label><select id="new-cust-vtype"><option>Car</option><option>Bike</option><option>Truck</option></select></div>
        <div class="fg"><label>Fuel Type</label><select id="new-cust-vfuel"><option>Petrol</option><option>Diesel</option><option>CNG</option></select></div>
      </div>
      <div class="fg"><label>Date Added</label><input type="date" id="new-cust-vdate"/></div>"""
html = re.sub(r'<div class="fg"><label>Vehicle Number</label><input type="text" id="new-cust-veh" placeholder="KA01AB1234"/></div>', cust_veh, html)

# Fix Feedback Modal
html = re.sub(r'<div class="fg"><label>Customer Name</label><input type="text" placeholder="Customer name \(optional\)"/></div><div class="fg"><label>Vehicle No.</label><input type="text" placeholder="KA01AB1234"/></div>',
              r'<div class="fg"><label>Customer Name</label><input type="text" id="new-fb-name" placeholder="Customer name" readonly/></div><div class="fg"><label>Vehicle No.</label><select id="new-fb-veh"></select></div>', html)
html = re.sub(r'<div class="fg"><label>Category</label>\s*<select>', r'<div class="fg"><label>Category</label><select id="new-fb-cat">', html)
html = re.sub(r'<div class="fg"><label>Comments</label><textarea placeholder="Share customer experience..."></textarea></div>', r'<div class="fg"><label>Comments</label><textarea id="new-fb-comment" placeholder="Share customer experience..."></textarea></div>', html)
html = re.sub(r'<button class="btn btn-pr" onclick="closeM\(\'m-fb\'\)"><i class="fas fa-check"></i> Submit Feedback</button>', r'<button class="btn btn-pr" onclick="addFeedback()"><i class="fas fa-check"></i> Submit Feedback</button>', html)

# Add Feedbacks section to Customer Portal
cust_acc = """<!-- Customer Feedbacks -->
    <div class="card" id="cust-fb-view" style="display:none;margin-bottom:20px;">
        <div class="card-hd"><h3><i class="fas fa-star" style="color:var(--yellow)"></i> My Feedbacks</h3></div>
        <div class="card-bd scrollable" id="cust-fb-list"></div>
    </div>"""
html = html.replace('<!-- Customer Account Details -->', cust_acc + '\n    <!-- Customer Account Details -->')
open('index.html', 'w', encoding='utf-8').write(html)


# ==========================================
# 2. UPDATE app.js
# ==========================================
js = open('app.js', 'r', encoding='utf-8').read()

js_additions = """
let activeFbStar = 5;
function setFbStar(n) {
    activeFbStar = n;
    const stars = document.querySelectorAll('#fb-stars .sr');
    stars.forEach((s, i) => {
        if(i < n) s.classList.add('on');
        else s.classList.remove('on');
    });
}

async function addFeedback() {
    const veh = document.getElementById('new-fb-veh').value;
    const cat = document.getElementById('new-fb-cat').value;
    const comment = document.getElementById('new-fb-comment').value;
    const name = document.getElementById('new-fb-name').value;
    
    if(!veh) { alert('Select a vehicle.'); return; }
    if(!comment) { alert('Please enter comments.'); return; }
    
    await fetch(`${API_URL}/feedback`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, veh, rating: activeFbStar, category: cat, comment, time: new Date().toLocaleDateString()})
    });
    
    alert('Feedback submitted successfully!');
    closeM('m-fb');
    fetchData(); // reload
    
    // Refresh customer view if customer
    if(document.getElementById('login-role').value === 'customer') {
        const u = document.getElementById('lu').value.trim();
        const p = document.getElementById('lp').value.trim();
        doLogin(); // Refresh login state
    }
}

async function addCustomerVehicle() {
    const veh = document.getElementById('new-cust-veh').value;
    const type = document.getElementById('new-cust-vtype').value;
    const fuel = document.getElementById('new-cust-vfuel').value;
    const date = document.getElementById('new-cust-vdate').value;
    const username = document.getElementById('lu').value.trim();
    
    if(!veh) { alert("Enter a vehicle number."); return; }
    
    await fetch(`${API_URL}/customer/vehicle`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, vehicle: {number: veh, type, fuel, date}})
    });
    
    alert("Vehicle added successfully!");
    closeM('m-cust');
    doLogin(); // refresh
}

async function togglePump(id, currentStatus) {
    const newStatus = currentStatus === 'active' ? 'idle' : 'active';
    await fetch(`${API_URL}/pumps/${id}/status`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({status: newStatus})
    });
    fetchData();
}

function updatePrices() {
    const p = document.getElementById('upd-price-petrol').value;
    const d = document.getElementById('upd-price-diesel').value;
    FUEL_RATES['Petrol'] = parseFloat(p);
    FUEL_RATES['Diesel'] = parseFloat(d);
    alert('Prices updated!');
    closeM('m-price');
}

// Override modal opening to set current date
const oldOpenM = openM;
openM = function(id) {
    oldOpenM(id);
    if(id === 'm-cust') {
        document.getElementById('new-cust-vdate').valueAsDate = new Date();
    }
    if(id === 'm-fb') {
        const vSel = document.getElementById('new-fb-veh');
        if(vSel && window.CUST_VEHICLES) {
            vSel.innerHTML = window.CUST_VEHICLES.map(v => `<option value="${v.number}">${v.number} (${v.type})</option>`).join('');
        }
        document.getElementById('new-fb-name').value = document.getElementById('s-name').textContent;
        setFbStar(5);
    }
}
"""

js = js.replace('// --- END NEW FUNCTIONS ---', js_additions + '\n// --- END NEW FUNCTIONS ---')

# Update login logic to fetch vehicles properly
login_rep = """if(data.role === 'customer') {
              window.CUST_VEHICLES = data.vehicles || [];
              goto('customer-portal');
              document.querySelectorAll('.sidebar .nav-item').forEach(n => {
                  if(n.dataset.page !== 'customer-portal' && n.dataset.page !== 'feedback') n.style.display = 'none';
              });
              document.getElementById('cust-name-disp').textContent = data.name;
              document.getElementById('cust-pts-disp').textContent = data.points;
              document.getElementById('cust-veh-disp').textContent = window.CUST_VEHICLES.map(v => v.number).join(', ') || 'None';
              document.getElementById('cust-acc-view').style.display = 'block';
              
              // Render feedbacks
              if(data.feedbacks && data.feedbacks.length > 0) {
                  document.getElementById('cust-fb-view').style.display = 'block';
                  document.getElementById('cust-fb-list').innerHTML = data.feedbacks.map(f => `
                      <div class="fb-card">
                          <div class="fb-hd">
                              <div><strong>${f.veh}</strong> <span class="bdg bdg-b">${f.category}</span></div>
                              <div class="fb-stars">${'★'.repeat(f.rating)}${'☆'.repeat(5-f.rating)}</div>
                          </div>
                          <div class="fb-text">${f.comment}</div>
                          <div style="font-size:0.7rem;color:gray;margin-top:5px">${f.time}</div>
                      </div>
                  `).join('');
              } else {
                  document.getElementById('cust-fb-view').style.display = 'none';
              }
          }"""
js = re.sub(r'if\(data\.role === \'customer\'\) \{.*?(?= else \{)', login_rep, js, flags=re.DOTALL)
open('app.js', 'w', encoding='utf-8').write(js)

# ==========================================
# 3. UPDATE server.py
# ==========================================
py = open('server.py', 'r', encoding='utf-8').read()
py_additions = """
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
"""
py = py.replace("@app.route('/api/pumps/<id>', methods=['DELETE'])", py_additions + "\n@app.route('/api/pumps/<id>', methods=['DELETE'])")

# Update login to fetch customer feedbacks and structured vehicles
py_login_old = """if user.get("role") == "customer":
            resp["points"] = user.get("points", 0)
            resp["vehicles"] = user.get("vehicles", [])
            resp["username"] = user.get("username")"""
py_login_new = """if user.get("role") == "customer":
            resp["points"] = user.get("points", 0)
            resp["vehicles"] = user.get("vehicles", [])
            resp["username"] = user.get("username")
            feedbacks = list(db.feedback.find({"name": user.get("name")}).sort("_id", -1))
            for f in feedbacks:
                f['_id'] = str(f['_id'])
            resp["feedbacks"] = feedbacks"""
py = py.replace(py_login_old, py_login_new)
open('server.py', 'w', encoding='utf-8').write(py)

print("Patching V2 Complete.")
