/* ═══════════════════════════════════════════════════
   KalkulatorPRO v1.0 — Main JavaScript
   ═══════════════════════════════════════════════════ */

// ─── STATE (Penyimpanan Status Klien) ───
// Menyimpan tab yang saat ini aktif secara default
let activeTab = 'aritmatika';
// Menyimpan operator terpilih untuk masing-masing kategori kalkulator
let activeOp = { aritmatika: '+', logika: 'AND' };
// Menyimpan pilihan tema pengguna (gelap/terang), mengambil dari localStorage jika ada
let currentTheme = localStorage.getItem('kpro-theme') || 'light';

// State tambahan untuk simulator logika & gerbang biner
let activeLogicMode = 'gate';
let gateInputA = 0;
let gateInputB = 0;

// ─── INIT (Inisialisasi Halaman saat DOM Siap) ───
document.addEventListener('DOMContentLoaded', () => {
  // Terapkan tema yang tersimpan di memori lokal browser
  applyTheme(currentTheme);
  // Alihkan antarmuka default ke tab Aritmatika
  switchTab('aritmatika');
  // Ambil dan tampilkan riwayat kalkulasi dari backend server
  loadHistory();
  // Daftarkan event listener klik untuk ikon-ikon di sidebar
  bindSidebarIcons();
  
  // Inisialisasi visual simulator gerbang logika 1-bit
  updateGateSimulation();
});

// ─── THEME (Pengaturan Tema Gelap / Terang) ───
/**
 * Menerapkan tema visual ke seluruh aplikasi kalkulator
 * @param {string} theme - Nama tema ('light' atau 'dark')
 */
function applyTheme(theme) {
  currentTheme = theme;
  // Menyetel atribut data-theme di tingkat tag HTML paling atas (documentElement)
  document.documentElement.setAttribute('data-theme', theme);
  // Menyimpan preferensi tema pengguna ke penyimpanan lokal browser
  localStorage.setItem('kpro-theme', theme);
  // Memperbarui ikon emoji tombol toggle tema
  const btn = document.getElementById('themeToggle');
  if (btn) btn.textContent = theme === 'dark' ? '☀️' : '🌙';
}

/**
 * Mengganti tema aplikasi secara bergantian antara terang dan gelap
 */
function toggleTheme() {
  applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
}



// ─── TAB SWITCHING (Pengalihan Halaman Fitur) ───
/**
 * Memindahkan tampilan aktif antar fitur kalkulator
 * @param {string} tab - Id tab target (misal: 'aritmatika', 'logika', 'basis', dll)
 */
function switchTab(tab) {
  activeTab = tab;
  
  // Mengaktifkan kelas CSS 'active' pada tombol navigasi tab yang dipilih
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
  // Menampilkan kontainer konten tab yang dipilih dan menyembunyikan sisanya
  document.querySelectorAll('.tab-content').forEach(c => c.classList.toggle('active', c.id === 'tab-' + tab));
  
  // Memetakan nama judul jendela kalkulator dalam bahasa Inggris
  const titles = {
    aritmatika: 'Arithmetic', 
    logika: 'Logic', 
    basis: 'Base Conversion',
    suhu: 'Temperature', 
    matauang: 'Kurs / Currency', 
    bonus: 'Bonus Tools'
  };
  // Mengubah label judul di title bar jendela retro kalkulator
  document.getElementById('windowTitle').textContent = titles[tab] || tab;
  
  // Menyelaraskan highlight ikon aktif pada panel sidebar sebelah kanan
  document.querySelectorAll('.sidebar-icon').forEach(s => s.classList.toggle('active', s.dataset.tab === tab));
  // Membersihkan terminal output hasil kalkulasi saat berganti fitur
  clearResult();

  if (tab === 'logika') {
    updateGateSimulation();
  }
}

// ─── SIDEBAR (Panel Kontrol Navigasi Samping) ───
/**
 * Mendaftarkan event click untuk ikon navigasi di bar samping kalkulator
 */
function bindSidebarIcons() {
  document.querySelectorAll('.sidebar-icon').forEach(icon => {
    icon.addEventListener('click', () => {
      const tab = icon.dataset.tab;
      // Khusus tombol 'clear', jalankan fungsi penghapusan riwayat kalkulasi
      if (tab === 'clear') { 
        clearHistory(); 
        return; 
      }
      // Alihkan tab jika tombol biasa diklik
      if (tab) switchTab(tab);
    });
  });
}

