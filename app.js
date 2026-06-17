const API_URL = 'http://localhost:8000/api';

let PUMPS = [];
let EMPS = [];
let TXNS = [];
let ALERTS = [];
let STOCK = [];
const FUEL_RATES={Petrol:96.72,Diesel:89.62,CNG:85.00,EV:12.00};

async function fetchData() {
    try {
        const [pRes, eRes, sRes, aRes, stRes] = await Promise.all([
            fetch(`${API_URL}/pumps`),
            fetch(`${API_URL}/employees`),
            fetch(`${API_URL}/sales`),
            fetch(`${API_URL}/alerts`),
            fetch(`${API_URL}/stock`)
        ]);
        PUMPS = await pRes.json() || [];
        EMPS = await eRes.json() || [];
        TXNS = await sRes.json() || [];
        ALERTS = await aRes.json() || [];
        STOCK = await stRes.json() || [];
        
        renderPumps();
        renderEmployees();
        renderTx(TXNS);
        renderAlerts();
        renderStock();
        if(typeof fetchStockHistory === 'function') fetchStockHistory();
    } catch (e) {
        console.error("Error fetching data:", e);
    }
}

// ═══════════════════════════════════════
// AUTH
// ═══════════════════════════════════════
async function doLogin(){
  const u=document.getElementById('lu').value.trim();
  const p=document.getElementById('lp').value.trim();
  const err=document.getElementById('login-err');
  
  try {
      const res = await fetch(`${API_URL}/login`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({username: u, password: p})
      });
      if(res.ok) {
          const data = await res.json();
          err.classList.remove('show');
          document.getElementById('login-page').classList.remove('active');
          document.getElementById('login-page').style.display='none';
          document.getElementById('app').style.display='block';
          document.getElementById('s-av').textContent=data.name[0].toUpperCase();
          document.getElementById('s-name').textContent=data.name;
          document.getElementById('s-role').textContent=data.role === 'admin' ? 'Administrator' : data.role === 'manager' ? 'Station Manager' : 'Customer';
          document.getElementById('dash-name').textContent=data.name;
          initApp();
          if(data.role === 'customer') {
              window.CUST_VEHICLES = data.vehicles || [];
              goto('customer-portal');
              document.querySelectorAll('.sidebar .nav-item').forEach(n => {
                  if(n.dataset.page !== 'customer-portal' && n.dataset.page !== 'feedback') n.style.display = 'none';
              });
              document.querySelectorAll('.s-section').forEach(s => s.style.display = 'none');
              fetchCustomerTx(data.username);
              document.getElementById('cust-name-disp').textContent = data.name;
              document.getElementById('cust-pts-disp').textContent = data.points;
              document.getElementById('cust-veh-disp').textContent = window.CUST_VEHICLES.map(v => typeof v === 'object' ? (v.number || '') : v).join(', ') || 'None';
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
          } else {
              document.querySelectorAll('.sidebar .nav-item').forEach(n => n.style.display = 'flex');
              document.querySelector('.sidebar .nav-item[data-page="customer-portal"]').style.display = 'none';
              document.querySelectorAll('.s-section').forEach(s => s.style.display = 'block');
              if(data.role === 'manager') {
                  document.getElementById('btn-create-admin').style.display = 'flex';
              }
              goto('dashboard');
          }
      } else {
          throw new Error('Invalid');
      }
  } catch(e) {
      err.classList.add('show');
      document.querySelector('.login-card').style.animation='shake .4s ease';
      setTimeout(()=>document.querySelector('.login-card').style.animation='',400);
  }
}

function doLogout(){
  document.getElementById('app').style.display='none';
  document.getElementById('login-page').style.display='flex';
  document.getElementById('login-page').classList.add('active');
}
function togglePw(){
  const inp=document.getElementById('lp');
  const ic=document.getElementById('pw-eye').querySelector('i');
  inp.type=inp.type==='password'?'text':'password';
  ic.className=inp.type==='password'?'fas fa-eye':'fas fa-eye-slash';
}
document.addEventListener('keydown',e=>{if(e.key==='Enter'&&document.getElementById('login-page').classList.contains('active')) doLogin();});

