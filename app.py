from flask import Flask, request, redirect, session
import os
import json
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'vortex_gizli_anahtar_1453_2026_tam_eksiksiz_uzun_versiyon')

# Admin şifresi
ADMIN_SIFRE = "Vortex1453"

# IBAN bilgisi (detaylı)
IBAN_UYARI = """
<div class="warn">
    <p><b>IBAN:</b> TR350006400000163002969560</p>
    <p><b>Alıcı Adı:</b> Haşim Seviniş</p>
    <p><b>Banka:</b> Garanti BBVA</p>
    <p style="color:#ff4444; font-weight:bold;">
        ⚠️ Açıklama kısmına MUTLAKA KULLANICI ADINI yaz!<br>
        Yazmazsan ödeme onaylanmaz ve ilan açamazsın!
    </p>
    <p>İlan açtırma parası: 25 TL</p>
    <p>Öne çıkartacaksanız: 75 TL</p>
    <p>Ödeme yaptıktan sonra admin onaylayacak ve 1 ilan hakkı alacaksın.</p>
</div>
"""

# Karanlık tema CSS - çok detaylı ve uzun
STYLE = """
<style>
    body { 
        background:#000000; 
        color:#00ff00; 
        font-family:'Segoe UI', Arial, sans-serif; 
        margin:0; 
        padding:0; 
        min-height:100vh; 
        box-sizing:border-box; 
        line-height:1.6;
    }
    h1 { 
        color:#00ff41; 
        text-align:center; 
        margin:30px 0 50px; 
        font-size:28px; 
        text-shadow: 0 0 10px rgba(0,255,0,0.5);
    }
    h2 { 
        color:#00ff41; 
        text-align:center; 
        margin:20px 0; 
        font-size:24px; 
    }
    h3 { 
        color:#00ff41; 
        margin:15px 0; 
        font-size:20px; 
    }
    p { 
        line-height:1.6; 
        font-size:16px; 
        margin:10px 0; 
    }
    a { 
        color:#00ff00; 
        text-decoration:none; 
        font-weight:bold; 
    }
    input, select { 
        background:#111111; 
        color:#00ff00; 
        border:2px solid #00ff00; 
        border-radius:12px; 
        padding:14px; 
        width:100%; 
        margin:10px 0; 
        box-sizing:border-box; 
        font-size:16px; 
    }
    button { 
        background:#00aa00; 
        color:#000000; 
        padding:16px; 
        border:none; 
        border-radius:12px; 
        width:100%; 
        font-weight:bold; 
        font-size:18px; 
        margin:10px 0; 
        cursor:pointer; 
        transition: background 0.3s, box-shadow 0.3s;
    }
    button:hover { 
        background:#00ff00; 
        box-shadow: 0 0 15px rgba(0,255,0,0.6);
    }
    .card { 
        background:#0a0a0a; 
        border:2px solid #00ff00; 
        border-radius:20px; 
        padding:25px; 
        margin:20px 0; 
        box-shadow:0 0 20px rgba(0,255,0,0.3); 
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .card:hover { 
        transform: translateY(-5px); 
        box-shadow: 0 0 30px rgba(0,255,0,0.5);
    }
    .warn { 
        background:#330000; 
        border:2px solid #ff4444; 
        border-radius:15px; 
        padding:20px; 
        margin:20px 0; 
        text-align:center;
    }
    .buy-button { background:#ff8800; color:#000000; }
    .delete-button { background:#ff0000; color:#ffffff; }
    .highlight-button { background:#0066ff; color:#ffffff; }
    .header { 
        position:fixed; 
        top:0; 
        left:0; 
        right:0; 
        background:#000000; 
        padding:10px; 
        text-align:right; 
        border-bottom:2px solid #00ff00; 
        z-index:1000; 
    }
    .header a, .header span { 
        background:#00aa00; 
        color:#000000; 
        padding:8px 16px; 
        border-radius:20px; 
        font-size:14px; 
        margin-left:10px; 
        font-weight:bold; 
        display:inline-block; 
        transition: background 0.3s;
    }
    .header a:hover { background:#00ff00; }
    .content { 
        padding-top:70px; 
        max-width:600px; 
        margin:auto; 
        padding-left:10px; 
        padding-right:10px; 
    }
    footer { 
        text-align:center; 
        padding:30px; 
        color:#006600; 
        font-size:14px; 
        margin-top:50px;
    }
    @media (max-width:600px) { 
        .header a, .header span { padding:6px 12px; font-size:13px; margin-left:5px; }
        h1 { font-size:24px; }
        .card { padding:20px; }
    }
</style>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
"""

