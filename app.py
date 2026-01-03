from flask import Flask, request, redirect, session
import os
import json
import uuid

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'vortex_gizli_anahtar_1453_2026')

# Admin şifresi
ADMIN_SIFRE = "Vortex1453"

# İlan açtırma parası (sadece bilgi, kodda kullanılmıyor)
ILAN_PARASI = "25 TL"

# IBAN bilgisi
IBAN_UYARI = """
<b>IBAN:</b> TR350006400000163002969560<br>
<b>Alıcı:</b> Haşim Seviniş<br>
<b>Banka:</b> Garanti BBVA<br><br>
<span style="color:#ff4444; font-weight:bold;">
⚠️ Açıklama kısmına KULLANICI ADINI yaz!<br>
Yazmazsan ödeme onaylanmaz!
</span>
<p>İlan açtırma parası: """ + ILAN_PARASI + """</p>
"""

# Karanlık tema CSS - butonlar düzeltilmiş, üst üste gelmez
STYLE = """
<style>
    body { background:#000; color:#00ff00; font-family:Arial; margin:0; padding:0; min-height:100vh; }
    h1 { color:#00ff41; text-align:center; margin:30px 0; font-size:28px; }
    .header { position:fixed; top:0; left:0; right:0; background:#000; padding:10px; text-align:right; border-bottom:2px solid #00ff00; z-index:100; }
    .header a { background:#00aa00; color:#000; padding:8px 16px; border-radius:20px; font-size:14px; margin-left:10px; font-weight:bold; display:inline-block; width:auto; }
    .header span { color:#00ff00; margin-right:10px; font-weight:bold; }
    .content { padding-top:70px; max-width:600px; margin:auto; padding-left:10px; padding-right:10px; }
    .card { background:#0a0a0a; border:2px solid #00ff00; border-radius:20px; padding:25px; margin:20px 0; box-shadow:0 0 15px rgba(0,255,0,0.3); }
    input { background:#111; color:#00ff00; border:2px solid #00ff00; border-radius:12px; padding:14px; width:100%; margin:10px 0; box-sizing:border-box; font-size:16px; }
    button { background:#00aa00; color:#000; padding:14px; border:none; border-radius:12px; width:100%; font-weight:bold; font-size:18px; margin:10px 0; cursor:pointer; }
    button:hover { background:#00ff00; }
    .warn { background:#330000; border:2px solid #ff4444; border-radius:15px; padding:20px; margin:20px 0; }
    .buy-button { background:#ff8800; color:#000; }
    footer { text-align:center; padding:30px; color:#006600; font-size:14px; }
    @media (max-width:600px) { .header a { padding:6px 12px; font-size:13px; margin-left:5px; } }
</style>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
"""

# Veri dosyaları
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
    sirali = sorted(ilanlar, key=lambda x: x.get('one_cikar', False), reverse=True)
    
    html = STYLE
    html += "<div class='header'>"
    if 'user' in session:
        current_user = next((u for u in users if u['username'] == session['user']), None)
        hak = current_user['ilan_hakki'] if current_user else 0
        html += f"<span>{session['user']} (Hak: {hak})</span>"
        html += "<a href='/ilanlarim'>İlanlarım</a> <a href='/ilan_ac'>İlan Aç</a> <a href='/cikis'>Çıkış</a>"
    else:
        html += "<a href='/kayit'>Kayıt Ol</a> <a href='/giris'>Giriş Yap</a>"
    html += "</div>"
    
    html += "<div class='content'>"
    html += "<h1>📚 Sınıf Pazarı</h1>"
    
    if not sirali:
        html += "<p style='text-align:center; padding:100px 0; font-size:18px;'>😢 Şu an satılık ilan yok.<br>Yeni ilanlar yakında gelir!</p>"
    else:
        for i in sirali:
            one = " ⭐ Öne Çıkarılmış" if i.get('one_cikar') else ""
            html += f"<div class='card'>"
            html += f"<h3>{i['ad']}{one}</h3>"
            html += f"<p><b>Fiyat:</b> {i['fiyat']}</p>"
            html += f"<p><b>Satıcı:</b> {i['satici']}</p>"
            html += f"<p><b>Stok:</b> {i['stok']}</p>"
            if 'user' in session and session['user'] != i['satici']:
                html += f"<form action='/satin_al/{i['id']}' method='post'>"
                html += "<button class='buy-button' type='submit'>Satın Al</button>"
                html += "</form>"
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
            return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
            + "<div class='content'><h2>Kullanıcı adı alınmış!</h2><a href='/kayit'>Geri</a></div>"
        users.append({
            "username": username,
            "password": password,
            "telefon": telefon,
            "ilan_hakki": 0,
            "banned": False
        })
        save(USERS_FILE, users)
        return redirect('/giris')
    return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
    + "<div class='content'><h2>Kayıt Ol</h2>"
    + "<form method='post'>"
    + "<input name='username' placeholder='Kullanıcı Adı' required>"
    + "<input type='password' name='password' placeholder='Şifre' required>"
    + "<input name='telefon' placeholder='Telefon (05xxxxxxxxxx)' required>"
    + "<button>Kayıt Ol</button></form>"
    + "<br><a href='/giris'>Giriş Yap</a></div>"

