import os
import json

log_path = r'C:\Users\hegde\.gemini\antigravity\brain\7a47ed8e-31ae-4461-af68-edc28d21c947\.system_generated\logs\overview.txt'
if not os.path.exists(log_path):
    print('Log not found')
else:
    with open(log_path, 'r', encoding='utf-8') as f:
        found = False
        for line in f:
            try:
                data = json.loads(line)
                content = data.get('content', '')
                if '<!DOCTYPE html>' in content and 'const ctx=document.getElemen' in content:
                    start_idx = content.find('<!DOCTYPE html>')
                    end_idx = content.find('const ctx=document.getElemen')
                    
                    html = content[start_idx:end_idx + len('const ctx=document.getElemen')]
                    
                    rest_of_js = '''tById('revChart').getContext('2d');
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
function switchRevChart(mode, el) {
  revMode = mode;
  document.querySelectorAll('#revChart').forEach(e => e.parentElement.previousElementSibling.querySelectorAll('.tab').forEach(t => t.classList.remove('active')));
  el.classList.add('active');
  if(!charts.rev) return;
  if(mode === 'revenue') {
    charts.rev.data.datasets[0].label = 'Revenue (₹)';
    charts.rev.data.datasets[0].data = rnd(35000, 55000, 14);
    charts.rev.data.datasets[0].borderColor = '#f97316';
    charts.rev.data.datasets[0].backgroundColor = 'rgba(249,115,22,0.1)';
  } else {
    charts.rev.data.datasets[0].label = 'Volume (L)';
    charts.rev.data.datasets[0].data = rnd(1200, 2500, 14);
    charts.rev.data.datasets[0].borderColor = '#3b82f6';
    charts.rev.data.datasets[0].backgroundColor = 'rgba(59,130,246,0.1)';
  }
  charts.rev.update();
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

function setReportPeriod(period, el) {
  document.querySelectorAll('#report-tabs .tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  // Mock data update based on period
  const mult = period === 'daily' ? 1 : period === 'weekly' ? 7 : 30;
  document.getElementById('rpt-rev').textContent = '₹' + (48320 * mult).toLocaleString();
  document.getElementById('rpt-vol').textContent = (1840 * mult).toLocaleString() + ' L';
  document.getElementById('rpt-txn').textContent = (214 * mult).toLocaleString();
  initReportCharts();
}

// Persist Dark Theme
const savedTheme = localStorage.getItem('petrosync-theme');
if (savedTheme === 'light') {
  document.documentElement.setAttribute('data-theme', 'light');
  document.getElementById('theme-btn').innerHTML = '<i class="fas fa-sun"></i>';
}
const origToggleTheme = toggleTheme;
toggleTheme = function() {
  origToggleTheme();
  if (document.documentElement.getAttribute('data-theme') === 'light') {
    localStorage.setItem('petrosync-theme', 'light');
  } else {
    localStorage.setItem('petrosync-theme', 'dark');
  }
}

// Extra Features: Export to CSV for transactions
function exportTransactionsCSV() {
  let csvContent = "data:text/csv;charset=utf-8,";
  csvContent += "ID,Fuel,Vehicle,Qty,Rate,Amount,Pump,Payment,Time,By\\n";
  txList.forEach(t => {
    let amount = (t.qty * t.rate).toFixed(2);
    csvContent += `${t.id},${t.fuel},${t.veh},${t.qty},${t.rate},${amount},${t.pump},${t.pay},${t.time},${t.by}\\n`;
  });
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "transactions_export.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Setup Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    const btn = document.querySelector('#p-transactions .btn-sc');
    if (btn) btn.addEventListener('click', exportTransactionsCSV);
});

function initApp(){
  renderPumps();
  renderEmployees();
  renderTx(txList);
  renderAlerts();
  startClock();
  initRevChart();
  
  // Initialize other pages slightly delayed to improve UI load
  setTimeout(() => {
    initPriceChart();
    initFbChart();
    initReportCharts();
  }, 500);
}

// Auto-login for dev (optional)
// doLogin();
</script>
</body>
</html>
'''
                    full_html = html + rest_of_js
                    
                    output_path = r'c:\Users\hegde\OneDrive\Desktop\Smart petrol bunk\petrosync\index.html'
                    with open(output_path, 'w', encoding='utf-8') as out:
                        out.write(full_html)
                    print('Successfully wrote index.html')
                    found = True
                    break
            except Exception:
                pass
        if not found:
            print('Could not find HTML content in log')