# Veri dosyaları
USERS_FILE = "users.json"
ILANLAR_FILE = "ilanlar.json"
ODEMELER_FILE = "odemeler.json"
TAMAMLANAN_FILE = "tamamlanan.json"

# Veri yükle/kaydet fonksiyonları (hata yönetimiyle)
def load(file, default=[]):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"{file} yüklenirken hata: {e}")
            return default
    return default

def save(file, data):
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"{file} kaydedilirken hata: {e}")

# Verileri yükle
users = load(USERS_FILE, [])
ilanlar = load(ILANLAR_FILE, [])
bekleyen_odemeler = load(ODEMELER_FILE, [])
tamamlanan_siparisler = load(TAMAMLANAN_FILE, [])

# Ana sayfa
@app.route('/')
def ana_sayfa():
    sirali = sorted(ilanlar, key=lambda x: x.get('one_cikar', False), reverse=True)
    
    html = STYLE
    html += "<div class='header'>"
    if 'user' in session:
        current_user = next((u for u in users if u['username'] == session['user']), None)
        hak = current_user['ilan_hakki'] if current_user else 0
        html += f"<span>{session['user']} (İlan Hakkı: {hak})</span>"
        html += "<a href='/ilan_ac'>İlan Aç</a>"
        html += "<a href='/ilanlarim'>İlanlarım</a>"
        html += "<a href='/cikis'>Çıkış</a>"
    else:
        html += "<a href='/kayit'>Kayıt Ol</a>"
        html += "<a href='/giris'>Giriş Yap</a>"
    html += "</div>"
    
    html += "<div class='content'>"
    html += "<h1>📚 Sınıf Pazarı</h1>"
    html += "<p style='text-align:center; font-size:18px; margin-bottom:40px;'>Güvenli ikinci el alışveriş platformu</p>"
    
    if not sirali:
        html += "<p style='text-align:center; padding:100px 0; font-size:18px;'>😢 Şu an satılık ilan bulunmamaktadır.<br>Yeni ilanlar yakında eklenecek!</p>"
    else:
        for i in sirali:
            one = " ⭐ Öne Çıkarılmış" if i.get('one_cikar') else ""
            html += f"<div class='card'>"
            html += f"<h3>{i['ad']}{one}</h3>"
            html += f"<p><b>Fiyat:</b> {i['fiyat']}</p>"
            html += f"<p><b>Satıcı:</b> {i['satici']}</p>"
            html += f"<p><b>Kalan Stok:</b> {i['stok']}</p>"
            if 'user' in session and session['user'] != i['satici']:
                html += f"<form action='/satin_al/{i['id']}' method='post'>"
                html += "<button class='buy-button'>Satın Al</button>"
                html += "</form>"
            html += "</div>"
    
    html += "<footer>Sınıf Pazarı © 2026 - Tüm hakları saklıdır.</footer></div>"
    return html

# Kayıt ol sayfası
@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        telefon = request.form['telefon'].strip()
        
        if not username or not password or not telefon:
            return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>" + "<div class='content'><h2>Tüm alanlar zorunlu!</h2><a href='/kayit'>Geri</a></div>"
        
        if any(u['username'] == username for u in users):
            return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>" + "<div class='content'><h2>Kullanıcı adı zaten alınmış!</h2><a href='/kayit'>Geri</a></div>"
        
        users.append({
            "username": username,
            "password": password,
            "telefon": telefon,
            "ilan_hakki": 0
        })
        save(USERS_FILE, users)
        return redirect('/giris')
    
    html = STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
    html += "<div class='content'>"
    html += "<h2>Kayıt Ol</h2>"
    html += "<p>Lütfen bilgilerini girerek kayıt ol.</p>"
    html += "<form method='post'>"
    html += "<input name='username' placeholder='Kullanıcı Adı' required>"
    html += "<input type='password' name='password' placeholder='Şifre' required>"
    html += "<input name='telefon' placeholder='Telefon (05xxxxxxxxxx)' required>"
    html += "<button>Kayıt Ol</button>"
    html += "</form>"
    html += "<br><p>Zaten hesabın var mı? <a href='/giris'>Giriş Yap</a></p>"
    html += "</div>"
    return html