// ─── OPERATION SELECT (Pemilihan Operator) ───
/**
 * Mengatur operator matematika/logika yang dipilih oleh pengguna
 * @param {string} category - Kategori kalkulator (misal 'aritmatika' atau 'logika')
 * @param {string} op - Operator terpilih (misal '+', '-', 'AND', 'XOR')
 * @param {HTMLElement} el - Element HTML tombol yang diklik
 */
function selectOp(category, op, el) {
  activeOp[category] = op;
  // Menemukan kontainer tombol operasi terdekat
  const grid = el.closest('.op-grid');
  // Menghapus tanda sorot aktif dari semua tombol di grid operasi tersebut
  grid.querySelectorAll('.op-btn').forEach(b => b.classList.remove('active'));
  // Menyorot tombol yang baru saja diklik
  el.classList.add('active');

  if (category === 'logika') {
    // Sembunyikan/tampilkan input B container tergantung operator NOT
    const containerB = document.getElementById('gateInputBContainer');
    const containerBitB = document.getElementById('logBContainer');
    if (op === 'NOT') {
      if (containerB) containerB.style.display = 'none';
      if (containerBitB) containerBitB.style.display = 'none';
    } else {
      if (containerB) containerB.style.display = '';
      if (containerBitB) containerBitB.style.display = '';
    }
    updateGateSimulation();
  }
}

// ─── CLEAR RESULT (Membersihkan Terminal Output) ───
/**
 * Mereset tampilan terminal utama hasil kalkulasi ke format prompt awal kosong
 */
function clearResult() {
  const terminal = document.getElementById('resultTerminal');
  if (terminal) {
    terminal.innerHTML = '<span class="prefix">&gt; </span><span class="cursor-blink">_</span>';
  }
}

// ─── SHOW RESULT (Menampilkan Hasil Kalkulasi & Log Langkah Pengerjaan) ───
/**
 * Merender daftar log proses eksekusi dan hasil akhir dari respon API ke terminal utama kalkulator
 * @param {Object} data - Objek hasil kalkulasi dari server
 */
function showResult(data) {
  const terminal = document.getElementById('resultTerminal');
  if (!terminal) return;

  let html = '';
  // Jika respon mengandung galat (error), tampilkan pesan kesalahan dengan teks berwarna merah
  if (data.error) {
    html = `<span class="prefix" style="color: #ff6b6b;">&gt; ERROR:</span> <span class="error-text">${data.error}</span>\n<span class="prefix">&gt; </span><span class="cursor-blink">_</span>`;
  } else {
    // Jika ada daftar langkah evaluasi kalkulasi, render setiap langkah secara berurutan
    if (data.steps && data.steps.length) {
      data.steps.forEach(s => { 
        html += `<div class="step-line"><span class="prefix">&gt; </span>${s}</div>`; 
      });
    }
    html += `\n<span class="prefix">&gt; </span><span class="cursor-blink">_</span>`;
  }

  terminal.innerHTML = html;
}

// ─── SHOW BADGES (Merender Kartu Konversi) ───
/**
 * Membuat kartu/badge kecil secara dinamis untuk menampilkan kumpulan hasil konversi simultan
 * @param {string} containerId - Id elemen pembungkus target
 * @param {Object} results - Data hasil perhitungan per unit/basis
 * @param {Object} labels - Label teks ramah pengguna untuk ditampilkan per unit/basis
 */
function showBadges(containerId, results, labels) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = '';
  // Mengiterasi dan merender badge untuk setiap unit konversi
  for (const [key, label] of Object.entries(labels)) {
    const val = results[key] !== undefined ? results[key] : '-';
    container.innerHTML += `
      <div class="result-badge">
        <div class="badge-label">${label}</div>
        <div class="badge-value">${val}</div>
      </div>`;
  }
}

// ─── API CALL (Konektor Asinkronus ke Flask Backend) ───
/**
 * Melakukan pemanggilan HTTP POST ke endpoint backend kalkulator
 * @param {string} endpoint - Path URL rute backend Flask
 * @param {Object} body - Objek parameter yang akan dikirim dalam format JSON
 * @returns {Promise<Object|null>} Kembalian objek JSON dari server atau null jika gagal
 */