// ═══════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════
const PAGE_TITLES={
  dashboard:'Dashboard',pumps:'Pump Management','fuel-stock':'Fuel Stock',
  'fuel-prices':'Fuel Prices',transactions:'Transactions',employees:'Employees',
  alerts:'Alerts & Notifications',feedback:'Customer Feedback',
  'customer-portal':'Customer Portal',receipt:'Receipt Generator',reports:'Reports & Analytics'
};
function goto(id,el){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  const pg=document.getElementById('p-'+id);
  if(pg) pg.classList.add('active');
  if(el){el.classList.add('active');}else{
    const found=document.querySelector(`.nav-item[data-page="${id}"]`);
    if(found) found.classList.add('active');
  }
  document.getElementById('pg-title').textContent=PAGE_TITLES[id]||id;
  if(id==='reports'){setTimeout(initReportCharts,120);}
  if(id==='fuel-prices'){setTimeout(initPriceChart,120);}
  if(id==='feedback'){setTimeout(initFbChart,120);}
}
function toggleSidebar(){
  document.getElementById('sidebar').classList.toggle('collapsed');
  document.getElementById('main').classList.toggle('expanded');
}
function toggleTheme(){
  const html=document.documentElement;
  const btn=document.getElementById('theme-btn');
  if(html.getAttribute('data-theme')==='light'){
    html.removeAttribute('data-theme');
    btn.innerHTML='<i class="fas fa-moon"></i>';
  }else{
    html.setAttribute('data-theme','light');
    btn.innerHTML='<i class="fas fa-sun"></i>';
  }
}

// ═══════════════════════════════════════
// MODALS
// ═══════════════════════════════════════
function openM(id){
    if(id === 'm-stock'){
        document.getElementById('new-stock-inv').value = 'INV-' + new Date().toISOString().slice(0,10).replace(/-/g,'') + '-' + Math.floor(Math.random()*10000);
    }
    if(id === 'm-pump'){
        // populate op dropdown
        const sel = document.getElementById('new-pump-op');
        sel.innerHTML = '<option value="">-- Select Operator --</option>' + EMPS.map(e => `<option>${e.name}</option>`).join('');
    }
    document.getElementById(id).classList.add('open');
}
function closeM(id){document.getElementById(id).classList.remove('open');}
document.addEventListener('click',e=>{if(e.target.classList.contains('modal-ov')) e.target.classList.remove('open');});

// ═══════════════════════════════════════
// CLOCK + GREETING
// ═══════════════════════════════════════
function startClock(){
  function tick(){
    const now=new Date();
    document.getElementById('clock').textContent=now.toLocaleTimeString('en-IN',{hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false});
    const h=now.getHours();
    const key=h<12?'☀️ Good morning':h<17?'🌤️ Good afternoon':'🌙 Good evening';
    document.getElementById('greeting').textContent=key;
  }
  tick();setInterval(tick,1000);
}

// ═══════════════════════════════════════
// PUMPS
// ═══════════════════════════════════════
function renderPumps(){
  const g=document.getElementById('pump-grid');
  const statusClass={active:'active-pump',idle:'idle-pump',maintenance:'maint-pump'};
  const dotClass={active:'dot-g',idle:'dot-y',maintenance:'dot-r'};
  const statusLabel={active:'Active',idle:'Idle',maintenance:'Maintenance'};
  const statusBdg={active:'bdg-g',idle:'bdg-y',maintenance:'bdg-r'};
  g.innerHTML=PUMPS.map(p=>`
    <div class="pump-card ${statusClass[p.status]}">
      <div class="pump-bg-num">${p.num}</div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <span style="font-weight:700;font-size:.92rem;font-family:'Syne',sans-serif">Pump ${p.num}</span>
        <span class="bdg ${statusBdg[p.status]}"><span class="pump-stat-dot ${dotClass[p.status]}"></span>${statusLabel[p.status]}</span>
      </div>
      <span class="fuel-pill fp-${p.fuel.toLowerCase()}" style="margin-bottom:11px;display:inline-flex">${p.fuel}</span>
      <div class="pump-meter-val">${(p.sales||0).toLocaleString()}<span style="font-size:.8rem;color:var(--text3);font-weight:400"> L</span></div>
      <div class="pump-meta-row">
        <div class="pump-meta-item"><span class="pump-meta-label">Revenue</span><span class="pump-meta-val" style="font-size:.78rem">₹${(p.rev||0).toLocaleString('en-IN',{maximumFractionDigits:0})}</span></div>
      </div>
      <div style="font-size:.74rem;color:var(--text3);margin-top:10px;padding-top:10px;border-top:1px solid var(--border)"><i class="fas fa-user" style="margin-right:5px;color:var(--blue)"></i>${p.operator}</div>
      <div class="pump-actions">
        <button class="btn btn-sm" style="flex:1;justify-content:center" onclick="togglePump('${p._id}', '${p.status}')">
          ${p.status==='active'?'<i class="fas fa-pause"></i> Set Idle':'<i class="fas fa-play"></i> Activate'}
        </button>
        <div class="btn-ic" title="Settings" onclick="openPumpSettings('${p._id}', ${p.sales||0}, ${p.rev||0})"><i class="fas fa-cog"></i></div>
        <div class="btn-ic dn" title="Delete" onclick="deletePump('${p._id}')"><i class="fas fa-trash"></i></div>
      </div>
    </div>
  `).join('');
  
  // Also update tx-pump dropdown
  const pumpSelects = document.querySelectorAll('#tx-pump, #r-pump');
  pumpSelects.forEach(sel => {
      if(sel) sel.innerHTML = PUMPS.map(p => `<option value="${p.num}">Pump ${p.num} — ${p.fuel}</option>`).join('');
  });
}

