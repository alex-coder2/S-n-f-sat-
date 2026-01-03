from flask import Flask, request, redirect, session
import os
import json
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'vortex_gizli_anahtar_1453_2026_son_sans')

# Admin şifresi
ADMIN_SIFRE = "Vortex1453"

# IBAN bilgisi
IBAN_UYARI = """
<b>IBAN:</b> TR350006400000163002969560<br>
<b>Alıcı Adı:</b> Haşim Seviniş<br>
<b>Banka:</b> Garanti BBVA<br><br>
<span style="color:#ff4444; font-weight:bold;">
⚠️ Açıklama kısmına MUTLAKA KULLANICI ADINI yaz!<br>
Yazmazsan ödeme onaylanmaz ve ilan açamazsın!
</span>
"""

# Karanlık tema CSS - mobil uyumlu + sağ üst butonlar
STYLE = """
<style>
    body { 
        background:#000000; 
        color:#00ff00; 
        font-family: 'Segoe UI', Arial, sans-serif; 
        margin:0; 
        padding:0; 
        min-height:100vh; 
        box-sizing:border-box;
    }
    h1 { 
        color:#00ff41; 
        text-align:center; 
        margin:30px 0 40px; 
        font-size:28px; 
    }
    h2 { 
        color:#00ff41; 
        text-align:center; 
        margin:20px 0; 
    }
    p { 
        line-height:1.6; 
        font-size:16px; 
        margin:10px 0; 
    }
    a { 
        color:#00ff00; 
        text-decoration:none; 
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
    }
    button:hover { 
        background:#00ff00; 
    }
    .card { 
        background:#0a0a0a; 
        border:2px solid #00ff00; 
        border-radius:20px; 
        padding:25px; 
        margin:20px 0; 
        box-shadow:0 0 20px rgba(0,255,0,0.3); 
    }
    .warn { 
        background:#330000; 
        border:2px solid #ff4444; 
        border-radius:15px; 
        padding:20px; 
        margin:20px 0; 
    }
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
    .header a { 
        background:#00aa00; 
        color:#000000; 
        padding:8px 16px; 
        border-radius:20px; 
        font-size:14px; 
        margin-left:10px; 
        font-weight:bold; 
    }
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
    }
    @media (max-width:600px) { 
        .header a { 
            padding:6px 12px; 
            font-size:13px; 
        }
        h1 { font-size:24px; }
    }
</style>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
"""

# Veri dosyaları
USERS_FILE = "users.json"
ILANLAR_FILE = "ilanlar.json"
ODEMELER_FILE = "odemeler.json"

