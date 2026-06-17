import re

# ==========================================
# 1. UPDATE server.py
# ==========================================
py = open('server.py', 'r', encoding='utf-8').read()

price_endpoint = """
@app.route('/api/stock/price', methods=['PUT'])
def update_stock_price():
    data = request.json
    for fuel, price in data.items():
        db.stock.update_one({"fuel": fuel}, {"$set": {"price": float(price)}})
    return jsonify({"success": True})
"""
if "/api/stock/price" not in py:
    py = py.replace("@app.route('/api/alerts', methods=['GET', 'DELETE'])", price_endpoint + "\n@app.route('/api/alerts', methods=['GET', 'DELETE'])")

open('server.py', 'w', encoding='utf-8').write(py)


# ==========================================
# 2. UPDATE app.js
# ==========================================
js = open('app.js', 'r', encoding='utf-8').read()

update_prices_old = """function updatePrices() {
    const p = document.getElementById('upd-price-petrol').value;
    const d = document.getElementById('upd-price-diesel').value;
    FUEL_RATES['Petrol'] = parseFloat(p);
    FUEL_RATES['Diesel'] = parseFloat(d);
    alert('Prices updated!');
    closeM('m-price');
}"""
update_prices_new = """async function updatePrices() {
    const p = document.getElementById('upd-price-petrol').value;
    const d = document.getElementById('upd-price-diesel').value;
    
    await fetch(`${API_URL}/stock/price`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'Petrol': p, 'Diesel': d})
    });
    
    alert('Prices updated in database!');
    closeM('m-price');
    fetchData(); // Refresh UI
}"""
js = js.replace(update_prices_old, update_prices_new)

stock_history = """
async function fetchStockHistory() {
    try {
        const res = await fetch(`${API_URL}/stock/history`);
        if(res.ok) {
            const history = await res.json();
            const tbody = document.getElementById('stock-hist-list');
            if(tbody) {
                if(history.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center">No history found</td></tr>';
                } else {
                    tbody.innerHTML = history.map(h => `
                        <tr>
                            <td>${h.time}</td>
                            <td><span class="bdg bdg-b">${h.type.toUpperCase()}</span></td>
                            <td style="font-weight:600">${h.fuel}</td>
                            <td>${h.qty} L</td>
                            <td style="color:var(--text3)">${h.supplier || 'N/A'}</td>
                        </tr>
                    `).join('');
                }
            }
        }
    } catch (e) {
        console.error(e);
    }
}

async function resolveAlert(id) {
    if(confirm("Are you sure you want to resolve this alert?")) {
        await fetch(`${API_URL}/alerts/${id}`, { method: 'DELETE' });
        fetchData();
    }
}
"""
if "fetchStockHistory()" not in js:
    js = js.replace('// --- END NEW FUNCTIONS ---', stock_history + '\n// --- END NEW FUNCTIONS ---')

if "fetchStockHistory();" not in js:
    js = js.replace("renderAlerts();\n}", "renderAlerts();\n    fetchStockHistory();\n}")

# Fix alert buttons
if 'onclick="resolveAlert' not in js:
    js = js.replace('<button class="btn btn-sm btn-sc">Resolve</button>', '<button class="btn btn-sm btn-sc" onclick="resolveAlert(\\'${a._id}\\')">Resolve</button>')

open('app.js', 'w', encoding='utf-8').write(js)

# ==========================================
# 3. UPDATE index.html
# ==========================================
idx = open('index.html', 'r', encoding='utf-8').read()

idx = idx.replace('<button class="btn btn-bl" onclick="goto(\\'receipt\\',null)"><i class="fas fa-file-invoice"></i> Preview Receipt</button>',
                  '<button class="btn btn-bl" onclick="previewTxReceipt()"><i class="fas fa-file-invoice"></i> Preview Receipt</button>')

idx = idx.replace('<tbody id="stock-hist">', '<tbody id="stock-hist-list">')

open('index.html', 'w', encoding='utf-8').write(idx)

print("Patching V5 Complete.")