async function deletePump(id) {
    if(confirm("Are you sure you want to delete this pump?")) {
        await fetch(`${API_URL}/pumps/${id}`, { method: 'DELETE' });
        fetchData();
    }
}

// ═══════════════════════════════════════
// EMPLOYEES
// ═══════════════════════════════════════
function renderEmployees(){
  const g=document.getElementById('emp-grid');
  const roleBdg={Manager:'bdg-o',Worker:'bdg-b',Accountant:'bdg-p',Security:'bdg-r',Supervisor:'bdg-t',Cashier:'bdg-g'};
  g.innerHTML=EMPS.map(e=>`
    <div class="emp-card">
      <div class="emp-av" style="background:${e.color||'#3b82f6'}">${e.name[0]}</div>
      <div class="emp-info">
        <div class="emp-name">${e.name}</div>
        <div class="emp-role" style="margin-bottom:7px">
          <span class="bdg ${roleBdg[e.role]||'bdg-b'}">${e.role}</span>
          <span class="bdg ${e.status==='on_duty'?'bdg-g':'bdg-y'}" style="margin-left:5px"><span style="width:6px;height:6px;border-radius:50%;background:${e.status==='on_duty'?'var(--green)':'var(--yellow)'};display:inline-block;margin-right:3px"></span>${e.status==='on_duty'?'On Duty':'Off Duty'}</span>
        </div>
        <div class="emp-meta">
          <div class="emp-meta-row"><i class="fas fa-phone"></i>${e.phone}</div>
          <div class="emp-meta-row"><i class="fas fa-pump-soap"></i>Assigned Pump: ${e.pump||'None'}</div>
        </div>
        <div style="margin-top:10px">
          <button class="btn btn-sm" onclick="toggleDuty('${e._id}')">${e.status==='on_duty'?'Mark Off-Duty':'Mark On-Duty'}</button>
        </div>
      </div>
    </div>
  `).join('');
}

async function createAdmin() {
    const name = document.getElementById('new-admin-name').value;
    const user = document.getElementById('new-admin-user').value;
    const pass = document.getElementById('new-admin-pass').value;
    const role = document.getElementById('new-admin-role').value;
    if(!name || !user || !pass) { alert('Please fill all fields'); return; }
    
    await fetch(`${API_URL}/admin/create`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name: name, username: user, password: pass, role: role})
    });
    
    alert('Admin/Manager created successfully!');
    closeM('m-admin');
}

// ═══════════════════════════════════════
// TRANSACTIONS
// ═══════════════════════════════════════
function renderTx(list){
  const fp={Petrol:'fp-petrol',Diesel:'fp-diesel',CNG:'fp-cng',EV:'fp-ev'};
  document.getElementById('tx-body').innerHTML=list.map((t, i)=>`
    <tr>
      <td class="mono">#${i+1}</td>
      <td><span class="fuel-pill ${fp[t.fuel]||'fp-petrol'}">${t.fuel}</span></td>
      <td style="font-weight:600">${t.veh}</td>
      <td>${t.qty}${t.fuel==='CNG'?'Kg':t.fuel==='EV'?'kWh':'L'}</td>
      <td class="muted">₹${parseFloat(t.rate).toFixed(2)}</td>
      <td class="amt">₹${parseFloat(t.amount).toFixed(2)}</td>
      <td class="muted">Pump ${t.pump}</td>
      <td><span class="bdg ${t.payment==='Cash'?'bdg-g':t.payment==='UPI'?'bdg-b':'bdg-p'}">${t.payment}</span></td>
      <td class="muted">${t.time}</td>
      <td class="muted">${t.by}</td>
    </tr>
  `).join('');
}
function filterTx(q){const l=TXNS.filter(t=>t.veh.toLowerCase().includes(q.toLowerCase())||t.fuel.toLowerCase().includes(q.toLowerCase()));renderTx(l);}
function filterTxFuel(f){const l=f?TXNS.filter(t=>t.fuel===f):TXNS;renderTx(l);}

