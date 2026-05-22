from flask import Flask, render_template, request, jsonify
import math
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'kalkulatorpro'

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