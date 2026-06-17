import re

# ==========================================
# 1. UPDATE index.html
# ==========================================
html = open('index.html', 'r', encoding='utf-8').read()

# Rename Customer Portal in sidebar to My Account
html = html.replace('<div class="nav-item" data-page="customer-portal" onclick="goto(\'customer-portal\',this)"><i class="fas fa-id-card"></i><span>Customer Portal</span></div>', 
                    '<div class="nav-item" data-page="customer-portal" onclick="goto(\'customer-portal\',this)"><i class="fas fa-home"></i><span>My Account</span></div>')

# Add Customer Transactions Section and Add Transaction Button to Customer Portal
cust_tx_section = """
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;margin-top:24px">
      <h3 style="font-family:'Syne',sans-serif"><i class="fas fa-receipt" style="color:var(--blue)"></i> My Transactions</h3>
      <button class="btn btn-sm btn-pr" onclick="openM('m-cust-tx')"><i class="fas fa-plus"></i> Add Transaction</button>
    </div>
    <div class="card" style="margin-bottom:20px;">
        <div class="tbl-wrap">
            <table class="tbl">
                <thead><tr><th>Date</th><th>Vehicle</th><th>Fuel</th><th>Qty</th><th>Total</th></tr></thead>
                <tbody id="cust-tx-list"><tr><td colspan="5" style="text-align:center">No transactions found</td></tr></tbody>
            </table>
        </div>
    </div>
"""
html = html.replace('<!-- Customer Feedbacks -->', cust_tx_section + '\n    <!-- Customer Feedbacks -->')

# Add Customer Transaction Modal
cust_tx_modal = """
<!-- Customer Tx Modal -->
<div class="modal-ov" id="m-cust-tx">
  <div class="modal">
    <div class="modal-hd"><h3><i class="fas fa-gas-pump" style="color:var(--blue)"></i> Log Transaction</h3><div class="modal-x" onclick="closeM('m-cust-tx')"><i class="fas fa-times"></i></div></div>
    <div style="display:flex;flex-direction:column;gap:12px">
      <div class="fg"><label>Vehicle Number</label><select id="new-ctx-veh"></select></div>
      <div class="form-grid">
        <div class="fg"><label>Fuel Type</label><select id="new-ctx-fuel"><option>Petrol</option><option>Diesel</option><option>CNG</option><option>EV</option></select></div>
        <div class="fg"><label>Quantity (L/Kg/kWh)</label><input type="number" id="new-ctx-qty" placeholder="10"/></div>
      </div>
      <div class="fg"><label>Total Amount Paid (₹)</label><input type="number" id="new-ctx-amt" placeholder="1000"/></div>
      <div class="form-actions"><button class="btn btn-pr" onclick="addCustomerTx()"><i class="fas fa-check"></i> Save Transaction</button><button class="btn btn-sc" onclick="closeM('m-cust-tx')">Cancel</button></div>
    </div>
  </div>
</div>
"""
html = html.replace('<!-- Customer Modal -->', cust_tx_modal + '\n<!-- Customer Modal -->')

open('index.html', 'w', encoding='utf-8').write(html)


# ==========================================
# 2. UPDATE app.js
# ==========================================
js = open('app.js', 'r', encoding='utf-8').read()

# Fix Routing and Sidebar logic in doLogin
login_routing_old = """} else {
              document.querySelector('.sidebar .nav-item[data-page="customer-portal"]').style.display = 'none';
              if(data.role === 'manager') {
                  document.getElementById('btn-create-admin').style.display = 'flex';
              }
          }"""
login_routing_new = """} else {
              document.querySelector('.sidebar .nav-item[data-page="customer-portal"]').style.display = 'none';
              document.querySelectorAll('.s-section').forEach(s => s.style.display = 'block');
              if(data.role === 'manager') {
                  document.getElementById('btn-create-admin').style.display = 'flex';
              }
              goto('dashboard');
          }"""
js = js.replace(login_routing_old, login_routing_new)

# Add logic to hide s-sections for customer
login_cust_old = """if(n.dataset.page !== 'customer-portal' && n.dataset.page !== 'feedback') n.style.display = 'none';
              });"""
login_cust_new = """if(n.dataset.page !== 'customer-portal' && n.dataset.page !== 'feedback') n.style.display = 'none';
              });
              document.querySelectorAll('.s-section').forEach(s => s.style.display = 'none');
              fetchCustomerTx(data.username);"""
js = js.replace(login_cust_old, login_cust_new)

js_additions = """
async function fetchCustomerTx(username) {
    const res = await fetch(`${API_URL}/customer/sales/${username}`);
    if(res.ok) {
        const txs = await res.json();
        const tbody = document.getElementById('cust-tx-list');
        if(txs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center">No transactions found</td></tr>';
        } else {
            tbody.innerHTML = txs.map(t => `
                <tr>
                  <td>${t.time}</td>
                  <td style="font-weight:600">${t.veh}</td>
                  <td><span class="bdg bdg-b">${t.fuel}</span></td>
                  <td>${t.qty}</td>
                  <td style="font-weight:700;color:var(--text)">₹${parseFloat(t.amount).toFixed(2)}</td>
                </tr>
            `).join('');
        }
    }
}

async function addCustomerTx() {
    const veh = document.getElementById('new-ctx-veh').value;
    const fuel = document.getElementById('new-ctx-fuel').value;
    const qty = parseFloat(document.getElementById('new-ctx-qty').value);
    const amount = parseFloat(document.getElementById('new-ctx-amt').value);
    const username = document.getElementById('lu').value.trim();
    
    if(!veh || !qty || !amount) { alert("Please fill all details."); return; }
    
    await fetch(`${API_URL}/customer/sales`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, veh, fuel, qty, amount, rate: (amount/qty).toFixed(2), payment: 'UPI', pump: 'External', by: 'Customer'})
    });
    
    alert("Transaction added successfully!");
    closeM('m-cust-tx');
    fetchCustomerTx(username);
}
"""

js = js.replace('// --- END NEW FUNCTIONS ---', js_additions + '\n// --- END NEW FUNCTIONS ---')

# Update openM to populate the new Customer Transaction modal's vehicles dropdown
openm_old = """if(id === 'm-fb') {"""
openm_new = """if(id === 'm-cust-tx') {
        const vSel = document.getElementById('new-ctx-veh');
        if(vSel && window.CUST_VEHICLES) {
            vSel.innerHTML = window.CUST_VEHICLES.map(v => `<option value="${v.number}">${v.number} (${v.type})</option>`).join('');
        }
    }
    if(id === 'm-fb') {"""
js = js.replace(openm_old, openm_new)

open('app.js', 'w', encoding='utf-8').write(js)

# ==========================================
# 3. UPDATE server.py
# ==========================================
py = open('server.py', 'r', encoding='utf-8').read()

py_additions = """
@app.route('/api/customer/sales/<username>', methods=['GET'])
def get_customer_sales(username):
    user = db.users.find_one({"username": username})
    if not user: return jsonify([])
    vehicles = [v.get("number", "") for v in user.get("vehicles", [])]
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
"""
py = py.replace("if __name__ == '__main__':", py_additions + "\nif __name__ == '__main__':")

open('server.py', 'w', encoding='utf-8').write(py)

print("Patching V3 Complete.")
