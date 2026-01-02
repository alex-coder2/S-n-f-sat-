from flask import Flask, request, redirect, session, url_for, jsonify
import os
import json
import uuid

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'vortex_gizli_anahtar_1453_2025')

# Veri dosyaları
USERS_FILE = "users.json"
ILANLAR_FILE = "ilanlar.json"
BEKLEYEN_ODEMELER_FILE = "bekleyen_odemeler.json"

# Admin şifresi
ADMIN_SIFRE = "Vortex1453"

# IBAN bilgisi
IBAN_BILGISI = """
<b>IBAN:</b> TR350006400000163002969560<br>
<b>Alıcı Adı:</b> Haşim Seviniş<br>
<b>Banka:</b> Garanti BBVA<br><br>
<span style="color:red; font-weight:bold;">
⚠️ Açıklama kısmına MUTLAKA KULLANICI ADINIZI yazın!<br>
Yazmazsanız para geri döner ve ödeme geçersiz sayılır!
</span>
"""

# Karanlık tema CSS (mobil uyumlu)
DARK_STYLE = """
<style>
    body { background:#000; color:#00ff00; font-family: Arial, sans-serif; margin:0; padding:0; min-height:100vh; }
    h1, h2, h3 { color:#00ff41; text-align:center; margin:20px 0; }
    p { line-height:1.6; font-size:16px; }
    a { color:#00ff00; text-decoration:none; }
    input, select { background:#111; color:#00ff00; border:2px solid #00ff00; border-radius:12px; padding:14px; font-size:16px; width:100%; box-sizing:border-box; margin:10px 0; }
    button { background:#00aa00; color:black; font-weight:bold; font-size:18px; padding:16px; border:none; border-radius:12px; cursor:pointer; width:100%; margin:10px 0; }
    button:hover { background:#00ff00; }
    .kart { background:#0a0a0a; border:2px solid #00ff00; border-radius:20px; padding:25px; margin:20px 0; box-shadow:0 0 20px rgba(0,255,0,0.3); }
    .uyari { background:#330000; border:2px solid #ff4444; border-radius:15px; padding:20px; margin:20px 0; }
    footer { color:#006600; text-align:center; padding:30px; font-size:14px; }
    @media (max-width: 600px) { .kart { margin:15px 10px; padding:20px; } body { padding:10px; } }
</style>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
"""

# Veriyi yükle
def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Kullanıcılar
users = load_json(USERS_FILE)

# İlanlar (öne çıkarılanlar önce)
ilanlar = load_json(ILANLAR_FILE)

# Bekleyen ödemeler
bekleyen_odemeler = load_json(BEKLEYEN_ODEMELER_FILE)

# Kullanıcı kaydı
@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        telefon = request.form['telefon'].strip()
        if not username or not password or not telefon:
            return DARK_STYLE + "<div style='text-align:center; padding:100px;'><h2 style='color:#ff4444;'>⚠️ Tüm alanlar zorunlu!</h2><a href='/kayit'>← Geri</a></div>"
        if any(u['username'] == username for u in users):
            return DARK_STYLE + "<div style='text-align:center; padding:100px;'><h2 style='color:#ff4444;'>Kullanıcı adı alınmış!</h2><a href='/kayit'>← Geri</a></div>"
        users.append({
            "username": username,
            "password": password,  # Gerçek hayatta hashle!
            "telefon": telefon,
            "ilan_hakki": 0
        })
        save_json(USERS_FILE, users)
        return redirect('/giris')
    html = DARK_STYLE + "<div style='text-align:center; padding:50px 20px; max-width:400px; margin:auto;'>"
    html += "<h2>Kayıt Ol</h2>"
    html += """
    <form method='post'>
        <input type='text' name='username' placeholder='Kullanıcı Adı' required>
        <input type='password' name='password' placeholder='Şifre' required>
        <input type='tel' name='telefon' placeholder='Telefon Numaran (zorunlu)' required>
        <button type='submit'>Kayıt Ol</button>
    </form>
    <br><a href='/giris'>Giriş Yap</a> | <a href='/'>Ana Sayfa</a>
    </div>
    """
    return html

# Giriş
@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            session['user'] = username
            return redirect('/ilan_ac')
        return DARK_STYLE + "<div style='text-align:center; padding:100px;'><h2 style='color:#ff4444;'>Yanlış kullanıcı veya şifre!</h2><a href='/giris'>← Geri</a></div>"
    html = DARK_STYLE + "<div style='text-align:center; padding:50px 20px; max-width:400px; margin:auto;'>"
    html += "<h2>Giriş Yap</h2>"
    html += """
    <form method='post'>
        <input type='text' name='username' placeholder='Kullanıcı Adı' required>
        <input type='password' name='password' placeholder='Şifre' required>
        <button type='submit'>Giriş Yap</button>
    </form>
    <br><a href='/kayit'>Kayıt Ol</a> | <a href='/'>Ana Sayfa</a>
    </div>
    """
    return html