function txFuelChange(){
  const sel=document.getElementById('tx-fuel');
  const fuel=sel.value;
  document.getElementById('tx-rate').value=FUEL_RATES[fuel]||0;
  calcTx();
}
function calcTx(){
  const qty=parseFloat(document.getElementById('tx-qty').value)||0;
  const rate=parseFloat(document.getElementById('tx-rate').value)||0;
  const fuel=document.getElementById('tx-fuel').value;
  const unit=fuel==='CNG'?'Kg':fuel==='EV'?'kWh':'L';
  const total=qty*rate;
  document.getElementById('tx-total').textContent='₹'+total.toLocaleString('en-IN',{minimumFractionDigits:2,maximumFractionDigits:2});
  document.getElementById('tx-breakdown').textContent=`${qty.toFixed(2)} ${unit} × ₹${rate.toFixed(2)} =`;
}
function clearTx(){
  document.getElementById('tx-qty').value='';
  document.getElementById('tx-veh').value='';
  document.getElementById('tx-total').textContent='₹0.00';
  document.getElementById('tx-breakdown').textContent='0.00 L × ₹96.72 =';
}
async function recordSale(){
  const fuel=document.getElementById('tx-fuel').value;
  const qty=parseFloat(document.getElementById('tx-qty').value)||0;
  const rate=parseFloat(document.getElementById('tx-rate').value)||0;
  const veh=(document.getElementById('tx-veh').value||'WALK-IN').toUpperCase();
  const pump=document.getElementById('tx-pump').value;
  const pay=document.getElementById('tx-pay').value;
  if(!qty){alert('Please enter quantity!');return;}
  
  const data = { fuel, qty, rate, amount: qty*rate, veh, pump, payment: pay, by: document.getElementById('dash-name').textContent };
  
  await fetch(`${API_URL}/sales`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
  });
  
  alert('Sale recorded successfully!');
  clearTx();
  fetchData();
}

