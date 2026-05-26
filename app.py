"""
KalkulatorPRO v1.0 - Flask Backend
Retro Y2K / Vintage Mac OS Aesthetic Calculator
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import math
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.secret_key = 'kalkulatorpro-retro-y2k-2026'

history_store = []

EXCHANGE_RATES = {
    'USD': 16250, 'EUR': 17800, 'SGD': 12100,
    'JPY': 108, 'MYR': 3650, 'GBP': 20500
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/aritmatika', methods=['POST'])
def aritmatika():
    data = request.get_json()
    a = data.get('a'); b = data.get('b'); op = data.get('op', '+')
    try:
        a = float(a)
        if op != '√': b = float(b)
    except (TypeError, ValueError):
        return jsonify({'error': 'Input harus berupa angka!'}), 400

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
    
    # Simpan ke history dengan format yang diminta
    history_store.append({
        'formula': formula,
        'result': str(result)
    })
    
    return jsonify({'result': result, 'formula': formula, 'steps': steps})

@app.route('/api/logika', methods=['POST'])
def logika():
    data = request.get_json()
    mode = data.get('mode', 'gate')  # 'gate' atau 'bitwise'
    op = data.get('op', 'AND')
    
    if mode == 'gate':
        a_raw = data.get('a')
        b_raw = data.get('b')
        try:
            a = int(a_raw)
            if a not in (0, 1):
                raise ValueError
            if op != 'NOT':
                b = int(b_raw)
                if b not in (0, 1):
                    raise ValueError
            else:
                b = 0
        except (TypeError, ValueError):
            return jsonify({'error': 'Input gerbang logika harus bernilai 0 atau 1!'}), 400
        
        # Operasi logika 1-bit standard
        if op == 'AND':
            result = a & b
        elif op == 'OR':
            result = a | b
        elif op == 'NOT':
            result = 1 if a == 0 else 0
        elif op == 'XOR':
            result = a ^ b
        elif op == 'NAND':
            result = 1 if (a & b) == 0 else 0
        elif op == 'NOR':
            result = 1 if (a | b) == 0 else 0
        elif op == 'XNOR':
            result = 1 if (a ^ b) == 0 else 0
        else:
            return jsonify({'error': f'Operasi "{op}" tidak dikenal!'}), 400

        formula = f'{a} {op} {b}' if op != 'NOT' else f'NOT {a}'
        steps = [
            f'Mode: Jaringan Gerbang Logika 1-Bit ({op})',
            f'Variabel A: {a}',
        ]
        if op != 'NOT':
            steps.append(f'Variabel B: {b}')
        steps.append(f'Mengevaluasi logika: {formula}')
        steps.append(f'Evaluasi selesai. Hasil Output biner: {result}')

        history_store.append({'formula': formula, 'result': str(result)})
        return jsonify({'result': result, 'formula': formula, 'steps': steps})

    else:
        # Mode Bitwise Multi-Bit
        a_raw = data.get('a')
        b_raw = data.get('b')
        try:
            width = int(data.get('width', 8))
            if width not in (8, 16, 32):
                width = 8
        except (TypeError, ValueError):
            width = 8

        try:
            a = int(a_raw)
            if op != 'NOT':
                b = int(b_raw)
            else:
                b = 0
        except (TypeError, ValueError):
            return jsonify({'error': 'Input harus berupa bilangan bulat!'}), 400

        mask = (1 << width) - 1
        
        # Terapkan operasi bitwise & mask agar hasilnya unsigned dan sesuai ukuran bit
        if op == 'AND':
            result = (a & b) & mask
        elif op == 'OR':
            result = (a | b) & mask
        elif op == 'NOT':
            result = (~a) & mask
        elif op == 'XOR':
            result = (a ^ b) & mask
        elif op == 'NAND':
            result = (~(a & b)) & mask
        elif op == 'NOR':
            result = (~(a | b)) & mask
        elif op == 'XNOR':
            result = (~(a ^ b)) & mask
        else:
            return jsonify({'error': f'Operasi "{op}" tidak dikenal!'}), 400

        formula = f'{a} {op} {b} ({width}-bit)' if op != 'NOT' else f'NOT {a} ({width}-bit)'
        
        # Representasi biner dengan padding sesuai lebar bit
        bin_format = f'0{width}b'
        bin_a = format(a & mask, bin_format)
        bin_b = format(b & mask, bin_format)
        bin_result = format(result, bin_format)

        steps = [
            f'Mode: Bitwise kalkulator {width}-bit ({op})',
            f'Representasi biner A ({a}): {bin_a}',
        ]
        if op != 'NOT':
            steps.append(f'Representasi biner B ({b}): {bin_b}')
        
        steps.append(f'Mengeksekusi operasi bitwise per bit...')
        steps.append(f'Evaluasi selesai. Hasil biner: {bin_result}')
        steps.append(f'Hasil desimal: {result}')

        history_store.append({'formula': formula, 'result': str(result)})
        return jsonify({'result': result, 'formula': formula, 'steps': steps})

@app.route('/api/basis', methods=['POST'])
def basis_bilangan():
    data = request.get_json()
    value = data.get('value', '').strip(); basis = data.get('basis', 'Desimal')
    try:
        bases = {'Desimal': 10, 'Biner': 2, 'Oktal': 8, 'Heksadesimal': 16}
        num = int(value, bases.get(basis, 10))
    except (ValueError, KeyError):
        return jsonify({'error': f'Nilai "{value}" tidak valid untuk basis {basis}!'}), 400

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

@app.route('/api/suhu', methods=['POST'])
def konversi_suhu():
    data = request.get_json()
    value = data.get('value'); unit = data.get('unit', 'Celsius')
    try: value = float(value)
    except (TypeError, ValueError): return jsonify({'error': 'Input harus berupa angka!'}), 400

    to_c = {'Celsius': lambda v: v, 'Fahrenheit': lambda v: (v-32)*5/9, 'Kelvin': lambda v: v-273.15, 'Reamur': lambda v: v*5/4}
    if unit not in to_c: return jsonify({'error': f'Satuan "{unit}" tidak dikenal!'}), 400
    c = to_c[unit](value)
    results = {'celsius': round(c,2), 'fahrenheit': round(c*9/5+32,2), 'kelvin': round(c+273.15,2), 'reamur': round(c*4/5,2)}
    formula = f'{value}° {unit}'
    
    steps = [
        f'Menyiapkan konversi temperatur',
        f'Input: {value} derajat {unit}',
        f'Menormalisasi nilai ke Celsius: {round(c, 2)}°C',
        f'Menghitung proporsi ke Fahrenheit, Kelvin, dan Reamur...',
        f'Evaluasi selesai.'
    ]
    
    history_store.append({'formula': formula, 'result': f'{results["celsius"]}°C'})
    return jsonify({'results': results, 'formula': formula, 'steps': steps})

@app.route('/api/matauang', methods=['POST'])
def konversi_mata_uang():
    data = request.get_json()
    try: idr = float(data.get('value'))
    except (TypeError, ValueError): return jsonify({'error': 'Input harus berupa angka!'}), 400
    if idr < 0: return jsonify({'error': 'Nilai tidak boleh negatif!'}), 400

    results = {k.lower(): round(idr / v, 2) for k, v in EXCHANGE_RATES.items()}
    formula = f'Rp {idr:,.0f}'
    
    steps = [
        f'Menyiapkan konversi valuta asing',
        f'Nilai dasar (IDR): Rp {idr:,.0f}',
        f'Mengambil kurs valuta saat ini...'
    ]
    for k, v in EXCHANGE_RATES.items():
        steps.append(f'Rate {k}: Rp {v:,}')
    steps.append('Menghitung ekuivalensi...')
    steps.append('Evaluasi selesai.')
    
    history_store.append({'formula': formula, 'result': f'${results["usd"]}'})
    return jsonify({'results': results, 'formula': formula, 'steps': steps})

@app.route('/api/faktorial', methods=['POST'])
def faktorial():
    data = request.get_json()
    try: n = int(data.get('value'))
    except (TypeError, ValueError): return jsonify({'error': 'Input harus bilangan bulat!'}), 400
    if n < 0: return jsonify({'error': 'Tidak bisa untuk bilangan negatif!'}), 400
    if n > 170: return jsonify({'error': 'Maksimal 170!'}), 400

    result = math.factorial(n)
    formula = f'{n}!'
    
    steps = [
        f'Menyiapkan fungsi faktorial (n!)',
        f'Nilai n = {n}',
        f'Melakukan iterasi perkalian mundur (n × n-1 × ... × 1)',
        f'Evaluasi selesai. Hasil: {result}'
    ]
    
    history_store.append({'formula': formula, 'result': str(result)})
    return jsonify({'result': str(result), 'formula': formula, 'steps': steps})

@app.route('/api/fibonacci', methods=['POST'])
def fibonacci():
    data = request.get_json()
    try: n = int(data.get('value'))
    except (TypeError, ValueError): return jsonify({'error': 'Input harus bilangan bulat!'}), 400
    if n < 1: return jsonify({'error': 'Minimal 1 suku!'}), 400
    if n > 50: return jsonify({'error': 'Maksimal 50 suku!'}), 400

    fib = []; a, b = 0, 1
    for _ in range(n):
        fib.append(a); a, b = b, a + b

    formula = f'Fibonacci({n})'
    steps = [
        f'Menyiapkan deret Fibonacci',
        f'Menargetkan jumlah {n} suku pertama',
        f'Menetapkan nilai awal: F(0) = 0, F(1) = 1',
        f'Menerapkan rumus rekursif F(n) = F(n-1) + F(n-2)...',
        f'Evaluasi selesai.'
    ]
    history_store.append({'formula': formula, 'result': str(fib[-1])})
    return jsonify({'result': fib, 'formula': formula, 'steps': steps})

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify({'history': history_store}) # Do not reverse here, we will render it top-down like terminal

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    history_store.clear()
    return jsonify({'message': 'History berhasil dihapus!'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
