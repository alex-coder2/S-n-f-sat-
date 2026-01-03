from flask import Flask, request, redirect, session
import os
import json
import uuid
from datetime import datetime

# templates.py'den her şeyi import et
from templates import *

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'vortex_gizli_anahtar_1453_2026_uzun_versiyon_tam')

# Admin şifresi
ADMIN_SIFRE = "Vortex1453"

# İlan açtırma parası bilgisi
ILAN_PARASI = "25 TL"

# IBAN bilgisi (tam detaylı)
IBAN_UYARI = f"""
<b>IBAN:</b> TR350006400000163002969560<br>
<b>Alıcı Adı:</b> Haşim Seviniş<br>
<b>Banka:</b> Garanti BBVA<br><br>
<span style="color:#ff4444; font-weight:bold;">
⚠️ Açıklama kısmına MUTLAKA KULLANICI ADINI yaz!<br>
Yazmazsan ödeme onaylanmaz ve ilan açamazsın!
</span>
<p>İlan açtırma parası: {ILAN_PARASI}</p>
<p>Ödeme yaptıktan sonra admin onaylayacak ve 1 ilan hakkı alacaksın.</p>
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
                print(f"{file} başarıyla yüklendi.")
                return data
        except Exception as e:
            print(f"{file} yüklenirken hata: {e}")
            return default
    else:
        print(f"{file} dosyası bulunamadı, varsayılan değer döndürülüyor.")
        return default

def save(file, data):
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"{file} başarıyla kaydedildi.")
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
    
    if 'user' in session:
        current_user = next((u for u in users if u['username'] == session['user']), None)
        hak = current_user['ilan_hakki'] if current_user else 0
    else:
        hak = 0
    
    return render_template_string(ANA_SAYFA, ilanlar=sirali, session=session, hak=hak)

# Kayıt ol sayfası
@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        telefon = request.form['telefon'].strip()
        
        if not username or not password or not telefon:
            return render_template_string(HATA, mesaj="Tüm alanlar zorunlu doldurulmalı!")
        
        if any(u['username'] == username for u in users):
            return render_template_string(HATA, mesaj="Bu kullanıcı adı zaten alınmış!")
        
        # Yeni kullanıcı ekle
        users.append({
            "username": username,
            "password": password,
            "telefon": telefon,
            "ilan_hakki": 0
        })
        save(USERS_FILE, users)
        return redirect('/giris')
    
    return render_template_string(KAYIT)

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
        return render_template_string(HATA, mesaj="Yanlış kullanıcı adı veya şifre!")
    
    return render_template_string(GIRIS)

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
        return render_template_string(ODEME_GEREKLI, IBAN_UYARI=IBAN_UYARI)
    
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
    
    return render_template_string(ILAN_AC)

# İlanlarım sayfası (aktif + tamamlanan)
@app.route('/ilanlarim')
def ilanlarim():
    if 'user' not in session:
        return redirect('/giris')
    
    aktif_ilanlar = [i for i in ilanlar if i['satici'] == session['user']]
    tamamlanan = [s for s in tamamlanan_siparisler if s['satici'] == session['user']]
    
    # Tamamlanan siparişler için telefon bilgisi ekle
    for s in tamamlanan:
        alici_user = next((u for u in users if u['username'] == s['alici']), None)
        s['tel'] = alici_user['telefon'] if alici_user else "Bilinmiyor"
    
    return render_template_string(ILANLARIM, aktif_ilanlar=aktif_ilanlar, tamamlanan=tamamlanan)

# Satın al işlemi
@app.route('/satin_al/<id>', methods=['POST'])
def satin_al(id):
    if 'user' not in session:
        return redirect('/giris')
    
    ilan = next((i for i in ilanlar if i['id'] == id), None)
    if not ilan or ilan['stok'] <= 0:
        return render_template_string(HATA, mesaj="Bu ilan stokta yok veya mevcut değil!")
    
    alici = session['user']
    
    # Satın alma kaydı ekle
    ilan['satin_alanlar'].append({"alan": alici})
    ilan['stok'] -= 1
    
    # Tamamlanan siparişlere ekle
    tamamlanan_siparisler.append({
        "ad": ilan['ad'],
        "fiyat": ilan['fiyat'],
        "satici": ilan['satici'],
        "alici": alici,
        "tarih": datetime.now().strftime("%d.%m.%Y %H:%M")
    })
    save(TAMAMLANAN_FILE, tamamlanan_siparisler)
    
    # Stok biterse ilan sil ve satıcıya hak ver
    if ilan['stok'] <= 0:
        ilanlar.remove(ilan)
        satıcı = next((u for u in users if u['username'] == ilan['satici']), None)
        if satıcı:
            satıcı['ilan_hakki'] += 1
            save(USERS_FILE, users)
    
    save(ILANLAR_FILE, ilanlar)
    
    # Satıcı telefonunu alıcıya göster
    satici_user = next((u for u in users if u['username'] == ilan['satici']), None)
    satici_tel = satici_user['telefon'] if satici_user else "Bilinmiyor"
    
    return render_template_string(SATIN_AL_BASARILI, ilan_ad=ilan['ad'], satici_tel=satici_tel)

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

# Admin giriş
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['sifre'] == ADMIN_SIFRE:
            session['admin'] = True
            return redirect('/admin')
    return render_template_string(ADMIN_LOGIN)

# Admin paneli
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/admin_login')
    
    return render_template_string(ADMIN, bekleyen_odemeler=bekleyen_odemeler, users=users, ilanlar=ilanlar)

# Ödeme onayla
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

# İlan öne çıkar
@app.route('/one_cikar/<id>', methods=['POST'])
def one_cikar(id):
    if not session.get('admin'):
        return redirect('/admin_login')
    for i in ilanlar:
        if i['id'] == id:
            i['one_cikar'] = not i.get('one_cikar', False)
    save(ILANLAR_FILE, ilanlar)
    return redirect('/admin')

# Admin ilan sil
@app.route('/ilan_sil_admin/<id>', methods=['POST'])
def ilan_sil_admin(id):
    if not session.get('admin'):
        return redirect('/admin_login')
    ilan = next((i for i in ilanlar if i['id'] == id), None)
    if ilan:
        ilanlar.remove(ilan)
        save(ILANLAR_FILE, ilanlar)
    return redirect('/admin')

# Kullanıcı sil (admin)
@app.route('/kullanici_sil/<username>', methods=['POST'])
def kullanici_sil(username):
    if not session.get('admin'):
        return redirect('/admin_login')
    global users
    users = [u for u in users if u['username'] != username]
    save(USERS_FILE, users)
    return redirect('/admin')

# Admin çıkış
@app.route('/admin_cikis')
def admin_cikis():
    session.pop('admin', None)
    return redirect('/')

# Uygulama çalıştır
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))