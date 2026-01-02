from flask import Flask, request, redirect, session
import os
import json
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'vortex_super_gizli_1453_2026')

ADMIN_SIFRE = "Vortex1453"

IBAN_UYARI = """
<b>IBAN:</b> TR350006400000163002969560<br>
<b>Alıcı:</b> Haşim Seviniş<br>
<b>Banka:</b> Garanti BBVA<br><br>
<span style="color:#ff4444; font-weight:bold;">
⚠️ Açıklama kısmına KULLANICI ADINI yaz!<br>
Yazmazsan ödeme onaylanmaz!
</span>
"""

STYLE = """
<style>
    body { background:#000; color:#00ff00; font-family:Arial; margin:0; padding:0; min-height:100vh; }
    h1,h2 { color:#00ff41; text-align:center; margin:30px 0; }
    a { color:#00ff00; }
    input,textarea { background:#111; color:#00ff00; border:2px solid #00ff00; border-radius:12px; padding:14px; width:100%; margin:10px 0; box-sizing:border-box; }
    button { background:#00aa00; color:#000; padding:16px; border:none; border-radius:12px; width:100%; font-weight:bold; margin:10px 0; }
    button:hover { background:#00ff00; }
    .card { background:#0a0a0a; border:2px solid #00ff00; border-radius:20px; padding:25px; margin:20px 0; box-shadow:0 0 15px #00ff0033; }
    .warn { background:#330000; border:2px solid #ff4444; border-radius:15px; padding:20px; margin:20px 0; }
    footer { text-align:center; padding:20px; color:#006600; }
    @media (max-width:600px) { body { padding:10px; } .card { margin:15px 0; } }
</style>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
"""

USERS_FILE = "users.json"
ILANLAR_FILE = "ilanlar.json"
ODEMELER_FILE = "odemeler.json"
MESAJLAR_FILE = "mesajlar.json"

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
mesajlar = load(MESAJLAR_FILE, [])

@app.route('/')
def ana_sayfa():
    sirali = sorted(ilanlar, key=lambda x: x.get('one_cikar', False), reverse=True)
    
    html = STYLE + "<div style='max-width:600px; margin:auto; padding:10px;'>"
    html += "<h1>📚 Sınıf Pazarı</h1>"
    
    if 'user' in session:
        html += f"<p style='text-align:center;'><b>{session['user']}</b> | <a href='/ilan_ac'>İlan Aç</a> | <a href='/cikis'>Çıkış</a></p>"
    else:
        html += "<div style='text-align:center; margin:40px 0;'>"
        html += "<a href='/kayit' style='display:block; background:#00aa00; color:black; padding:18px; border-radius:12px; font-size:20px; margin:10px;'>Kayıt Ol</a>"
        html += "<a href='/giris' style='display:block; background:#006600; color:white; padding:18px; border-radius:12px; font-size:20px; margin:10px;'>Giriş Yap</a>"
        html += "</div>"
    
    if not sirali:
        html += "<p style='text-align:center; padding:80px;'>Henüz ilan yok.</p>"
    else:
        for i in sirali:
            one = " ⭐ Öne Çıkarılmış" if i.get('one_cikar') else ""
            html += f"<div class='card'><h3>{i['ad']}{one}</h3>"
            html += f"<p><b>Fiyat:</b> {i['fiyat']}</p>"
            html += f"<p><b>Satıcı:</b> {i['satici']}</p>"
            if 'user' in session and session['user'] != i['satici']:
                html += f"<a href='/mesaj_gonder/{i['id']}' style='display:block; background:#00aa00; color:black; padding:14px; border-radius:12px; margin-top:15px; text-align:center;'>💬 Mesaj Gönder</a>"
            html += "</div>"
    
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
    return STYLE + "<div style='max-width:400px; margin:auto; padding:50px;'><h2>Kayıt Ol</h2>"
    + "<form method='post'>"
    + "<input name='username' placeholder='Kullanıcı Adı' required>"
    + "<input type='password' name='password' placeholder='Şifre' required>"
    + "<input name='telefon' placeholder='Telefon' required>"
    + "<button>Kayıt Ol</button></form>"
    + "<br><a href='/giris'>Giriş Yap</a></div>"

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
    return STYLE + "<div style='max-width:400px; margin:auto; padding:50px;'><h2>Giriş Yap</h2>"
    + "<form method='post'>"
    + "<input name='username' placeholder='Kullanıcı Adı' required>"
    + "<input type='password' name='password' placeholder='Şifre' required>"
    + "<button>Giriş Yap</button></form>"
    + "<br><a href='/kayit'>Kayıt Ol</a></div>"

