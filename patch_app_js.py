import re

# 1. Update index.html
html = open('index.html', 'r', encoding='utf-8').read()

# Remove duplicate modal
html = re.sub(r'<div class="modal-ov" id="m-emp">\s*<div class="modal">\s*<div class="modal-hd"><h3><i class="fas fa-user-plus" style="color:var\(--green\)"></i> Add Employee</h3>.*?</div>\s*</div>\s*</div>', '', html, flags=re.DOTALL)

# Update customer modal to Add Vehicle
cust_modal_new = '''<!-- Customer Modal -->
<div class="modal-ov" id="m-cust">
  <div class="modal">
    <div class="modal-hd"><h3><i class="fas fa-car" style="color:var(--blue)"></i> Add Vehicle</h3><div class="modal-x" onclick="closeM('m-cust')"><i class="fas fa-times"></i></div></div>
    <div style="display:flex;flex-direction:column;gap:12px">
      <div class="fg"><label>Vehicle Number</label><input type="text" id="new-cust-veh" placeholder="KA01AB1234"/></div>
      <div class="form-actions"><button class="btn btn-pr" onclick="addCustomerVehicle()"><i class="fas fa-check"></i> Add</button><button class="btn btn-sc" onclick="closeM('m-cust')">Cancel</button></div>
    </div>
  </div>
</div>'''
html = re.sub(r'<!-- Customer Modal -->.*?</div>\s*</div>\s*</div>', cust_modal_new, html, flags=re.DOTALL)

# Wire Add Pump modal button
html = re.sub(r'<button class="btn btn-pr" onclick="closeM\(\'m-pump\'\)"><i class="fas fa-check"></i> Add Pump</button>', r'<button class="btn btn-pr" onclick="addPump()"><i class="fas fa-check"></i> Add Pump</button>', html)

# Wire Add Stock modal button
html = re.sub(r'<button class="btn btn-pr" onclick="closeM\(\'m-stock\'\)"><i class="fas fa-check"></i> Add Stock</button>', r'<button class="btn btn-pr" onclick="addStock()"><i class="fas fa-check"></i> Add Stock</button>', html)

# Change "Preview Receipt" to do previewTxReceipt
html = re.sub(r'<button class="btn btn-sc" onclick="goto\(\'receipt\'\)"><i class="fas fa-print"></i> Preview Receipt</button>', r'<button class="btn btn-sc" onclick="previewTxReceipt()"><i class="fas fa-print"></i> Preview Receipt</button>', html)

open('index.html', 'w', encoding='utf-8').write(html)

# 2. Update app.js
js = open('app.js', 'r', encoding='utf-8').read()

