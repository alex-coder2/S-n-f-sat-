from flask import Flask, request, redirect, session, url_for
import os
import json
import uuid

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'super_gizli_vortex_1453')

# Admin şifresi
ADMIN_SIFRE = "Vortex1453"

# IBAN bilgisi (açıklama uyarısı ile)
IBAN_UYARI = """
<b>IBAN:</b> TR350006400000163002969560<br>
<b>Alıcı:</b> Haşim Seviniş<br>
<b>Banka:</b> Garanti BBVA<br><br>
<span style="color:#ff4444; font-weight:bold;">
⚠️ Açıklama kısmına MUTLAKA KULLANICI ADINI yaz!<br>
Yazmazsan ödeme onaylanmaz ve ilan açamazsın!
</span>
"""

# Mobil uyumlu karanlık tema
STYLE = """
<style>
    body { background:#000; color:#00ff00; font-family:Arial; margin:0; padding:0; min-height:100vh; }
    h1,h2 { color:#00ff41; text-align:center; }
    a { color:#00ff00; }
    input,select { background:#111; color:#00ff00; border:2px solid #00ff00; border-radius:12px; padding:14px; width:100%; margin:10px 0; box-sizing:border-box; }
    button { background:#00aa00; color:#000; padding:16px; border:none; border-radius:12px; width:100%; font-weight:bold; margin:10px 0; }
    button:hover { background:#00ff00; }
    .card { background:#0a0a0a; border:2px solid #00ff00; border-radius:20px; padding:20px; margin:20px 0; box-shadow:0 0 15px #00ff0033; }
    .warn { background:#330000; border:2px solid #ff4444; border-radius:15px; padding:20px; margin:20px 0; }
    footer { text-align:center; padding:20px; color:#006600; }
    @media (max-width:600px) { body { padding:10px; } .card { margin:15px 0; } }
</style>
<meta name="viewport" content="width=device-width, initial-scale=1">
"""

# Dosyalar
USERS_FILE = "users.json"
ILANLAR_FILE = "ilanlar.json"
ODEMELER_FILE = "odemeler.json"

def load(file, default=[]):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

users = load(USERS_FILE, [])
ilanlar = load(ILANLAR_FILE, [])
bekleyen_odemeler = load(ODEMELER_FILE, [])

@app.route('/')
def ana_sayfa():
    # Öne çıkarılanlar önce
    sirali_ilanlar = sorted(ilanlar, key=lambda x: x.get('one_cikar', False), reverse=True)
    
    html = STYLE + "<div style='max-width:600px; margin:auto; padding:10px;'>"
    html += "<h1>📚 Sınıf Pazarı</h1>"
    html += "<p style='text-align:center;'>Güvenli ikinci el alışveriş</p>"
    
    if 'user' in session:
        html += f"<p>Hoş geldin <b>{session['user']}</b> | <a href='/ilan_ac'>İlan Aç</a> | <a href='/cikis'>Çıkış</a></p>"
    else:
        html += "<p><a href='/giris'>Giriş Yap</a> | <a href='/kayit'>Kayıt Ol</a></p>"
    
    if not sirali_ilanlar:
        html += "<p style='text-align:center; padding:50px;'>Henüz ilan yok.</p>"
    else:
        for i in sirali_ilanlar:
            one = " ⭐ Öne Çıkarılmış" if i.get('one_cikar') else ""
            html += f"<div class='card'><h3>{i['ad']}{one}</h3>"
            html += f"<p><b>Fiyat:</b> {i['fiyat']}</p>"
            html += f"<p><b>Satıcı:</b> {i['satici']}</p></div>"
    
    html += "<footer>Sınıf Pazarı © 2026</footer></div>"
    return html

@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        telefon = request.form['telefon'].strip()
        if any(u['username'] == username for u in users):
            return STYLE + "<div style='text-align:center; padding:100px;'><h2>Kullanıcı adı alınmış!</h2><a href='/kayit'>Geri</a></div>"
        users.append({"username": username, "password": password, "telefon": telefon, "ilan_hakki": 0})
        save(USERS_FILE, users)
        return redirect('/giris')
    return STYLE + "<div style='max-width:400px; margin:auto; padding:50px;'><h2>Kayıt Ol</h2><form method='post'>"
    return STYLE + "<form method='post'>"
    + "<input name='username' placeholder='Kullanıcı Adı' required>"
    + "<input type='password' name='password' placeholder='Şifre' required>"
    + "<input name='telefon' placeholder='Telefon (05xxxxxxxxxx)' required>"
    + "<button>Kayıt Ol</button></form><br><a href='/giris'>Giriş Yap</a></div>"

@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            session['user'] = username
            return redirect('/')
        return STYLE + "<div style='text-align:center; padding:100px;'><h2>Yanlış bilgi!</h2><a href='/giris'>Geri</a></div>"
    return STYLE + "<div style='max-width:400px; margin:auto; padding:50px;'><h2>Giriş Yap</h2><form method='post'>"
    + "<input name='username' placeholder='Kullanıcı Adı' required>"
    + "<input type='password' name='password' placeholder='Şifre' required>"
    + "<button>Giriş Yap</button></form><br><a href='/kayit'>Kayıt Ol</a></div>"