@app.route('/ilan_ac', methods=['GET', 'POST'])
def ilan_ac():
    if 'user' not in session:
        return redirect('/giris')
    user = next(u for u in users if u['username'] == session['user'])
    if user['ilan_hakki'] <= 0:
        odeme_id = str(uuid.uuid4())
        bekleyen_odemeler.append({"id": odeme_id, "username": user['username']})
        save(ODEMELER_FILE, bekleyen_odemeler)
        return STYLE + f"<div style='max-width:500px; margin:auto; padding:50px;'><h2>İlan Hakkın Yok</h2><div class='warn'>{IBAN_UYARI}</div><a href='/'>Ana Sayfa</a></div>"
    
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
    
    return STYLE + "<div style='max-width:400px; margin:auto; padding:50px;'><h2>İlan Aç</h2><form method='post'>"
    + "<input name='ad' placeholder='Başlık' required>"
    + "<input name='fiyat' placeholder='Fiyat' required>"
    + "<button>İlan Aç</button></form><a href='/'>Ana Sayfa</a></div>"

@app.route('/mesaj_gonder/<ilan_id>', methods=['GET', 'POST'])
def mesaj_gonder(ilan_id):
    if 'user' not in session:
        return redirect('/giris')
    ilan = next((i for i in ilanlar if i['id'] == ilan_id), None)
    if not ilan:
        return "İlan yok"
    
    if request.method == 'POST':
        mesajlar.append({
            "ilan_id": ilan_id,
            "gonderen": session['user'],
            "alici": ilan['satici'],
            "mesaj": request.form['mesaj'],
            "tarih": datetime.now().strftime("%d.%m %H:%M")
        })
        save(MESAJLAR_FILE, mesajlar)
        return STYLE + "<div style='text-align:center; padding:100px;'><h2>Mesaj gönderildi!</h2><a href='/'>Ana Sayfa</a></div>"
    
    return STYLE + f"<div style='max-width:500px; margin:auto; padding:50px;'><h2>Mesaj Gönder - {ilan['ad']}</h2>"
    + f"<p>Satıcı: {ilan['satici']}</p>"
    + "<form method='post'>"
    + "<textarea name='mesaj' rows='6' placeholder='Mesajın...' required></textarea>"
    + "<button>Gönder</button></form><a href='/'>Ana Sayfa</a></div>"

@app.route('/cikis')
def cikis():
    session.pop('user', None)
    return redirect('/')

# Admin
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['sifre'] == ADMIN_SIFRE:
            session['admin'] = True
            return redirect('/admin')
    return STYLE + "<div style='max-width:400px; margin:auto; padding:100px;'><h2>Admin Giriş</h2>"
    + "<form method='post'>"
    + "<input type='password' name='sifre' placeholder='Şifre' required>"
    + "<button>Giriş Yap</button></form></div>"

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/admin_login')
    
    html = STYLE + "<div style='max-width:900px; margin:auto; padding:20px;'><h1>Admin Paneli</h1>"
    html += "<p><a href='/admin_cikis'>Çıkış</a></p>"
    
    html += "<h2>Bekleyen Ödemeler</h2>"
    for o in bekleyen_odemeler:
        html += f"<div class='card'><p>{o['username']}</p>"
        html += f"<form action='/odeme_onayla/{o['id']}' method='post'><button>Onayla</button></form></div>"
    
    html += "<h2>Mesajlar</h2>"
    for m in mesajlar:
        html += f"<div class='card'><p><b>{m['gonderen']}</b> → <b>{m['alici']}</b> ({m['tarih']})</p><p>{m['mesaj']}</p></div>"
    
    html += "<h2>İlanlar</h2>"
    for i in ilanlar:
        star = " ⭐" if i.get('one_cikar') else ""
        html += f"<div class='card'><p>{i['ad']} - {i['fiyat']} ({i['satici']}){star}</p>"
        html += f"<form action='/one_cikar/{i['id']}' method='post'><button>Öne Çıkar</button></form>"
        html += f"<form action='/ilan_sil/{i['id']}' method='post'><button>Sil</button></form></div>"
    
    html += "</div>"
    return html

@app.route('/odeme_onayla/<id>', methods=['POST'])
def odeme_onayla(id):
    if not session.get('admin'):
        return redirect('/admin_login')
    odeme = next((o for o in bekleyen_odemeler if o['id'] == id), None)
    if odeme:
        user = next((u for u in users if u['username'] == odeme['username']), None)
        if user:
            user['ilan_hakki'] += 1
            save(USERS_FILE, users)
        bekleyen_odemeler.remove(odeme)
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