async function apiCall(endpoint, body) {
  const terminal = document.getElementById('resultTerminal');
  // Menampilkan indikator pemrosesan di terminal utama saat menunggu respon server
  if (terminal) terminal.innerHTML = '<span class="loading-text" style="color: var(--accent);">Processing</span>';

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    // Tangani skenario kode status respons yang tidak sukses (bukan 2xx)
    if (!res.ok) { 
      showResult({ error: data.error || 'Terjadi kesalahan!' }); 
      return null; 
    }
    return data;
  } catch (err) {
    // Tangani kegagalan koneksi jaringan ke server Flask
    showResult({ error: 'Koneksi gagal!' });
    return null;
  }
}

// ═══ HANDLERS (Fungsi Pengendali Aksi Klik Tombol Hitung) ═══

/**
 * Pemicu kalkulasi Aritmatika dasar/lanjutan.
 * Mengambil input nilai variabel A, variabel B, dan operator aritmatika aktif.
 */
async function hitungAritmatika() {
  const data = await apiCall('/api/aritmatika', { 
    a: document.getElementById('aritA').value, 
    b: document.getElementById('aritB').value, 
    op: activeOp.aritmatika 
  });
  if (data) { 
    showResult(data); 
    loadHistory(); 
  }
}

/**
 * Pemicu kalkulasi logika bitwise (AND, OR, XOR, NOR, dll.).
 * Mengambil input desimal bulat A, B, dan operator logika biner aktif.
 */
async function hitungLogika() {
  let payload = {
    mode: activeLogicMode,
    op: activeOp.logika
  };
  
  if (activeLogicMode === 'gate') {
    payload.a = gateInputA;
    payload.b = activeOp.logika === 'NOT' ? 0 : gateInputB;
  } else {
    payload.a = document.getElementById('logA').value;
    payload.b = activeOp.logika === 'NOT' ? 0 : document.getElementById('logB').value;
    payload.width = document.getElementById('bitWidthSelect').value;
  }
  
  const data = await apiCall('/api/logika', payload);
  if (data) { 
    showResult(data); 
    loadHistory(); 
  }
}

// ─── GATE SIMULATION FUNCTIONS ───

/**
 * Mengubah mode logika antara simulator gerbang 1-bit dan bitwise multi-bit
 */
function setLogicMode(mode) {
  activeLogicMode = mode;
  const gateBtn = document.getElementById('modeGateBtn');
  const bitwiseBtn = document.getElementById('modeBitwiseBtn');
  if (gateBtn) gateBtn.classList.toggle('active', mode === 'gate');
  if (bitwiseBtn) bitwiseBtn.classList.toggle('active', mode === 'bitwise');
  
  const gateSec = document.getElementById('logic-gate-section');
  const bitwiseSec = document.getElementById('logic-bitwise-section');
  if (gateSec) gateSec.style.display = mode === 'gate' ? '' : 'none';
  if (bitwiseSec) bitwiseSec.style.display = mode === 'bitwise' ? '' : 'none';
  
  if (mode === 'gate') {
    updateGateSimulation();
  }
  clearResult();
}

/**
 * Men-toggle nilai input gerbang logika (0 atau 1)
 */
function toggleGateInput(name) {
  if (name === 'A') {
    gateInputA = gateInputA === 0 ? 1 : 0;
    const btn = document.getElementById('gateInputA');
    if (btn) {
      btn.textContent = gateInputA;
      btn.classList.toggle('active', gateInputA === 1);
    }
  } else if (name === 'B') {
    gateInputB = gateInputB === 0 ? 1 : 0;
    const btn = document.getElementById('gateInputB');
    if (btn) {
      btn.textContent = gateInputB;
      btn.classList.toggle('active', gateInputB === 1);
    }
  }
  updateGateSimulation();
}

/**
 * Memperbarui visualisasi gerbang logika (SVG) dan tabel kebenaran secara lokal/instan
 */