# Giriş yap sayfası
@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            session['user'] = username
            return redirect('/')
        return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>" + "<div class='content'><h2>Yanlış kullanıcı adı veya şifre!</h2><a href='/giris'>Geri</a></div>"
    
    html = STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
    html += "<div class='content'>"
    html += "<h2>Giriş Yap</h2>"
    html += "<p>Hesabına giriş yap.</p>"
    html += "<form method='post'>"
    html += "<input name='username' placeholder='Kullanıcı Adı' required>"
    html += "<input type='password' name='password' placeholder='Şifre' required>"
    html += "<button>Giriş Yap</button>"
    html += "</form>"
    html += "<br><p>Hesabın yok mu? <a href='/kayit'>Kayıt Ol</a></p>"
    html += "</div>"
    return html

# İlan aç sayfası
@app.route('/ilan_ac', methods=['GET', 'POST'])
def ilan_ac():
    if 'user' not in session:
        return redirect('/giris')
    
    user = next(u for u in users if u['username'] == session['user'])
    
    if user['ilan_hakki'] <= 0:
        odeme_id = str(uuid.uuid4())
        bekleyen_odemeler.append({"id": odeme_id, "username": user['username']})
        save(ODEMELER_FILE, bekleyen_odemeler)
        html = STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
        html += "<div class='content'>"
        html += "<h2>İlan Hakkın Yok</h2>"
        html += IBAN_UYARI
        html += "<p>Ödeme yaptıktan sonra admin onaylayacak ve ilan açabileceksin.</p>"
        html += "<a href='/'>Ana Sayfa</a>"
        html += "</div>"
        return html
    
    if request.method == 'POST':
        ilan_id = str(uuid.uuid4())
        stok = int(request.form['stok'])
        yeni_ilan = {
            "id": ilan_id,
            "ad": request.form['ad'].strip(),
            "fiyat": request.form['fiyat'].strip(),
            "satici": user['username'],
            "one_cikar": False,
            "stok": stok,
            "satin_alanlar": []
        }
        ilanlar.append(yeni_ilan)
        user['ilan_hakki'] -= 1
        save(ILANLAR_FILE, ilanlar)
        save(USERS_FILE, users)
        return redirect('/ilanlarim')
    
    html = STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
    html += "<div class='content'>"
    html += "<h2>Yeni İlan Aç</h2>"
    html += "<p>İlan bilgilerini gir.</p>"
    html += "<form method='post'>"
    html += "<input name='ad' placeholder='İlan Başlığı (örn: 1 aylık Netflix)' required>"
    html += "<input name='fiyat' placeholder='Fiyat (örn: 250 TL)' required>"
    html += "<input type='number' name='stok' placeholder='Stok Miktarı' value='1' min='1' required>"
    html += "<button>İlanı Yayınla</button>"
    html += "</form>"
    html += "</div>"
    return html

# İlanlarım sayfası (aktif + tamamlanan)
@app.route('/ilanlarim')
def ilanlarim():
    if 'user' not in session:
        return redirect('/giris')
    
    aktif_ilanlar = [i for i in ilanlar if i['satici'] == session['user']]
    tamamlanan = [s for s in tamamlanan_siparisler if s['satici'] == session['user']]
    
    html = STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
    html += "<div class='content'>"
    html += "<h2>İlanlarım</h2>"
    
    html += "<h3>Aktif İlanlar</h3>"
    if aktif_ilanlar:
        for i in aktif_ilanlar:
            html += f"<div class='card'>"
            html += f"<h3>{i['ad']}</h3>"
            html += f"<p><b>Fiyat:</b> {i['fiyat']}</p>"
            html += f"<p><b>Kalan Stok:</b> {i['stok']}</p>"
            html += f"<form action='/ilan_sil/{i['id']}' method='post'>"
            html += "<button class='delete-button'>İlanı Sil (1 hak geri ver)</button>"
            html += "</form>"
            html += "</div>"
    else:
        html += "<p>Aktif ilanınız bulunmamaktadır.</p>"
    
    html += "<h3>Alınan Siparişler</h3>"
    if tamamlanan:
        for s in tamamlanan:
            alici_user = next((u for u in users if u['username'] == s['alici']), None)
            tel = alici_user['telefon'] if alici_user else "Bilinmiyor"
            html += f"<div class='card'>"
            html += f"<p><b>Ürün:</b> {s['ad']}</p>"
            html += f"<p><b>Fiyat:</b> {s['fiyat']}</p>"
            html += f"<p><b>Alıcı:</b> {s['alici']}</p>"
            html += f"<p><b>Telefon:</b> {tel}</p>"
            html += f"<p><b>Tarih:</b> {s['tarih']}</p>"
            html += "</div>"
    else:
        html += "<p>Tamamlanan siparişiniz bulunmamaktadır.</p>"
    
    html += "<br><a href='/ilan_ac'>Yeni İlan Aç</a>"
    html += "</div>"
    return html