# Admin giriş
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    hata = None
    if request.method == 'POST':
        if request.form['sifre'] == ADMIN_SIFRE:
            session['admin_logged_in'] = True
            return redirect('/admin')
        else:
            hata = "Yanlış şifre!"
    html = DARK_STYLE + "<div style='text-align:center; padding:100px 20px; max-width:400px; margin:auto;'>"
    html += "<h2>🔐 Admin Girişi</h2>"
    if hata:
        html += f"<p style='color:#ff4444;'>{hata}</p>"
    html += """
    <form method='post'>
        <input type='password' name='sifre' placeholder='Şifre' required>
        <button type='submit'>Giriş Yap</button>
    </form>
    <br><a href='/'>← Ana Sayfa</a>
    </div>
    """
    return html

# Admin panel
@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')

    html = DARK_STYLE + "<div style='max-width:900px; margin:auto; padding:20px;'>"
    html += "<h1>🔐 Admin Paneli</h1>"
    html += "<p style='text-align:center;'><a href='/admin_cikis'>Çıkış yap</a></p>"

    # Bekleyen ödemeler
    html += "<h2>Bekleyen Ödemeler</h2>"
    for o in bekleyen_odemeler:
        html += f"<div class='kart'>"
        html += f"<p>Kullanıcı: {o['username']}</p>"
        html += f"<form action='/onayla_odeme/{o['id']}' method='post'><button type='submit'>Onayla (İlan Hakkı Ver)</button></form>"
        html += "</div>"

    # İlanlar yönetimi
    html += "<h2>İlanlar</h2>"
    for i in ilanlar:
        one_cikar = 'Öne Çıkarılmış' if i['one_cikar'] else ''
        html += f"<div class='kart'>"
        html += f"<p>{i['ad']} - {i['fiyat']} ({i['satici']}) {one_cikar}</p>"
        html += f"<form action='/one_cikar/{i['id']}' method='post'><button type='submit'>Öne Çıkar</button></form>"
        html += f"<form action='/ilan_sil/{i['id']}' method='post'><button type='submit'>Sil</button></form>"
        html += "</div>"

    html += "<br><a href='/'>← Ana Sayfa</a></div>"
    return html

# Ödeme onaylama
@app.route('/onayla_odeme/<string:odeme_id>', methods=['POST'])
def onayla_odeme(odeme_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    global bekleyen_odemeler, users
    odeme = next((o for o in bekleyen_odemeler if o['id'] == odeme_id), None)
    if odeme:
        user = next((u for u in users if u['username'] == odeme['username']), None)
        if user:
            user['ilan_hakki'] += 1
            bekleyen_odemeler = [o for o in bekleyen_odemeler if o['id'] != odeme_id]
            save_json(USERS_FILE, users)
            save_json(BEKLEYEN_ODEMELER_FILE, bekleyen_odemeler)
    return redirect('/admin')

# İlan öne çıkarma
@app.route('/one_cikar/<string:ilan_id>', methods=['POST'])
def one_cikar(ilan_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    global ilanlar
    for i in ilanlar:
        if i['id'] == ilan_id:
            i['one_cikar'] = not i.get('one_cikar', False)
    save_json(ILANLAR_FILE, ilanlar)
    return redirect('/admin')

# İlan sil
@app.route('/ilan_sil/<string:ilan_id>', methods=['POST'])
def ilan_sil(ilan_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    global ilanlar
    ilanlar = [i for i in ilanlar if i['id'] != ilan_id]
    save_json(ILANLAR_FILE, ilanlar)
    return redirect('/admin')

# Kullanıcı ilan açma
@app.route('/ilan_ac', methods=['GET', 'POST'])
def ilan_ac():
    if not session.get('user'):
        return redirect('/giris')

    user = next((u for u in users if u['username'] == session['user']), None)
    if user['ilan_hakki'] <= 0:
        odeme_id = str(uuid.uuid4())
        bekleyen_odemeler.append({"id": odeme_id, "username": user['username']})
        save_json(BEKLEYEN_ODEMELER_FILE, bekleyen_odemeler)
        return DARK_STYLE + f"<div style='text-align:center; padding:50px;'><h2>İlan Hakkın Yok</h2><p>Ödeme yap, admin onaylasın.</p><div class='uyari'>{IBAN_BILGISI}</div><a href='/'>← Ana Sayfa</a></div>"
    
    if request.method == 'POST':
        ad = request.form['ad'].strip()
        fiyat = request.form['fiyat'].strip()
        ilan_id = str(uuid.uuid4())
        ilanlar.append({
            "id": ilan_id,
            "ad": ad,
            "fiyat": fiyat,
            "satici": user['username'],
            "one_cikar": False
        })
        user['ilan_hakki'] -= 1
        save_json(ILANLAR_FILE, ilanlar)
        save_json(USERS_FILE, users)
        return redirect('/')

    html = DARK_STYLE + "<div style='text-align:center; padding:50px 20px; max-width:400px; margin:auto;'>"
    html += "<h2>İlan Aç</h2>"
    html += """
    <form method='post'>
        <input type='text' name='ad' placeholder='İlan Adı' required>
        <input type='text' name='fiyat' placeholder='Fiyat' required>
        <button type='submit'>İlan Aç</button>
    </form>
    <br><a href='/'>← Ana Sayfa</a>
    </div>
    """
    return html

# Admin çıkış
@app.route('/admin_cikis')
def admin_cikis():
    session.pop('admin_logged_in', None)
    return redirect('/')

# Kullanıcı çıkış
@app.route('/cikis')
def cikis():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))