@app.route('/ilan_ac', methods=['GET', 'POST'])
def ilan_ac():
    if 'user' not in session:
        return redirect('/giris')
    user = next(u for u in users if u['username'] == session['user'])
    if user['ilan_hakki'] <= 0:
        # Yeni ödeme kaydı oluştur
        odeme_id = str(uuid.uuid4())
        bekleyen_odemeler.append({"id": odeme_id, "username": user['username']})
        save(ODEMELER_FILE, bekleyen_odemeler)
        return STYLE + f"<div style='max-width:500px; margin:auto; padding:50px;'><h2>İlan Hakkın Yok</h2><p>İlan açmak için ödeme yapman lazım.</p><div class='warn'>{IBAN_UYARI}</div><p>Ödeme yapınca admin onaylayacak ve ilan açabileceksin.</p><a href='/'>← Ana Sayfa</a></div>"
    
    if request.method == 'POST':
        ilan_id = str(uuid.uuid4())
        ilanlar.append({
            "id": ilan_id,
            "ad": request.form['ad'],
            "fiyat": request.form['fiyat'],
            "satici": user['username'],
            "one_cikar": False
        })
        user['ilan_hakki'] -= 1
        save(ILANLAR_FILE, ilanlar)
        save(USERS_FILE, users)
        return redirect('/')
    
    return STYLE + "<div style='max-width:400px; margin:auto; padding:50px;'><h2>Yeni İlan Aç</h2><form method='post'>"
    + "<input name='ad' placeholder='İlan Başlığı' required>"
    + "<input name='fiyat' placeholder='Fiyat' required>"
    + "<button>İlan Aç</button></form><br><a href='/'>← Ana Sayfa</a></div>"

@app.route('/cikis')
def cikis():
    session.pop('user', None)
    return redirect('/')

# Admin bölümü
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['sifre'] == ADMIN_SIFRE:
            session['admin'] = True
            return redirect('/admin')
    return STYLE + "<div style='max-width:400px; margin:auto; padding:100px;'><h2>Admin Giriş</h2><form method='post'>"
    + "<input type='password' name='sifre' placeholder='Şifre' required>"
    + "<button>Giriş Yap</button></form></div>"

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/admin_login')
    
    html = STYLE + "<div style='max-width:800px; margin:auto; padding:20px;'><h1>Admin Paneli</h1>"
    html += "<p><a href='/admin_cikis'>Çıkış</a></p>"
    
    # Bekleyen ödemeler
    html += "<h2>Bekleyen Ödemeler</h2>"
    if bekleyen_odemeler:
        for o in bekleyen_odemeler:
            html += f"<div class='card'><p>Kullanıcı: {o['username']}</p>"
            html += f"<form action='/odeme_onayla/{o['id']}' method='post'><button>Onayla (İlan Hakkı Ver)</button></form></div>"
    else:
        html += "<p>Yok</p>"
    
    # İlanlar
    html += "<h2>İlanlar</h2>"
    for i in ilanlar:
        star = " ⭐" if i.get('one_cikar') else ""
        html += f"<div class='card'><p>{i['ad']} - {i['fiyat']} ({i['satici']}){star}</p>"
        html += f"<form action='/one_cikar/{i['id']}' method='post'><button>Öne Çıkar</button></form> "
        html += f"<form action='/ilan_sil/{i['id']}' method='post'><button>Sil</button></form></div>"
    
    html += "</div>"
    return html

@app.route('/odeme_onayla/<id>', methods=['POST'])
def odeme_onayla(id):
    if not session.get('admin'):
        return redirect('/admin_login')
    global bekleyen_odemeler, users
    odeme = next((o for o in bekleyen_odemeler if o['id'] == id), None)
    if odeme:
        user = next((u for u in users if u['username'] == odeme['username']), None)
        if user:
            user['ilan_hakki'] += 1
            save(USERS_FILE, users)
        bekleyen_odemeler = [o for o in bekleyen_odemeler if o['id'] != id]
        save(ODEMELER_FILE, bekleyen_odemeler)
    return redirect('/admin')

@app.route('/one_cikar/<id>', methods=['POST'])
def one_cikar(id):
    if not session.get('admin'):
        return redirect('/admin_login')
    for i in ilanlar:
        if i['id'] == id:
            i['one_cikar'] = not i.get('one_cikar', False)
    save(ILANLAR_FILE, ilanlar)
    return redirect('/admin')

@app.route('/ilan_sil/<id>', methods=['POST'])
def ilan_sil(id):
    if not session.get('admin'):
        return redirect('/admin_login')
    global ilanlar
    ilanlar = [i for i in ilanlar if i['id'] != id]
    save(ILANLAR_FILE, ilanlar)
    return redirect('/admin')

@app.route('/admin_cikis')
def admin_cikis():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))