js_additions = '''
// --- NEW FUNCTIONS ---
async function addPump() {
    const pFuel = document.getElementById('new-pump-fuel').value;
    const pOp = document.getElementById('new-pump-op').value;
    if(!pOp) { alert("Please select an operator"); return; }
    
    // Find next pump num
    const num = PUMPS.length > 0 ? Math.max(...PUMPS.map(p=>p.num)) + 1 : 1;
    
    await fetch(`${API_URL}/pumps`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({num: num, fuel: pFuel, status: 'idle', operator: pOp})
    });
    closeM('m-pump');
    fetchData();
}

async function addStock() {
    const fuel = document.getElementById('new-stock-fuel').value;
    const qty = document.getElementById('new-stock-qty').value;
    const supplier = document.getElementById('new-stock-supplier').value;
    const invoice = document.getElementById('new-stock-inv').value;
    if(!qty) { alert("Enter quantity"); return; }
    
    await fetch(`${API_URL}/stock/refill`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({fuel, qty, supplier, invoice})
    });
    closeM('m-stock');
    fetchData();
}

function previewTxReceipt() {
    const qty = document.getElementById('tx-qty').value;
    const rate = document.getElementById('tx-rate').value;
    const veh = document.getElementById('tx-veh').value;
    const pump = document.getElementById('tx-pump').value;
    const fuel = document.getElementById('tx-fuel').value;
    const pay = document.getElementById('tx-pay').value;
    
    if(!qty) { alert("Enter quantity for the transaction first."); return; }
    
    document.getElementById('r-qty').value = qty;
    document.getElementById('r-rate').value = rate;
    document.getElementById('r-veh').value = veh || 'WALK-IN';
    document.getElementById('r-pump').value = pump;
    document.getElementById('r-fuel').value = fuel;
    document.getElementById('r-pay').value = pay;
    
    updateReceipt();
    goto('receipt');
}

async function addEmployee() {
    const name = document.getElementById('new-emp-name').value;
    const role = document.getElementById('new-emp-role').value;
    const phone = document.getElementById('new-emp-phone').value;
    const pump = document.getElementById('new-emp-pump').value;
    
    if(phone.length !== 10 || isNaN(phone)) { alert("Enter a valid 10-digit mobile number."); return; }
    if(!name) { alert("Enter name."); return; }
    
    await fetch(`${API_URL}/employees`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, role, phone, pump: pump?parseInt(pump):null, status: 'off_duty', color: '#10b981'})
    });
    closeM('m-emp');
    fetchData();
}

async function toggleDuty(id) {
    await fetch(`${API_URL}/employees/${id}/duty`, { method: 'PUT' });
    fetchData();
}

async function loadEmployees(roleFilter, el) {
    if(el) {
        document.querySelectorAll('#emp-tabs .tab').forEach(t => t.classList.remove('active'));
        el.classList.add('active');
    }
    const res = await fetch(`${API_URL}/employees?role=${roleFilter}`);
    EMPS = await res.json();
    renderEmployees();
}

function addCustomerVehicle() {
    alert("Vehicle added to your account! (Mocked)");
    closeM('m-cust');
}

function redeemPoints() {
    alert("Redeeming points logic triggered! (Mocked)");
}
// --- END NEW FUNCTIONS ---
'''

# Update Employee Card to have Toggle Duty button
emp_card_old = '''<div class="emp-meta-row"><i class="fas fa-pump-soap"></i>Assigned Pump: ${e.pump||'None'}</div>
        </div>
      </div>
    </div>'''
emp_card_new = '''<div class="emp-meta-row"><i class="fas fa-pump-soap"></i>Assigned Pump: ${e.pump||'None'}</div>
        </div>
        <div style="margin-top:10px">
          <button class="btn btn-sm" onclick="toggleDuty('${e._id}')">${e.status==='on_duty'?'Mark Off-Duty':'Mark On-Duty'}</button>
        </div>
      </div>
    </div>'''
js = js.replace(emp_card_old, emp_card_new)

js += js_additions

# Update Login Logic to properly display things for customer portal
js = js.replace('''if(data.role === 'customer') {
              goto('customer-portal');
              document.querySelectorAll('.sidebar .nav-item').forEach(n => {
                  if(n.dataset.page !== 'customer-portal') n.style.display = 'none';
              });
          }''', '''if(data.role === 'customer') {
              goto('customer-portal');
              document.querySelectorAll('.sidebar .nav-item').forEach(n => {
                  if(n.dataset.page !== 'customer-portal' && n.dataset.page !== 'feedback') n.style.display = 'none';
              });
              document.getElementById('cust-name-disp').textContent = data.name;
              document.getElementById('cust-pts-disp').textContent = data.points;
              document.getElementById('cust-veh-disp').textContent = data.vehicles.join(', ') || 'None';
              document.getElementById('cust-acc-view').style.display = 'block';
          } else {
              document.querySelector('.sidebar .nav-item[data-page="customer-portal"]').style.display = 'none';
              if(data.role === 'manager') {
                  document.getElementById('btn-create-admin').style.display = 'flex';
              }
          }''')

open('app.js', 'w', encoding='utf-8').write(js)
print("Patched app.js and index.html")