// ═══════════════════════════════════════
// STOCK
// ═══════════════════════════════════════
function renderStock() {
    const g = document.getElementById('stock-grid');
    if(!g || STOCK.length === 0) return;
    
    const conf = {
        'Petrol': { icon: 'droplet', color: 'accent', track: 'pf-o', capacity: 5000 },
        'Diesel': { icon: 'oil-can', color: 'blue', track: 'pf-b', capacity: 5000 },
        'CNG': { icon: 'wind', color: 'green', track: 'pf-r', capacity: 2000, unit: 'Kg' },
        'EV': { icon: 'bolt', color: 'purple', track: 'pf-p', capacity: 4, unit: 'Bays' }
    };
    
    g.innerHTML = STOCK.map(s => {
        let fId = s.fuel.toLowerCase();
        if (fId === 'ev') fId = 'ev'; // just in case
        const disp = document.getElementById('disp-price-' + fId);
        if(disp) disp.textContent = '₹' + s.price.toFixed(2);
        
        const c = conf[s.fuel] || conf['Petrol'];
        const unit = c.unit || 'Litres';
        const pct = Math.min(100, Math.round((s.qty / c.capacity) * 100)) || 0;
        const isCritical = s.qty <= s.threshold && s.threshold > 0;
        const bdgClass = isCritical ? 'bdg-r' : 'bdg-g';
        const bdgIcon = isCritical ? 'exclamation-triangle' : 'check';
        const bdgText = isCritical ? 'Critical' : 'Sufficient';
        const valColor = isCritical ? 'var(--red)' : 'var(--text)';
        const cardStyle = isCritical ? 'border-color:rgba(239,68,68,.3)' : '';
        const notice = isCritical ? `<div style="font-size:.72rem;color:var(--red);margin-top:10px;display:flex;justify-content:space-between;align-items:center"><span><i class="fas fa-exclamation-triangle" style="margin-right:4px"></i>Alert sent to supplier! Awaiting delivery.</span><span onclick="this.parentElement.style.display='none'" style="cursor:pointer;background:rgba(239,68,68,.1);padding:2px 5px;border-radius:4px" title="Dismiss Alert"><i class="fas fa-times"></i></span></div>` : '';
        
        return `
        <div class="card hover-rise" style="${cardStyle}">
            <div class="card-hd">
                <h3 style="color:var(--${c.color})"><i class="fas fa-${c.icon}"></i> ${s.fuel}</h3>
                <span class="bdg ${bdgClass}"><i class="fas fa-${bdgIcon}"></i> ${bdgText}</span>
            </div>
            <div class="card-bd">
                <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:${valColor}">${s.qty.toLocaleString()} <span style="font-size:.9rem;color:var(--text3);font-weight:400">${unit}</span></div>
                <div class="prog-track" style="margin:8px 0"><div class="prog-fill ${c.track}" style="width:${pct}%"></div></div>
                <div style="display:flex;justify-content:space-between;font-size:.72rem;color:var(--text3);margin-bottom:14px">
                    <span style="${isCritical ? 'color:var(--red)' : ''}">${s.threshold > 0 ? 'Min: '+s.threshold+(unit==='Kg'?'Kg':'L') : ''}</span><span>Capacity: ${c.capacity.toLocaleString()}${unit==='Kg'?'Kg':unit==='Bays'?' Bays':'L'}</span>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-bottom:12px">
                    <div class="stat-box"><span class="stat-val" style="color:var(--${c.color})">₹${s.price.toFixed(2)}</span><span class="stat-lbl">${s.fuel==='EV'?'Per kWh': 'Price/'+(unit==='Kg'?'Kg':'Litre')}</span></div>
                    <div class="stat-box"><span class="stat-val" style="color:var(--${isCritical?'red':'green'})">₹${((s.qty * s.price)/1000).toFixed(1)}k</span><span class="stat-lbl">${s.fuel==='EV'?'Today':'Stock Value'}</span></div>
                </div>
                ${s.fuel==='EV' ? `<div style="font-size:.72rem;color:var(--text3)"><i class="fas fa-clock" style="margin-right:4px"></i>Avg charge time: 42 min · Last Updated: ${s.last_refill || 'N/A'}</div>` :
                `<div style="font-size:.72rem;color:var(--text3)"><i class="fas fa-clock" style="margin-right:4px"></i>Last Updated: ${s.last_refill || 'N/A'} · Supplier: ${s.supplier || 'N/A'}</div>`}
                ${notice}
                ${s.fuel!=='EV' ? `
                <div style="display:flex;gap:7px;margin-top:13px">
                    <button class="btn btn-sm ${isCritical ? 'btn-pr' : 'pr'}" style="${isCritical?'width:100%':'flex:1'};justify-content:center" onclick="openM('m-stock')"><i class="fas fa-fill-drip"></i> ${isCritical ? 'Emergency Refill' : 'Refill'}</button>
                    ${!isCritical ? `<button class="btn btn-sm" style="flex:1;justify-content:center" onclick="openStockSettings('${s.fuel}', ${s.qty}, ${s.threshold})"><i class="fas fa-edit"></i> Settings</button>` : ''}
                </div>` : `
                <div style="display:flex;gap:7px;margin-top:13px">
                    <button class="btn btn-sm" style="flex:1;justify-content:center" onclick="openStockSettings('${s.fuel}', ${s.qty}, ${s.threshold})"><i class="fas fa-edit"></i> Settings</button>
                </div>
                `}
            </div>
        </div>
        `;
    }).join('');
}

// ═══════════════════════════════════════
// ALERTS TIMELINE
// ═══════════════════════════════════════
function renderAlerts(){
  document.getElementById('alert-tl').innerHTML=ALERTS.map(a=>`
    <div class="tl-item">
      <div class="tl-dot ${a.type==='critical'?'r':'y'}"><i class="fas fa-exclamation-circle"></i></div>
      <div class="tl-body">
        <div class="tl-title">${a.message}</div>
      </div>
      <button class="btn-sm" style="align-self:flex-start;margin-top:5px" onclick="clearAlert('${a._id}')">Clear</button>
    </div>
  `).join('');
}

async function clearAlert(id) {
    await fetch(`${API_URL}/alerts/${id}`, { method: 'DELETE' });
    fetchData();
}

