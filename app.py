from flask import Flask, render_template, request, jsonify
import math
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'kalkulatorpro'

history_store = [] # Menyimpan riwayat kalkulasi selama server berjalan

EXCHANGE_RATES = {
    'USD': 16250, 'EUR': 17800, 'SGD': 12100,
    'JPY': 108, 'MYR': 3650, 'GBP': 20500
}
# Halaman utama
@app.route('/')
def index():
    return render_template('index.html')

# API untuk operasi aritmatika
@app.route('/api/aritmatika', methods=['POST'])
def aritmatika():
    data = request.get_json()
    a = data.get('a'); b = data.get('b'); op = data.get('op', '+')
    try:
        a = float(a)
        if op != '√': b = float(b) # Untuk operasi akar kuadrat, hanya a yang digunakan, b diabaikan saja
    except (TypeError, ValueError):
        return jsonify({'error': 'Input harus berupa angka!'}), 400

    # Definisikan operasi aritmatika dengan langkah-langkah penjelasan yang lebih rinci dan bahasa yang lebih mudah dipahami. Setiap operasi akan memiliki penjelasan langkah demi langkah yang jelas, termasuk penjelasan tentang variabel yang digunakan dan proses perhitungannya.
    ops = {
        '+': lambda: (a + b, f'{a} + {b}', [f'Menyiapkan operasi penjumlahan (+)', f'Variabel A ditetapkan: {a}', f'Variabel B ditetapkan: {b}', f'Mengkalkulasi: {a} ditambah {b}']),
        '-': lambda: (a - b, f'{a} - {b}', [f'Menyiapkan operasi pengurangan (-)', f'Variabel A ditetapkan: {a}', f'Variabel B ditetapkan: {b}', f'Mengkalkulasi: {a} dikurangi {b}']),
        '×': lambda: (a * b, f'{a} × {b}', [f'Menyiapkan operasi perkalian (×)', f'Variabel A ditetapkan: {a}', f'Variabel B ditetapkan: {b}', f'Mengkalkulasi: {a} dikali {b}']),
        '÷': lambda: (a / b, f'{a} ÷ {b}', [f'Menyiapkan operasi pembagian (÷)', f'Variabel A (Pembilang): {a}', f'Variabel B (Penyebut): {b}', f'Mengkalkulasi: {a} dibagi {b}']),
        '^': lambda: (a ** b, f'{a} ^ {b}', [f'Menyiapkan operasi eksponen (^)', f'Variabel A (Basis): {a}', f'Variabel B (Pangkat): {b}', f'Mengkalkulasi: {a} dipangkatkan {b}']),
        '√': lambda: (math.sqrt(a), f'√{a}', [f'Menyiapkan operasi akar kuadrat (√)', f'Variabel A ditetapkan: {a}', f'Mengkalkulasi: akar kuadrat dari {a}']),
        '%': lambda: (a % b, f'{a} mod {b}', [f'Menyiapkan operasi modulo (mod)', f'Variabel A ditetapkan: {a}', f'Variabel B ditetapkan: {b}', f'Mengkalkulasi: sisa bagi {a} dibagi {b}']),
        '//': lambda: (a // b, f'{a} // {b}', [f'Menyiapkan operasi pembagian bulat (//)', f'Variabel A: {a}', f'Variabel B: {b}', f'Mengkalkulasi: hasil bagi bulat {a} dibagi {b}']),
    }
    if op in ('÷', '%', '//') and b == 0:
        return jsonify({'error': 'Tidak bisa membagi dengan nol!'}), 400
    if op == '√' and a < 0:
        return jsonify({'error': 'Tidak bisa akar kuadrat bilangan negatif!'}), 400
    if op not in ops:
        return jsonify({'error': f'Operasi "{op}" tidak dikenal!'}), 400

    result, formula, steps = ops[op]()
    if result == int(result): result = int(result)
    steps.append(f'Evaluasi selesai. Hasil akhir: {result}')
    
    # Simpan ke history 
    history_store.append({
        'formula': formula,
        'result': str(result)
    })
    
    return jsonify({'result': result, 'formula': formula, 'steps': steps})

# API: Operasi logika bitwise (AND, OR, NOT, XOR, NAND, NOR)
@app.route('/api/logika', methods=['POST'])
def logika():
    data = request.get_json()
    a = data.get('a'); b = data.get('b'); op = data.get('op', 'AND')
    try:
        a = int(a)
        if op != 'NOT': b = int(b) # NOT hanya butuh 1 input
    except (TypeError, ValueError):
        return jsonify({'error': 'Input harus berupa bilangan bulat!'}), 400

# Definisikan operasi logika bitwise dengan penjelasan langkah demi langkah yang lebih rinci dan bahasa yang lebih mudah dipahami. Setiap operasi akan memiliki penjelasan langkah demi langkah yang jelas, termasuk penjelasan tentang variabel yang digunakan, representasi biner, dan proses perhitungannya. 
    ops = {
        'AND': lambda: (a & b, f'{a} AND {b}'),
        'OR': lambda: (a | b, f'{a} OR {b}'),
        'NOT': lambda: (~a, f'NOT {a}'),
        'XOR': lambda: (a ^ b, f'{a} XOR {b}'),
        'NAND': lambda: (~(a & b), f'{a} NAND {b}'),
        'NOR': lambda: (~(a | b), f'{a} NOR {b}'),
    }
    if op not in ops:
        return jsonify({'error': f'Operasi "{op}" tidak dikenal!'}), 400
    result, formula = ops[op]()
    
    # Susun langkah-langkah penjelasan biner
    steps = [f'Menyiapkan operasi bitwise {op}']
    steps.append(f'Representasi biner A ({a}): {bin(a)}')
    if op != 'NOT':
        steps.append(f'Representasi biner B ({b}): {bin(b)}')
    
    steps.append(f'Mengeksekusi operasi bit per bit...')
    steps.append(f'Evaluasi selesai. Hasil biner: {bin(result)}')
    steps.append(f'Hasil desimal: {result}')

    history_store.append({'formula': formula, 'result': str(result)})
    return jsonify({'result': result, 'formula': formula, 'steps': steps})

# API: Konversi basis bilangan (Desimal, Biner, Oktal, Heksadesimal)
@app.route('/api/basis', methods=['POST'])
def basis_bilangan():
    data = request.get_json()
    value = data.get('value', '').strip(); basis = data.get('basis', 'Desimal')
    try:
        bases = {'Desimal': 10, 'Biner': 2, 'Oktal': 8, 'Heksadesimal': 16}
        num = int(value, bases.get(basis, 10))  # Ubah ke integer sesuai basis asal
    except (ValueError, KeyError):
        return jsonify({'error': f'Nilai "{value}" tidak valid untuk basis {basis}!'}), 400

    # Konversi ke semua basis target (hapus prefix '0b', '0o', '0x')
    results = {'desimal': str(num), 'biner': bin(num)[2:], 'oktal': oct(num)[2:], 'heksadesimal': hex(num)[2:].upper()}
    formula = f'{value} ({basis})'
    
    steps = [
        f'Menyiapkan konversi dari basis {basis}',
        f'Nilai input: {value}',
        f'Mengonversi ke nilai absolut (desimal): {num}',
        f'Membuat pemetaan ke basis lain...',
        f'Evaluasi selesai.'
    ]
    
    history_store.append({'formula': formula, 'result': f'DEC:{results["desimal"]}'})
    return jsonify({'results': results, 'formula': formula, 'steps': steps})
