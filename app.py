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

# API: Konversi suhu (Celsius, Fahrenheit, Kelvin, Reamur)
@app.route('/api/suhu', methods=['POST'])
def konversi_suhu():
    data = request.get_json()
    value = data.get('value'); unit = data.get('unit', 'Celsius')
    try: value = float(value)
    except (TypeError, ValueError): return jsonify({'error': 'Input harus berupa angka!'}), 400

    # Normalisasi semua satuan ke Celsius terlebih dahulu
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

# API: Konversi mata uang dari IDR ke valuta asing
@app.route('/api/matauang', methods=['POST'])
def konversi_mata_uang():
    data = request.get_json()
    try: idr = float(data.get('value'))
    except (TypeError, ValueError): return jsonify({'error': 'Input harus berupa angka!'}), 400
    if idr < 0: return jsonify({'error': 'Nilai tidak boleh negatif!'}), 400

    # Hitung ekuivalensi IDR ke tiap mata uang asing
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

# API: Menghitung faktorial n! (maks n=170)
@app.route('/api/faktorial', methods=['POST'])
def faktorial():
    data = request.get_json()
    try: n = int(data.get('value'))
    except (TypeError, ValueError): return jsonify({'error': 'Input harus bilangan bulat!'}), 400
    if n < 0: return jsonify({'error': 'Tidak bisa untuk bilangan negatif!'}), 400
    if n > 170: return jsonify({'error': 'Maksimal 170!'}), 400

    result = math.factorial(n)  # Gunakan fungsi bawaan Python
    formula = f'{n}!'
    
    steps = [
        f'Menyiapkan fungsi faktorial (n!)',
        f'Nilai n = {n}',
        f'Melakukan iterasi perkalian mundur (n × n-1 × ... × 1)',
        f'Evaluasi selesai. Hasil: {result}'
    ]
    
    history_store.append({'formula': formula, 'result': str(result)})
    return jsonify({'result': str(result), 'formula': formula, 'steps': steps})  # str agar JS tidak bulatkan

# API: Menghitung deret Fibonacci hingga n suku (maks 50)
@app.route('/api/fibonacci', methods=['POST'])
def fibonacci():
    data = request.get_json()
    try: n = int(data.get('value'))
    except (TypeError, ValueError): return jsonify({'error': 'Input harus bilangan bulat!'}), 400
    if n < 1: return jsonify({'error': 'Minimal 1 suku!'}), 400
    if n > 50: return jsonify({'error': 'Maksimal 50 suku!'}), 400

    # Algoritma iteratif deret Fibonacci
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

# API: Ambil riwayat kalkulasi
@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify({'history': history_store})  # Urutan asli (top-down seperti terminal)

# API: Hapus seluruh riwayat kalkulasi
@app.route('/api/history', methods=['DELETE'])
def clear_history():
    history_store.clear()
    return jsonify({'message': 'History berhasil dihapus!'})

if __name__ == '__main__':
    app.run(debug=True, port=5050)