// ═══════════════════════════════════════
// RECEIPT
// ═══════════════════════════════════════
function updateReceipt(){
  const fuel=document.getElementById('r-fuel').value;
  const qty=parseFloat(document.getElementById('r-qty').value)||0;
  const rate=parseFloat(document.getElementById('r-rate').value)||0;
  const veh=document.getElementById('r-veh').value||'—';
  const cust=document.getElementById('r-cust').value||'Walk-in';
  const pump=document.getElementById('r-pump').value;
  const pay=document.getElementById('r-pay').value;
  const gstPct=parseFloat(document.getElementById('r-gst').value)||0;
  const unit=fuel==='CNG'?'Kg':fuel==='EV'?'kWh':'L';
  const subtotal=qty*rate;
  const gstAmt=subtotal*gstPct/100;
  const total=subtotal+gstAmt;
  document.getElementById('r-show-dt').textContent=new Date().toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'})+' · '+new Date().toLocaleTimeString('en-IN',{hour:'2-digit',minute:'2-digit'});
  document.getElementById('r-show-cust').textContent=cust;
  document.getElementById('r-show-veh').textContent=veh;
  document.getElementById('r-show-fuel').textContent=fuel;
  document.getElementById('r-show-qty').textContent=qty.toFixed(2)+' '+unit;
  document.getElementById('r-show-rate').textContent='₹'+rate.toFixed(2)+' / '+unit;
  document.getElementById('r-show-pump').textContent='Pump '+pump;
  document.getElementById('r-show-pay').textContent=pay;
  const gstRow=document.getElementById('r-gst-row');
  if(gstPct>0){
    gstRow.style.display='flex';
    document.getElementById('r-show-gstp').textContent=gstPct;
    document.getElementById('r-show-gst').textContent='₹'+gstAmt.toFixed(2);
  }else{gstRow.style.display='none';}
  document.getElementById('r-show-total').textContent='₹'+total.toLocaleString('en-IN',{minimumFractionDigits:2,maximumFractionDigits:2});
}
function clearReceipt(){
  document.getElementById('r-qty').value=30;
  document.getElementById('r-rate').value=96.72;
  document.getElementById('r-veh').value='KA01AB1234';
  document.getElementById('r-cust').value='Ravi Kumar';
  document.getElementById('r-gst').value=0;
  updateReceipt();
}

function downloadReceiptPDF() {
    const element = document.getElementById('receipt-prev');
    html2pdf().from(element).save('petrosync-receipt.pdf');
}

function shareReceipt() {
    if (navigator.share) {
        navigator.share({
            title: 'PetroSync Receipt',
            text: 'Here is your fuel receipt.',
            url: window.location.href,
        }).catch(console.error);
    } else {
        alert("Web Share API is not supported in your browser.");
    }
}

// ═══════════════════════════════════════
// SEARCH
// ═══════════════════════════════════════
function globalSearch(q) {
    if (!q) return;
    // Just a mocked global search
    alert("Searching for: " + q);
}

// Bind PDF and Share in Receipt
document.addEventListener('DOMContentLoaded', () => {
    const pdfBtn = document.querySelector('#p-receipt .btn-pr');
    if(pdfBtn) pdfBtn.addEventListener('click', downloadReceiptPDF);
    
    const shareBtn = document.querySelector('#p-receipt .btn-bl');
    if(shareBtn) shareBtn.addEventListener('click', shareReceipt);
    
    const searchInput = document.querySelector('.topbar-search input');
    if(searchInput) {
        searchInput.addEventListener('keydown', (e) => {
            if(e.key === 'Enter') globalSearch(e.target.value);
        });
    }
});


// ═══════════════════════════════════════
// CHARTS & INIT
// ═══════════════════════════════════════
let charts={};
const chartDefaults={
  responsive:true,maintainAspectRatio:false,
  plugins:{legend:{labels:{color:'#8fa3c8',font:{family:"'DM Sans'",size:11},boxWidth:10}}},
};
function mkLabels14(){const l=[];const n=new Date();for(let i=13;i>=0;i--){const d=new Date(n);d.setDate(d.getDate()-i);l.push(d.toLocaleDateString('en-IN',{day:'2-digit',month:'short'}));}return l;}
function rnd(a,b,n){return Array.from({length:n},()=>Math.round(Math.random()*(b-a)+a));}

