from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import pytz
import os

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_anda'  # Kunci sesi login
DATA_FILE = 'data.txt'

# --- FUNGSI WAKTU WIB ---
def get_wib_time():
    utc_now = datetime.now(pytz.utc)
    wib_tz = pytz.timezone('Asia/Jakarta')
    wib_now = utc_now.astimezone(wib_tz)
    return wib_now.strftime("%d %B %Y %H:%M WIB")

# --- HALAMAN LOGIN ---
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    wib_time = get_wib_time()
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validasi Login
        if username == 'nase' and password == 'sukasari1':
            session['logged_in'] = True
            return redirect(url_for('input_page'))
        else:
            error = 'Username atau Password salah!'
            
    return render_template('login.html', time=wib_time, error=error)

# --- HALAMAN INPUT (DASHBOARD) ---
@app.route('/input', methods=['GET', 'POST'])
def input_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # 1. LOGIKA SIMPAN DATA BARU
    if request.method == 'POST':
        kategori = request.form['kategori'].strip() # Hapus spasi berlebih
        nama_web = request.form['nama_web'].strip()
        link_web = request.form['link_web'].strip()
        
        # Format data: Kategori|NamaWeb|Link
        new_line = f"{kategori}|{nama_web}|{link_web}\n"
        
        current_content = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                current_content = f.readlines()
        
        # Insert di index 0 agar data baru selalu PALING ATAS
        current_content.insert(0, new_line)
        
        with open(DATA_FILE, 'w') as f:
            f.writelines(current_content)
            
        return redirect(url_for('bookmark_page'))

    # 2. LOGIKA BACA KATEGORI UNTUK AUTOCOMPLETE
    existing_categories = set()
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 1 and parts[0].strip():
                    # Ambil bagian nama kategori saja
                    existing_categories.add(parts[0])
    
    # Kirim list kategori yang sudah diurutkan ke template input.html
    return render_template('input.html', categories=sorted(list(existing_categories)))

# --- HALAMAN BOOKMARK ---
@app.route('/bookmark')
def bookmark_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    bookmarks = {}
    # Membaca file data.txt dari atas ke bawah
    # Urutan di dictionary akan mengikuti urutan baris di file txt
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split('|')
                if len(parts) == 3:
                    cat, name, link = parts
                    
                    # Jika kategori belum ada, buat list baru
                    # Ini menjamin kategori yang dibaca duluan akan tampil duluan
                    if cat not in bookmarks:
                        bookmarks[cat] = []
                    bookmarks[cat].append({'name': name, 'link': link})
    
    return render_template('bookmark.html', bookmarks=bookmarks)

# --- API BACKEND: PINDAHKAN POSISI KE ATAS (PERMANEN) ---
@app.route('/move_top', methods=['POST'])
def move_top():
    if not session.get('logged_in'):
        return jsonify({'status': 'error'}), 403

    data = request.json
    target_type = data.get('type') # 'category' atau 'link'
    cat_name = data.get('category')
    link_url = data.get('link') 

    if not os.path.exists(DATA_FILE):
        return jsonify({'status': 'error', 'message': 'File not found'}), 404

    with open(DATA_FILE, 'r') as f:
        lines = f.readlines()

    moved_lines = []
    remaining_lines = []

    if target_type == 'category':
        # LOGIKA PERMANEN KATEGORI:
        # Cari semua baris yang memiliki nama kategori tersebut
        # Pindahkan ke list 'moved_lines', sisanya ke 'remaining_lines'
        print(f"Moving category '{cat_name}' to top.") # Debugging log
        
        for line in lines:
            parts = line.strip().split('|')
            # Cek apakah bagian pertama (kategori) cocok
            if len(parts) >= 1 and parts[0] == cat_name:
                moved_lines.append(line)
            else:
                remaining_lines.append(line)
                
    elif target_type == 'link':
        # LOGIKA PERMANEN LINK:
        # Pindahkan satu baris spesifik ke paling atas
        print(f"Moving link '{link_url}' to top.") # Debugging log
        
        for line in lines:
            parts = line.strip().split('|')
            # Cek kecocokan Kategori DAN Link agar akurat
            if len(parts) == 3 and parts[0] == cat_name and parts[2] == link_url:
                moved_lines.append(line)
            else:
                remaining_lines.append(line)

    # Gabungkan: Data yang dipindah ditaruh paling awal + sisa data di bawahnya
    new_content = moved_lines + remaining_lines

    # Tulis ulang file data.txt (Simpan Permanen)
    with open(DATA_FILE, 'w') as f:
        f.writelines(new_content)

    return jsonify({'status': 'success'})

# --- LOGOUT ---
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Gunakan host='0.0.0.0' agar bisa diakses dari perangkat lain dalam jaringan yang sama
    app.run(debug=True, host='0.0.0.0', port=5000)