from flask import Flask, request, redirect, session
import os
import json
import uuid

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'vortex_gizli_1453_2026')

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
    h1 { color:#00ff41; text-align:center; margin:30px 0; font-size:28px; }
    .header { position:fixed; top:0; left:0; right:0; background:#000; padding:10px; text-align:right; border-bottom:2px solid #00ff00; z-index:100; }
    .header a { background:#00aa00; color:#000; padding:8px 16px; border-radius:20px; font-size:14px; margin-left:10px; font-weight:bold; }
    .content { padding-top:70px; max-width:600px; margin:auto; padding-left:10px; padding-right:10px; }
    .card { background:#0a0a0a; border:2px solid #00ff00; border-radius:20px; padding:25px; margin:20px 0; box-shadow:0 0 15px rgba(0,255,0,0.3); }
    input { background:#111; color:#00ff00; border:2px solid #00ff00; border-radius:12px; padding:14px; width:100%; margin:10px 0; box-sizing:border-box; font-size:16px; }
    button { background:#00aa00; color:#000; padding:14px; border:none; border-radius:12px; width:100%; font-weight:bold; font-size:18px; margin:10px 0; }
    button:hover { background:#00ff00; }
    .warn { background:#330000; border:2px solid #ff4444; border-radius:15px; padding:20px; margin:20px 0; }
    .buy { background:#ff8800; color:#000; }
    .delete { background:#ff0000; color:#fff; }
    footer { text-align:center; padding:30px; color:#006600; font-size:14px; }
    @media (max-width:600px) { .header a { padding:6px 12px; font-size:13px; } }
</style>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
"""

USERS_FILE = "users.json"
ILANLAR_FILE = "ilanlar.json"
ODEMELER_FILE = "odemeler.json"
TAMAMLANAN_FILE = "tamamlanan.json"  # Yeni: Tamamlanan siparişler

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
tamamlanan_siparisler = load(TAMAMLANAN_FILE, [])

@app.route('/')
def ana_sayfa():
    sirali = sorted(ilanlar, key=lambda x: x.get('one_cikar', False), reverse=True)
    
    html = STYLE
    html += "<div class='header'>"
    if 'user' in session:
        current_user = next((u for u in users if u['username'] == session['user']), None)
        hak = current_user['ilan_hakki'] if current_user else 0
        html += f"<b>{session['user']}</b> (Hak: {hak}) | <a href='/ilan_ac'>İlan Aç</a> | <a href='/ilanlarim'>İlanlarım</a> | <a href='/cikis'>Çıkış</a>"
    else:
        html += "<a href='/kayit'>Kayıt Ol</a> <a href='/giris'>Giriş Yap</a>"
    html += "</div>"
    
    html += "<div class='content'>"
    html += "<h1>📚 Sınıf Pazarı</h1>"
    
    if not sirali:
        html += "<p style='text-align:center; padding:100px 0; font-size:18px;'>😢 Şu an ilan yok.</p>"
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
                html += "<button class='buy'>Satın Al</button>"
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
            return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>" + "<div class='content'><h2>Kullanıcı adı alınmış!</h2><a href='/kayit'>Geri</a></div>"
        users.append({"username": username, "password": password, "telefon": telefon, "ilan_hakki": 0})
        save(USERS_FILE, users)
        return redirect('/giris')
    return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>" + "<div class='content'><h2>Kayıt Ol</h2><form method='post'>"
    + "<input name='username' placeholder='Kullanıcı Adı' required>"
    + "<input type='password' name='password' placeholder='Şifre' required>"
    + "<input name='telefon' placeholder='Telefon' required>"
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
        return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>" + "<div class='content'><h2>Yanlış bilgi!</h2><a href='/giris'>Geri</a></div>"
    return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>" + "<div class='content'><h2>Giriş Yap</h2><form method='post'>"
    + "<input name='username' placeholder='Kullanıcı Adı' required>"
    + "<input type='password' name='password' placeholder='Şifre' required>"
    + "<button>Giriş Yap</button></form><br><a href='/kayit'>Kayıt Ol</a></div>"

@app.route('/ilan_ac', methods=['GET', 'POST'])
def ilan_ac():
    if 'user' not in session:
        return redirect('/giris')
    user = next(u for u in users if u['username'] == session['user'])
    if user['ilan_hakki'] <= 0:
        odeme_id = str(uuid.uuid4())
        bekleyen_odemeler.append({"id": odeme_id, "username": user['username']})
        save(ODEMELER_FILE, bekleyen_odemeler)
        return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>" + "<div class='content'><h2>İlan Hakkın Yok</h2>" + f"<div class='warn'>{IBAN_UYARI}</div></div>"
    
    if request.method == 'POST':
        ilan_id = str(uuid.uuid4())
        stok = int(request.form['stok'])
        ilanlar.append({
            "id": ilan_id,
            "ad": request.form['ad'].strip(),
            "fiyat": request.form['fiyat'].strip(),
            "satici": user['username'],
            "one_cikar": False,
            "stok": stok,
            "satin_alanlar": []
        })
        user['ilan_hakki'] -= 1
        save(ILANLAR_FILE, ilanlar)
        save(USERS_FILE, users)
        return redirect('/ilanlarim')
    
    return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>" + "<div class='content'><h2>Yeni İlan Aç</h2><form method='post'>"
    + "<input name='ad' placeholder='Başlık' required>"
    + "<input name='fiyat' placeholder='Fiyat' required>"
    + "<input type='number' name='stok' placeholder='Stok' value='1' min='1' required>"
    + "<button>İlan Aç</button></form></div>"

@app.route('/ilanlarim')
def ilanlarim():
    if 'user' not in session:
        return redirect('/giris')
    aktif_ilanlar = [i for i in ilanlar if i['satici'] == session['user']]
    tamamlanan = [s for s in tamamlanan_siparisler if s['satici'] == session['user']]
    
    html = STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>" + "<div class='content'><h2>İlanlarım</h2>"
    
    html += "<h3>Aktif İlanlar</h3>"
    if aktif_ilanlar:
        for i in aktif_ilanlar:
            html += f"<div class='card'>"
            html += f"<h3>{i['ad']}</h3>"
            html += f"<p><b>Fiyat:</b> {i['fiyat']}</p>"
            html += f"<p><b>Stok:</b> {i['stok']}</p>"
            html += f"<form action='/ilan_sil/{i['id']}' method='post'>"
            html += "<button class='delete'>İlanı Sil (Hak geri)</button>"
            html += "</form>"
            html += "</div>"
    else:
        html += "<p>Aktif ilan yok.</p>"
    
    html += "<h3>Tamamlanan Siparişler</h3>"
    if tamamlanan:
        for s in tamamlanan:
            alici_user = next((u for u in users if u['username'] == s['alici']), None)
            tel = alici_user['telefon'] if alici_user else "Bilinmiyor"
            html += f"<div class='card'>"
            html += f"<p><b>Ürün:</b> {s['ad']}</p>"
            html += f"<p><b>Alıcı:</b> {s['alici']}</p>"
            html += f"<p><b>Telefon:</b> {tel}</p>"
            html += f"<p><b>Tarih:</b> {s['tarih']}</p>"
            html += "</div>"
    else:
        html += "<p>Tamamlanan sipariş yok.</p>"
    
    html += "<a href='/ilan_ac'>Yeni İlan Aç</a></div>"
    return html

@app.route('/satin_al/<id>', methods=['POST'])
def satin_al(id):
    if 'user' not in session:
        return redirect('/giris')
    ilan = next((i for i in ilanlar if i['id'] == id), None)
    if not ilan or ilan['stok'] <= 0:
        return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>" + "<div class='content'><h2 style='color:#ff4444;'>Stok yok!</h2><a href='/'>Ana Sayfa</a></div>"
    
    alici = session['user']
    ilan['stok'] -= 1
    
    # Tamamlanan siparişe ekle
    tamamlanan_siparisler.append({
        "ilan_id": ilan['id'],
        "ad": ilan['ad'],
        "fiyat": ilan['fiyat'],
        "satici": ilan['satici'],
        "alici": alici,
        "tarih": datetime.now().strftime("%d.%m.%Y %H:%M")
    })
    save(TAMAMLANAN_FILE, tamamlanan_siparisler)
    
    if ilan['stok'] <= 0:
        ilanlar.remove(ilan)
        satıcı = next((u for u in users if u['username'] == ilan['satici']), None)
        if satıcı:
            satıcı['ilan_hakki'] += 1
            save(USERS_FILE, users)
    
    save(ILANLAR_FILE, ilanlar)
    
    satici_tel = next((u for u in users if u['username'] == ilan['satici']), None)['telefon']
    html = STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>" + "<div class='content'><h2>Satın Alındı!</h2>"
    html += f"<p>{ilan['ad']} satın alındı.</p>"
    html += f"<p><b>Satıcı Tel:</b> {satici_tel}</p>"
    html += "<a href='/'>Ana Sayfa</a></div>"
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

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['sifre'] == ADMIN_SIFRE:
            session['admin'] = True
            return redirect('/admin')
    return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>" + "<div class='content'><h2>Admin Giriş</h2><form method='post'>"
    + "<input type='password' name='sifre' placeholder='Şifre' required>"
    + "<button>Giriş Yap</button></form></div>"

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/admin_login')
    
    html = STYLE + "<div class='header'><a href='/admin_cikis'>Çıkış</a></div>" + "<div class='content'><h1>Admin Paneli</h1>"
    
    html += "<h2>Bekleyen Ödemeler</h2>"
    if bekleyen_odemeler:
        for o in bekleyen_odemeler:
            html += f"<div class='card'><p>Kullanıcı: {o['username']}</p>"
            html += f"<form action='/odeme_onayla/{o['id']}' method='post'><button>Onayla</button></form></div>"
    else:
        html += "<p>Yok</p>"
    
    html += "<h2>Kullanıcılar</h2>"
    for u in users:
        html += f"<div class='card'><p>{u['username']} - Tel: {u['telefon']} - Hak: {u['ilan_hakki']}</p>"
        html += f"<form action='/kullanici_sil/{u['username']}' method='post'><button class='delete'>Kullanıcıyı Sil</button></form></div>"
    
    html += "<h2>İlanlar</h2>"
    for i in ilanlar:
        star = " ⭐" if i.get('one_cikar') else ""
        html += f"<div class='card'><p>{i['ad']} - {i['fiyat']} ({i['satici']}){star} - Stok: {i['stok']}</p>"
        html += f"<form action='/one_cikar/{i['id']}' method='post'><button>Öne Çıkar</button></form>"
        html += f"<form action='/ilan_sil_admin/{i['id']}' method='post'><button class='delete'>Sil</button></form></div>"
    
    html += "<a href='/'>Ana Sayfa</a></div>"
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
    ilan = next((i for i in ilanlar if i['id'] == id), None)
    if ilan:
        ilanlar.remove(ilan)
        save(ILANLAR_FILE, ilanlar)
    return redirect('/admin')

@app.route('/kullanici_sil/<username>', methods=['POST'])
def kullanici_sil(username):
    if not session.get('admin'):
        return redirect('/admin_login')
    global users
    users = [u for u in users if u['username'] != username]
    save(USERS_FILE, users)
    return redirect('/admin')

@app.route('/admin_cikis')
def admin_cikis():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))