function initRevChart(){
  if(charts.rev) return;
  const ctx=document.getElementById('revChart').getContext('2d');
  charts.rev = new Chart(ctx, {
    type: 'line',
    data: {
      labels: mkLabels14(),
      datasets: [{
        label: 'Revenue (₹)',
        data: rnd(35000, 55000, 14),
        borderColor: '#f97316',
        backgroundColor: 'rgba(249,115,22,0.1)',
        fill: true,
        tension: 0.4
      }]
    },
    options: chartDefaults
  });
}
function initPriceChart(){
  if(charts.price) return;
  const ctx=document.getElementById('priceChart').getContext('2d');
  charts.price = new Chart(ctx, {
    type: 'line',
    data: {
      labels: Array.from({length:30}, (_,i)=>i+1),
      datasets: [
        {label:'Petrol', data:rnd(95, 98, 30), borderColor:'#f97316', tension:0.2},
        {label:'Diesel', data:rnd(88, 91, 30), borderColor:'#3b82f6', tension:0.2}
      ]
    },
    options: chartDefaults
  });
}
function initFbChart(){
  if(charts.fb) return;
  const ctx=document.getElementById('fbChart').getContext('2d');
  charts.fb = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
      datasets: [{label:'Avg Rating', data:[4.2,4.5,4.6,4.4,4.7,4.8,4.7], backgroundColor:'#10b981'}]
    },
    options: chartDefaults
  });
}
function initReportCharts(){
  if(charts.rpt) charts.rpt.destroy();
  if(charts.pie) charts.pie.destroy();
  
  const ctx1=document.getElementById('rptChart').getContext('2d');
  charts.rpt = new Chart(ctx1, {
    type: 'bar',
    data: {
      labels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
      datasets: [
        {label:'Petrol', data:rnd(15000,25000,7), backgroundColor:'#f97316'},
        {label:'Diesel', data:rnd(10000,18000,7), backgroundColor:'#3b82f6'},
        {label:'CNG', data:rnd(1000,3000,7), backgroundColor:'#10b981'}
      ]
    },
    options: { ...chartDefaults, scales: { x: { stacked: true }, y: { stacked: true } } }
  });

  const ctx2=document.getElementById('rptPie').getContext('2d');
  charts.pie = new Chart(ctx2, {
    type: 'doughnut',
    data: {
      labels: ['Petrol','Diesel','CNG'],
      datasets: [{data:[58,37,5], backgroundColor:['#f97316','#3b82f6','#10b981']}]
    },
    options: { responsive:true, maintainAspectRatio:false, plugins: { legend: { display: false } } }
  });
}

const savedTheme = localStorage.getItem('petrosync-theme');
if (savedTheme === 'light') {
  document.documentElement.setAttribute('data-theme', 'light');
  const btn = document.getElementById('theme-btn');
  if(btn) btn.innerHTML = '<i class="fas fa-sun"></i>';
}

function initApp(){
  fetchData();
  startClock();
  initRevChart();
  
  setTimeout(() => {
    initPriceChart();
    initFbChart();
    initReportCharts();
  }, 500);
}

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

async function redeemPoints() {
    const pts = prompt("How many points would you like to redeem?");
    const username = document.getElementById('lu').value.trim();
    if(!pts || isNaN(pts) || parseInt(pts) <= 0) return;
    
    try {
        const res = await fetch(`${API_URL}/customer/redeem`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: username, points: parseInt(pts)})
        });
        if(res.ok) {
            const data = await res.json();
            alert(`Successfully redeemed ${pts} points! Remaining balance: ${data.new_points}`);
            document.getElementById('cust-pts-disp').textContent = data.new_points;
        } else {
            alert('Insufficient points or invalid request.');
        }
    } catch(e) {
        console.error(e);
    }
}

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

function openPriceModal() {
    const p = STOCK.find(s => s.fuel === 'Petrol');
    const d = STOCK.find(s => s.fuel === 'Diesel');
    const c = STOCK.find(s => s.fuel === 'CNG');
    const e = STOCK.find(s => s.fuel === 'EV');
    if(p) document.getElementById('upd-price-petrol').value = p.price;
    if(d) document.getElementById('upd-price-diesel').value = d.price;
    if(c) document.getElementById('upd-price-cng').value = c.price;
    if(e) document.getElementById('upd-price-ev').value = e.price;
    openM('m-price');
}

async function savePrices() {
    const p = document.getElementById('upd-price-petrol').value;
    const d = document.getElementById('upd-price-diesel').value;
    const c = document.getElementById('upd-price-cng').value;
    const e = document.getElementById('upd-price-ev').value;
    
    await fetch(`${API_URL}/stock/price`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'Petrol': p, 'Diesel': d, 'CNG': c, 'EV': e})
    });
    
    alert('Prices updated immediately!');
    closeM('m-price');
    fetchData(); // Refresh UI
}