# Veri yükle/kaydet fonksiyonları
def load(file, default=[]):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def save(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Veriler
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
        html += f"<b>{session['user']}</b> (İlan Hakkı: {hak}) | "
        html += "<a href='/ilan_ac'>İlan Aç</a> | <a href='/cikis'>Çıkış</a>"
    else:
        html += "<a href='/kayit'>Kayıt Ol</a> <a href='/giris'>Giriş Yap</a>"
    html += "</div>"
    
    html += "<div class='content'>"
    html += "<h1>📚 Sınıf Pazarı</h1>"
    html += "<p style='text-align:center; font-size:18px; margin-bottom:40px;'>Güvenli ikinci el alışveriş</p>"
    
    if not sirali:
        html += "<p style='text-align:center; padding:100px 0; font-size:18px;'>😢 Şu an satılık ilan yok.<br>Yeni ilanlar yakında gelir!</p>"
    else:
        for i in sirali:
            one = " ⭐ Öne Çıkarılmış" if i.get('one_cikar') else ""
            html += f"<div class='card'>"
            html += f"<h3>{i['ad']}{one}</h3>"
            html += f"<p><b>Fiyat:</b> {i['fiyat']}</p>"
            html += f"<p><b>Satıcı:</b> {i['satici']}</p>"
            html += "</div>"
    
    html += "<footer>Sınıf Pazarı © 2026 - Güvenli Alışveriş</footer></div>"
    return html

@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        telefon = request.form['telefon'].strip()
        if not username or not password or not telefon:
            return STYLE + "<div class='content'><h2>Tüm alanlar zorunlu!</h2><a href='/kayit'>Geri</a></div>"
        if any(u['username'] == username for u in users):
            return STYLE + "<div class='content'><h2>Kullanıcı adı alınmış!</h2><a href='/kayit'>Geri</a></div>"
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
    html += "<form method='post'>"
    html += "<input name='username' placeholder='Kullanıcı Adı' required>"
    html += "<input type='password' name='password' placeholder='Şifre' required>"
    html += "<input name='telefon' placeholder='Telefon (05xxxxxxxxxx)' required>"
    html += "<button>Kayıt Ol</button>"
    html += "</form>"
    html += "<br><a href='/giris'>Zaten hesabın var mı? Giriş Yap</a>"
    html += "</div>"
    return html

@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            session['user'] = username
            return redirect('/')
        return STYLE + "<div class='content'><h2>Yanlış kullanıcı adı veya şifre!</h2><a href='/giris'>Geri</a></div>"
    
    html = STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
    html += "<div class='content'>"
    html += "<h2>Giriş Yap</h2>"
    html += "<form method='post'>"
    html += "<input name='username' placeholder='Kullanıcı Adı' required>"
    html += "<input type='password' name='password' placeholder='Şifre' required>"
    html += "<button>Giriş Yap</button>"
    html += "</form>"
    html += "<br><a href='/kayit'>Hesabın yok mu? Kayıt Ol</a>"
    html += "</div>"
    return html

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
        html += "<p>İlan açabilmek için ödeme yapman gerekiyor.</p>"
        html += f"<div class='warn'>{IBAN_UYARI}</div>"
        html += "<p>Ödeme yaptıktan sonra admin onaylayacak ve ilan açabileceksin.</p>"
        html += "</div>"
        return html
    
    if request.method == 'POST':
        ilan_id = str(uuid.uuid4())
        ilanlar.append({
            "id": ilan_id,
            "ad": request.form['ad'].strip(),
            "fiyat": request.form['fiyat'].strip(),
            "satici": user['username'],
            "one_cikar": False
        })
        user['ilan_hakki'] -= 1
        save(ILANLAR_FILE, ilanlar)
        save(USERS_FILE, users)
        return redirect('/')
    
    html = STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
    html += "<div class='content'>"
    html += "<h2>Yeni İlan Aç</h2>"
    html += "<form method='post'>"
    html += "<input name='ad' placeholder='İlan Başlığı' required>"
    html += "<input name='fiyat' placeholder='Fiyat (örn: 250 TL)' required>"
    html += "<button>İlan Aç</button>"
    html += "</form>"
    html += "</div>"
    return html

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
    html = STYLE + "<div class='header'><a href='/'>Ana Sayfa</a></div>"
    html += "<div class='content'>"
    html += "<h2>🔐 Admin Girişi</h2>"
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
    html += "<div class='content'>"
    html += "<h1>🔐 Admin Paneli</h1>"
    
    # Bekleyen ödemeler
    html += "<h2>⏳ Bekleyen Ödemeler</h2>"
    if bekleyen_odemeler:
        for o in bekleyen_odemeler:
            html += f"<div class='card'>"
            html += f"<p><b>Kullanıcı:</b> {o['username']}</p>"
            html += f"<form action='/odeme_onayla/{o['id']}' method='post'>"
            html += "<button>Onayla (İlan Hakkı Ver)</button>"
            html += "</form>"
            html += "</div>"
    else:
        html += "<p>Bekleyen ödeme yok.</p>"
    
    # İlanlar yönetimi
    html += "<h2>📦 Tüm İlanlar</h2>"
    if ilanlar:
        for i in ilanlar:
            star = " ⭐ Öne Çıkarılmış" if i.get('one_cikar') else ""
            html += f"<div class='card'>"
            html += f"<p><b>{i['ad']}</b> - {i['fiyat']} ({i['satici']}){star}</p>"
            html += f"<form action='/one_cikar/{i['id']}' method='post' style='display:inline; margin:5px;'>"
            html += "<button>Öne Çıkar</button>"
            html += "</form>"
            html += f"<form action='/ilan_sil/{i['id']}' method='post' style='display:inline; margin:5px;'>"
            html += "<button style='background:#ff0000;'>Sil</button>"
            html += "</form>"
            html += "</div>"
    else:
        html += "<p>Henüz ilan yok.</p>"
    
    html += "<br><a href='/'>← Ana Sayfa</a>"
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