@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            if user['banned']:
                return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
                + "<div class='content'><h2 style='color:#ff4444;'>Hesabın banlanmış!</h2><a href='/'>Ana Sayfa</a></div>"
            session['user'] = username
            return redirect('/')
        return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
        + "<div class='content'><h2>Yanlış bilgi!</h2><a href='/giris'>Geri</a></div>"
    return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
    + "<div class='content'><h2>Giriş Yap</h2>"
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
        return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
        + "<div class='content'><h2>İlan Hakkın Yok</h2>"
        + f"<div class='warn'>{IBAN_UYARI}</div>"
        + "<p>Ödeme yapınca admin onaylayacak.</p></div>"
    
    if request.method == 'POST':
        ilan_id = str(uuid.uuid4())
        ilanlar.append({
            "id": ilan_id,
            "ad": request.form['ad'].strip(),
            "fiyat": request.form['fiyat'].strip(),
            "satici": user['username'],
            "one_cikar": False,
            "stok": int(request.form['stok']),
            "satin_alanlar": []
        })
        user['ilan_hakki'] -= 1
        save(ILANLAR_FILE, ilanlar)
        save(USERS_FILE, users)
        return redirect('/ilanlarim')
    
    return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
    + "<div class='content'><h2>Yeni İlan Aç</h2>"
    + "<form method='post'>"
    + "<input name='ad' placeholder='İlan Başlığı' required>"
    + "<input name='fiyat' placeholder='Fiyat (örn: 250 TL)' required>"
    + "<input type='number' name='stok' placeholder='Stok Miktarı' min='1' value='1' required>"
    + "<button>İlan Aç</button></form></div>"

@app.route('/ilanlarim', methods=['GET', 'POST'])
def ilanlarim():
    if 'user' not in session:
        return redirect('/giris')
    user_ilanlar = [i for i in ilanlar if i['satici'] == session['user']]
    
    html = STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
    html += "<div class='content'><h2>İlanlarım</h2>"
    
    if not user_ilanlar:
        html += "<p style='text-align:center; padding:100px 0; font-size:18px;'>Henüz ilanın yok. <a href='/ilan_ac'>Yeni İlan Aç</a></p>"
    else:
        for i in user_ilanlar:
            one = " ⭐ Öne Çıkarılmış" if i.get('one_cikar') else ""
            html += f"<div class='card'>"
            html += f"<h3>{i['ad']}{one}</h3>"
            html += f"<p><b>Fiyat:</b> {i['fiyat']}</p>"
            html += f"<p><b>Stok:</b> {i['stok']}</p>"
            html += "<p><b>Satın Alanlar:</b></p>"
            if i['satin_alanlar']:
                for alici in i['satin_alanlar']:
                    alici_info = next((u for u in users if u['username'] == alici['alan']), None)
                    tel = alici_info['telefon'] if alici_info else "Bilinmiyor"
                    html += f"<p>{alici['alan']} - Telefon: {tel} - İletişime geçin!</p>"
            else:
                html += "<p>Henüz satın alan yok.</p>"
            html += f"<form action='/ilan_sil/{i['id']}' method='post'>"
            html += "<button style='background:#ff0000;'>İlanı Sil (1 hak geri ver)</button>"
            html += "</form>"
            html += "</div>"
    
    html += "<a href='/ilan_ac'>Yeni İlan Aç</a></div>"
    return html

@app.route('/satin_al/<id>', methods=['POST'])
def satin_al(id):
    if 'user' not in session:
        return redirect('/giris')
    ilan = next((i for i in ilanlar if i['id'] == id), None)
    if not ilan or ilan['stok'] <= 0:
        return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
        + "<div class='content'><h2 style='color:#ff4444;'>Stok yok veya ilan bulunamadı!</h2><a href='/'>Ana Sayfa</a></div>"
    
    alici = session['user']
    ilan['satin_alanlar'].append({"alan": alici})
    ilan['stok'] -= 1
    if ilan['stok'] <= 0:
        ilanlar.remove(ilan)
        satıcı_user = next((u for u in users if u['username'] == ilan['satici']), None)
        if satıcı_user:
            satıcı_user['ilan_hakki'] += 1
            save(USERS_FILE, users)
    save(ILANLAR_FILE, ilanlar)
    
    alici_info = next((u for u in users if u['username'] == alici), None)
    satıcı_info = next((u for u in users if u['username'] == ilan['satici']), None)
    alici_tel = alici_info['telefon'] if alici_info else "Bilinmiyor"
    satici_tel = satıcı_info['telefon'] if satıcı_info else "Bilinmiyor"
    
    html = STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
    html += "<div class='content'><h2 style='color:#00ff41;'>Satın Alma Başarılı!</h2>"
    html += f"<p>{ilan['ad']} satın alındı.</p>"
    html += f"<p><b>Satıcı Telefon:</b> {satici_tel} - İletişime geçin!</p>"
    html += "</div>"
    return html