// Override modal opening to set current date
const oldOpenM = openM;
openM = function(id) {
    oldOpenM(id);
    if(id === 'm-cust') {
        document.getElementById('new-cust-vdate').valueAsDate = new Date();
    }
    if(id === 'm-cust-tx') {
        const vSel = document.getElementById('new-ctx-veh');
        if(vSel && window.CUST_VEHICLES) {
            vSel.innerHTML = window.CUST_VEHICLES.map(v => `<option value="${v.number}">${v.number} (${v.type})</option>`).join('');
        }
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

// --- END NEW FUNCTIONS ---

async function fetchStockHistory() {
    try {
        const res = await fetch(`${API_URL}/stock/history`);
        if(res.ok) {
            const history = await res.json();
            const tbody = document.getElementById('stock-hist-list');
            if(tbody) {
                if(history.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center">No history found</td></tr>';
                } else {
                    tbody.innerHTML = history.map(h => `
                        <tr>
                            <td class="muted">${h.time}</td>
                            <td><span class="fuel-pill fp-${h.fuel.toLowerCase()}">${h.fuel}</span></td>
                            <td><span class="bdg bdg-${h.type === 'refill' ? 'g' : 'r'}">${h.type === 'refill' ? '+Refill' : '–Sale'}</span></td>
                            <td style="font-weight:700;color:var(--${h.type === 'refill' ? 'green' : 'red'})">${h.type === 'refill' ? '+' : '-'}${h.qty} L</td>
                            <td>${h.supplier || h.pump || 'N/A'}</td>
                            <td>--</td>
                            <td>admin</td>
                        </tr>
                    `).join('');
                }
            }
        }
    } catch (e) {
        console.error(e);
    }
}

function globalSearch(query) {
    if(!query) return;
    const q = query.toLowerCase();
    if(q.includes('pump')) goto('pumps');
    else if(q.includes('stock') || q.includes('fuel')) goto('fuel-stock');
    else if(q.includes('price')) goto('fuel-prices');
    else if(q.includes('sale') || q.includes('transaction')) goto('transactions');
    else if(q.includes('receipt')) goto('receipt');
    else if(q.includes('report') || q.includes('analytic')) goto('reports');
}

function openStockSettings(fuel, qty, threshold) {
    document.getElementById('cfg-fuel').value = fuel;
    document.getElementById('cfg-fuel-name').textContent = fuel;
    document.getElementById('cfg-qty').value = qty;
    document.getElementById('cfg-threshold').value = threshold;
    openM('m-stock-settings');
}

async function saveStockSettings() {
    const fuel = document.getElementById('cfg-fuel').value;
    const qty = document.getElementById('cfg-qty').value;
    const threshold = document.getElementById('cfg-threshold').value;
    
    try {
        await fetch(`${API_URL}/stock/adjust`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({fuel, qty, threshold})
        });
        alert(fuel + ' stock overrides saved successfully!');
        closeM('m-stock-settings');
        fetchData();
    } catch (e) {
        console.error("Failed to update stock:", e);
    }
}

function filterFeedback(tag) {
    document.querySelectorAll('#fb-filter-tags button').forEach(btn => btn.style.background = 'var(--bg3)');
    event.target.style.background = 'var(--blue)';
    
    document.querySelectorAll('.fb-card').forEach(card => {
        if(tag === 'All') {
            card.style.display = 'block';
            return;
        }
        let found = false;
        card.querySelectorAll('.fb-tags .bdg').forEach(t => {
            if(t.textContent.includes(tag)) found = true;
        });
        card.style.display = found ? 'block' : 'none';
    });
}

function openPumpSettings(id, sales, rev) {
    document.getElementById('cfg-pump-id').value = id;
    document.getElementById('cfg-pump-sales').value = sales;
    document.getElementById('cfg-pump-rev').value = rev;
    openM('m-pump-settings');
}

async function savePumpSettings() {
    const id = document.getElementById('cfg-pump-id').value;
    const sales = document.getElementById('cfg-pump-sales').value;
    const rev = document.getElementById('cfg-pump-rev').value;
    
    try {
        await fetch(`${API_URL}/pumps/adjust`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({id, sales, rev})
        });
        alert('Pump overrides saved successfully!');
        closeM('m-pump-settings');
        fetchData();
    } catch (e) {
        console.error("Failed to update pump:", e);
    }
}