function updateGateSimulation() {
  const svg = document.getElementById('gateSvg');
  if (!svg) return;
  
  const op = activeOp.logika;
  const a = gateInputA;
  const b = op === 'NOT' ? 0 : gateInputB;
  let out = 0;
  
  if (op === 'AND') out = a & b;
  else if (op === 'OR') out = a | b;
  else if (op === 'NOT') out = a === 0 ? 1 : 0;
  else if (op === 'XOR') out = a ^ b;
  else if (op === 'NAND') out = (a & b) === 0 ? 1 : 0;
  else if (op === 'NOR') out = (a | b) === 0 ? 1 : 0;
  else if (op === 'XNOR') out = (a ^ b) === 0 ? 1 : 0;
  
  const classA = a === 1 ? 'gate-svg-wire active' : 'gate-svg-wire inactive';
  const classB = b === 1 ? 'gate-svg-wire active' : 'gate-svg-wire inactive';
  const classOut = out === 1 ? 'gate-svg-wire active' : 'gate-svg-wire inactive';
  
  // Render SVG dinamis berdasarkan tipe gerbang
  if (op === 'AND') {
    svg.innerHTML = `
      <path d="M 20 35 L 60 35" class="${classA}"></path>
      <path d="M 20 65 L 60 65" class="${classB}"></path>
      <path d="M 120 50 L 180 50" class="${classOut}"></path>
      <path d="M 60 20 L 90 20 A 30 30 0 0 1 90 80 L 60 80 Z" class="gate-svg-body"></path>
      <text x="15" y="32" class="gate-svg-text">A</text>
      <text x="15" y="73" class="gate-svg-text">B</text>
      <text x="175" y="46" class="gate-svg-text">Y</text>
      <text x="75" y="54" class="gate-svg-text" style="font-size:12px; fill:var(--titlebar-text);">AND</text>
    `;
  } else if (op === 'OR') {
    svg.innerHTML = `
      <path d="M 20 35 L 56 35" class="${classA}"></path>
      <path d="M 20 65 L 56 65" class="${classB}"></path>
      <path d="M 115 50 L 180 50" class="${classOut}"></path>
      <path d="M 50 20 C 65 20, 85 25, 115 50 C 85 75, 65 80, 50 80 C 60 65, 60 35, 50 20 Z" class="gate-svg-body"></path>
      <text x="15" y="32" class="gate-svg-text">A</text>
      <text x="15" y="73" class="gate-svg-text">B</text>
      <text x="175" y="46" class="gate-svg-text">Y</text>
      <text x="75" y="54" class="gate-svg-text" style="font-size:12px; fill:var(--titlebar-text);">OR</text>
    `;
  } else if (op === 'NOT') {
    svg.innerHTML = `
      <path d="M 20 50 L 60 50" class="${classA}"></path>
      <path d="M 116 50 L 180 50" class="${classOut}"></path>
      <path d="M 60 25 L 100 50 L 60 75 Z" class="gate-svg-body"></path>
      <circle cx="106" cy="50" r="6" class="gate-svg-bubble"></circle>
      <text x="15" y="46" class="gate-svg-text">A</text>
      <text x="175" y="46" class="gate-svg-text">Y</text>
      <text x="70" y="54" class="gate-svg-text" style="font-size:12px; fill:var(--titlebar-text);">NOT</text>
    `;
  } else if (op === 'XOR') {
    svg.innerHTML = `
      <path d="M 20 35 L 50 35" class="${classA}"></path>
      <path d="M 20 65 L 50 65" class="${classB}"></path>
      <path d="M 115 50 L 180 50" class="${classOut}"></path>
      <path d="M 50 20 C 65 20, 85 25, 115 50 C 85 75, 65 80, 50 80 C 60 65, 60 35, 50 20 Z" class="gate-svg-body"></path>
      <path d="M 42 20 C 52 35, 52 65, 42 80" fill="none" stroke="var(--border)" stroke-width="3"></path>
      <text x="15" y="32" class="gate-svg-text">A</text>
      <text x="15" y="73" class="gate-svg-text">B</text>
      <text x="175" y="46" class="gate-svg-text">Y</text>
      <text x="72" y="54" class="gate-svg-text" style="font-size:12px; fill:var(--titlebar-text);">XOR</text>
    `;
  } else if (op === 'NAND') {
    svg.innerHTML = `
      <path d="M 20 35 L 60 35" class="${classA}"></path>
      <path d="M 20 65 L 60 65" class="${classB}"></path>
      <path d="M 132 50 L 180 50" class="${classOut}"></path>
      <path d="M 60 20 L 90 20 A 30 30 0 0 1 90 80 L 60 80 Z" class="gate-svg-body"></path>
      <circle cx="126" cy="50" r="6" class="gate-svg-bubble"></circle>
      <text x="15" y="32" class="gate-svg-text">A</text>
      <text x="15" y="73" class="gate-svg-text">B</text>
      <text x="175" y="46" class="gate-svg-text">Y</text>
      <text x="73" y="54" class="gate-svg-text" style="font-size:12px; fill:var(--titlebar-text);">NAND</text>
    `;
  } else if (op === 'NOR') {
    svg.innerHTML = `
      <path d="M 20 35 L 56 35" class="${classA}"></path>
      <path d="M 20 65 L 56 65" class="${classB}"></path>
      <path d="M 127 50 L 180 50" class="${classOut}"></path>
      <path d="M 50 20 C 65 20, 85 25, 115 50 C 85 75, 65 80, 50 80 C 60 65, 60 35, 50 20 Z" class="gate-svg-body"></path>
      <circle cx="121" cy="50" r="6" class="gate-svg-bubble"></circle>
      <text x="15" y="32" class="gate-svg-text">A</text>
      <text x="15" y="73" class="gate-svg-text">B</text>
      <text x="175" y="46" class="gate-svg-text">Y</text>
      <text x="70" y="54" class="gate-svg-text" style="font-size:12px; fill:var(--titlebar-text);">NOR</text>
    `;
  } else if (op === 'XNOR') {
    svg.innerHTML = `
      <path d="M 20 35 L 50 35" class="${classA}"></path>
      <path d="M 20 65 L 50 65" class="${classB}"></path>
      <path d="M 127 50 L 180 50" class="${classOut}"></path>
      <path d="M 50 20 C 65 20, 85 25, 115 50 C 85 75, 65 80, 50 80 C 60 65, 60 35, 50 20 Z" class="gate-svg-body"></path>
      <path d="M 42 20 C 52 35, 52 65, 42 80" fill="none" stroke="var(--border)" stroke-width="3"></path>
      <circle cx="121" cy="50" r="6" class="gate-svg-bubble"></circle>
      <text x="15" y="32" class="gate-svg-text">A</text>
      <text x="15" y="73" class="gate-svg-text">B</text>
      <text x="175" y="46" class="gate-svg-text">Y</text>
      <text x="68" y="54" class="gate-svg-text" style="font-size:12px; fill:var(--titlebar-text);">XNOR</text>
    `;
  }
  
  // Render Tabel Kebenaran secara lokal
  const table = document.getElementById('gateTruthTable');
  if (table) {
    if (op === 'NOT') {
      let tableHtml = `
        <thead>
          <tr>
            <th>A</th>
            <th>Y</th>
          </tr>
        </thead>
        <tbody>
      `;
      [0, 1].forEach(valA => {
        const valY = valA === 0 ? 1 : 0;
        const isActive = (valA === a);
        tableHtml += `
          <tr class="${isActive ? 'active-row' : ''}">
            <td>${valA}</td>
            <td>${valY}</td>
          </tr>
        `;
      });
      tableHtml += '</tbody>';
      table.innerHTML = tableHtml;
    } else {
      let tableHtml = `
        <thead>
          <tr>
            <th>A</th>
            <th>B</th>
            <th>Y</th>
          </tr>
        </thead>
        <tbody>
      `;
      const rows = [
        { a: 0, b: 0 },
        { a: 0, b: 1 },
        { a: 1, b: 0 },
        { a: 1, b: 1 }
      ];
      rows.forEach(r => {
        let valY = 0;
        if (op === 'AND') valY = r.a & r.b;
        else if (op === 'OR') valY = r.a | r.b;
        else if (op === 'XOR') valY = r.a ^ r.b;
        else if (op === 'NAND') valY = (r.a & r.b) === 0 ? 1 : 0;
        else if (op === 'NOR') valY = (r.a | r.b) === 0 ? 1 : 0;
        else if (op === 'XNOR') valY = (r.a ^ r.b) === 0 ? 1 : 0;
        
        const isActive = (r.a === a && r.b === b);
        tableHtml += `
          <tr class="${isActive ? 'active-row' : ''}">
            <td>${r.a}</td>
            <td>${r.b}</td>
            <td>${valY}</td>
          </tr>
        `;
      });
      tableHtml += '</tbody>';
      table.innerHTML = tableHtml;
    }
  }
}