# Satın al işlemi
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
    
    satici_user = next((u for u in users if u['username'] == ilan['satici']), None)
    satici_tel = satici_user['telefon'] if satici_user else "Bilinmiyor"
    
    html = STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
    html += "<div class='content'>"
    html += "<h2 style='color:#00ff41;'>✅ Satın Alma Başarılı!</h2>"
    html += f"<p>{ilan['ad']} satın alındı.</p>"
    html += f"<p>Satıcı ile iletişime geçin:</p>"
    html += f"<p><b>Telefon:</b> {satici_tel}</p>"
    html += "<br><a href='/'>Ana Sayfa'ya Dön</a>"
    html += "</div>"
    return html

# İlan sil (kullanıcı kendi ilanı)
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

# Çıkış yap
@app.route('/cikis')
def cikis():
    session.pop('user', None)
    return redirect('/')

# Admin giriş (şifre soran sayfa düzeltildi)
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        sifre = request.form.get('sifre', '')
        if sifre == ADMIN_SIFRE:
            session['admin'] = True
            return redirect('/admin')
        else:
            return STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>" + "<div class='content'><h2 style='color:#ff4444;'>Yanlış şifre!</h2><a href='/admin_login'>Tekrar Dene</a></div>"
    
    html = STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
    html += "<div class='content'>"
    html += "<h2>🔐 Admin Girişi</h2>"
    html += "<p>Admin şifresi ile giriş yap.</p>"
    html += "<form method='post'>"
    html += "<input type='password' name='sifre' placeholder='Şifre' required autofocus>"
    html += "<button>Giriş Yap</button>"
    html += "</form>"
    html += "</div>"
    return html

# Admin panel
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/admin_login')
    
    html = STYLE + "<div class='header'><a href='/admin_cikis'>Çıkış Yap</a></div>"
    html += "<div class='content'>"
    html += "<h1>🔐 Admin Paneli</h1>"
    
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
    
    html += "<h2>👥 Kullanıcılar</h2>"
    if users:
        for u in users:
            html += f"<div class='card'>"
            html += f"<p><b>{u['username']}</b></p>"
            html += f"<p>Telefon: {u['telefon']}</p>"
            html += f"<p>İlan Hakkı: {u['ilan_hakki']}</p>"
            html += f"<form action='/kullanici_sil/{u['username']}' method='post'>"
            html += "<button class='delete-button'>Kullanıcıyı Sil</button>"
            html += "</form>"
            html += "</div>"
    else:
        html += "<p>Kullanıcı yok.</p>"
    
    html += "<h2>📦 Tüm İlanlar</h2>"
    if ilanlar:
        for i in ilanlar:
            star = " ⭐ Öne Çıkarılmış" if i.get('one_cikar') else ""
            html += f"<div class='card'>"
            html += f"<p><b>{i['ad']}</b> - {i['fiyat']} ({i['satici']}){star}</p>"
            html += f"<p>Stok: {i['stok']}</p>"
            html += f"<form action='/one_cikar/{i['id']}' method='post'>"
            html += "<button class='highlight-button'>Öne Çıkar</button>"
            html += "</form>"
            html += f"<form action='/ilan_sil_admin/{i['id']}' method='post'>"
            html += "<button class='delete-button'>Sil</button>"
            html += "</form>"
            html += "</div>"
    else:
        html += "<p>İlan yok.</p>"
    
    html += "<br><a href='/'>← Ana Sayfa</a>"
    html += "</div>"
    return html

# Admin route'lar
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

# Uygulama çalıştır
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))