@app.route('/ilan_sil/<id>', methods=['POST'])
def ilan_sil(id):
    if 'user' not in session:
        return redirect('/giris')
    ilan = next((i for i in ilanlar if i['id'] == id and i['satici'] == session['user']), None)
    if ilan:
        ilanlar.remove(ilan)
        user = next(u for u in users if u['username'] == session['user'])
        user['ilan_hakki'] += 1
        save(ILANLAR_FILE, ilanlar)
        save(USERS_FILE, users)
    return redirect('/ilanlarim')

@app.route('/cikis')
def cikis():
    session.pop('user', None)
    return redirect('/')

# Admin paneli
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['sifre'] == ADMIN_SIFRE:
            session['admin'] = True
            return redirect('/admin')
    html = STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
    html += "<div class='content'><h2>🔐 Admin Girişi</h2>"
    html += "<form method='post'>"
    html += "<input type='password' name='sifre' placeholder='Admin Şifresi' required>"
    html += "<button>Giriş Yap</button>"
    html += "</form>"
    html += "</div>"
    return html

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/admin_login')
    
    html = STYLE + "<div class='header'><a href='/admin_cikis'>Çıkış Yap</a></div>"
    html += "<div class='content'><h1>🔐 Admin Paneli</h1>"
    
    # Bekleyen ödemeler
    html += "<h2>⏳ Bekleyen Ödemeler</h2>"
    if bekleyen_odemeler:
        for o in bekleyen_odemeler:
            html += f"<div class='card'>"
            html += f"<p><b>Kullanıcı:</b> {o['username']}</p>"
            html += f"<form action='/odeme_onayla/{o['id']}' method='post'>"
            html += "<button>Onayla (1 İlan Hakkı Ver)</button>"
            html += "</form>"
            html += "</div>"
    else:
        html += "<p>Bekleyen ödeme yok.</p>"
    
    # Tüm ilanlar
    html += "<h2>📦 Tüm İlanlar</h2>"
    if ilanlar:
        for i in ilanlar:
            star = " ⭐" if i.get('one_cikar') else ""
            html += f"<div class='card'>"
            html += f"<p><b>{i['ad']}</b> - {i['fiyat']} ({i['satici']}){star}</p>"
            html += f"<p>Stok: {i['stok']}</p>"
            html += f"<form action='/one_cikar/{i['id']}' method='post'>"
            html += "<button>Öne Çıkar</button>"
            html += "</form>"
            html += f"<form action='/ilan_sil_admin/{i['id']}' method='post'>"
            html += "<button style='background:#ff0000;'>Sil</button>"
            html += "</form>"
            html += "</div>"
    else:
        html += "<p>Henüz ilan yok.</p>"
    
    # Kullanıcılar (banlama)
    html += "<h2>👥 Kullanıcılar</h2>"
    if users:
        for u in users:
            banned = " (Banlı)" if u.get('banned') else ""
            html += f"<div class='card'>"
            html += f"<p><b>{u['username']}</b>{banned}</p>"
            html += f"<p>Telefon: {u['telefon']}</p>"
            html += f"<p>İlan Hakkı: {u['ilan_hakki']}</p>"
            html += f"<form action='/banla/{u['username']}' method='post'>"
            html += "<button style='background:#ff0000;'>Banla</button>"
            html += "</form>"
            html += f"<form action='/ban_kaldir/{u['username']}' method='post'>"
            html += "<button>Ban Kaldır</button>"
            html += "</form>"
            html += "</div>"
    else:
        html += "<p>Kullanıcı yok.</p>"
    
    html += "<br><a href='/'>← Ana Sayfa</a></div>"
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

@app.route('/ilan_sil_admin/<id>', methods=['POST'])
def ilan_sil_admin(id):
    if not session.get('admin'):
        return redirect('/admin_login')
    global ilanlar
    ilanlar = [i for i in ilanlar if i['id'] != id]
    save(ILANLAR_FILE, ilanlar)
    return redirect('/admin')

@app.route('/banla/<username>', methods=['POST'])
def banla(username):
    if not session.get('admin'):
        return redirect('/admin_login')
    user = next((u for u in users if u['username'] == username), None)
    if user:
        user['banned'] = True
        save(USERS_FILE, users)
    return redirect('/admin')

@app.route('/ban_kaldir/<username>', methods=['POST'])
def ban_kaldir(username):
    if not session.get('admin'):
        return redirect('/admin_login')
    user = next((u for u in users if u['username'] == username), None)
    if user:
        user['banned'] = False
        save(USERS_FILE, users)
    return redirect('/admin')

@app.route('/admin_cikis')
def admin_cikis():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))