/**
 * Pemicu kalkulasi konversi basis bilangan.
 * Mengirim nilai asal dan nama basis asal ke server, lalu merender outputnya ke badges.
 */
async function hitungBasis() {
  const data = await apiCall('/api/basis', { 
    value: document.getElementById('basisInput').value, 
    basis: document.getElementById('basisSelect').value 
  });
  if (data) {
    showResult(data);
    showBadges('basisBadges', data.results, { desimal: 'Desimal', biner: 'Biner', oktal: 'Oktal', heksadesimal: 'Hex' });
    loadHistory();
  }
}

/**
 * Pemicu kalkulasi konversi temperatur.
 * Mengirim nilai suhu dan unit asal ke server, lalu merender output ke unit Celsius, Fahrenheit, Kelvin, Reamur.
 */
async function hitungSuhu() {
  const data = await apiCall('/api/suhu', { 
    value: document.getElementById('suhuInput').value, 
    unit: document.getElementById('suhuSelect').value 
  });
  if (data) {
    showResult(data);
    showBadges('suhuBadges', data.results, { celsius: 'Celsius', fahrenheit: 'Fahrenheit', kelvin: 'Kelvin', reamur: 'Reamur' });
    loadHistory();
  }
}

/**
 * Pemicu kalkulasi konversi valas (mata uang).
 * Mengirim nominal Rupiah ke server untuk dihitung ekuivalensinya ke USD, EUR, SGD, JPY, MYR, GBP.
 */
async function hitungMataUang() {
  const data = await apiCall('/api/matauang', { value: document.getElementById('idrInput').value });
  if (data) {
    showResult(data);
    showBadges('currencyBadges', data.results, { usd: 'USD', eur: 'EUR', sgd: 'SGD', jpy: 'JPY', myr: 'MYR', gbp: 'GBP' });
    loadHistory();
  }
}

/**
 * Pemicu kalkulasi faktorial (Bonus).
 * Mengirim nilai n ke backend dan menuliskan log langkah faktorial secara eksklusif ke terminal faktorial.
 */
async function hitungFaktorial() {
  const data = await apiCall('/api/faktorial', { value: document.getElementById('faktInput').value });
  if (data) {
    const t = document.getElementById('faktResult');
    if (t) {
      t.innerHTML = data.steps.map(s => `<div class="step-line"><span class="prefix">&gt; </span>${s}</div>`).join('') + `\n<span class="prefix">&gt; </span><span class="cursor-blink">_</span>`;
    }
    loadHistory();
  }
}

/**
 * Pemicu kalkulasi deret Fibonacci (Bonus).
 * Mengirim jumlah suku ke backend dan menuliskan deret angka ke terminal Fibonacci.
 */
async function hitungFibonacci() {
  const data = await apiCall('/api/fibonacci', { value: document.getElementById('fibInput').value });
  if (data) {
    const t = document.getElementById('fibResult');
    if (t) {
      t.innerHTML = data.steps.map(s => `<div class="step-line"><span class="prefix">&gt; </span>${s}</div>`).join('') + `<div class="step-line"><span class="prefix">&gt; </span>Deret: ${Array.isArray(data.result) ? data.result.join(', ') : data.result}</div>\n<span class="prefix">&gt; </span><span class="cursor-blink">_</span>`;
    }
    loadHistory();
  }
}

// ─── HISTORY (Pencatatan Riwayat & Log Sesi) ───

/**
 * Mengambil log riwayat kalkulasi dari backend server dan merendernya secara top-down ke panel Logs.txt
 */
async function loadHistory() {
  try {
    const res = await fetch('/api/history');
    const data = await res.json();
    const list = document.getElementById('historyList');
    if (!list) return;

    // Header awal log sesi kalkulator
    let html = `<div style="color: #668866; margin-bottom: 4px;">* KalkulatorPRO v1.0.42<br>* Session started: ${new Date().toISOString().split('T')[0]}</div>`;
    
    // Tulis setiap baris riwayat yang berhasil diambil dari backend
    if (data.history && data.history.length > 0) {
      data.history.forEach(h => {
        html += `<div class="history-item"><span class="prefix" style="color:var(--terminal-text);">&gt;</span> ${h.formula} = ${h.result}</div>`;
      });
    }
    
    html += `<div style="margin-top:4px;"><span class="prefix" style="color:var(--terminal-text);">&gt;</span> <span class="cursor-blink">_</span></div>`;
    list.innerHTML = html;
    
    // Melakukan gulir otomatis (autoscroll) ke posisi terbawah pada log panel
    const container = list.parentElement;
    container.scrollTop = container.scrollHeight;
  } catch (e) { 
    /* Silent catch: abaikan jika ada galat koneksi saat memuat history */ 
  }
}

/**
 * Mengirim perintah penghapusan riwayat kalkulasi ke backend, lalu memperbarui tampilan panel log
 */
async function clearHistory() {
  await fetch('/api/history', { method: 'DELETE' });
  loadHistory();
}

