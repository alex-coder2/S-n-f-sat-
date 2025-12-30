from flask import Flask, request, render_template_string, redirect, url_for, session
import os

app = Flask(__name__)

# Flask için secret key (güvenlik için, rastgele olsun)
app.secret_key = os.getenv('SECRET_KEY', 'super_gizli_anahtar')  # Render'da değişken olarak koyabilirsin

# Şifreyi buraya yaz (istediğin şifreyi koy, mesela "sinif123")
ADMIN_SIFRE = "Vortex1453"  # <--- BURAYI DEĞİŞTİR, İSTEDİĞİN ŞİFREYİ YAZ !!!

urunler = [
    {"id": 1, "ad": "10. Sınıf Fizik Kitabı", "fiyat": "100 TL", "satici": "Ali"},
    {"id": 2, "ad": "Kablosuz Kulaklık", "fiyat": "300 TL", "satici": "Ayşe"},
    {"id": 3, "ad": "Matematik Notları", "fiyat": "50 TL", "satici": "Mehmet"},
    {"id": 4, "ad": "Elden PS4 Kol", "fiyat": "500 TL", "satici": "Can"},
]

bekleyen_siparisler = []
onaylanan_siparisler = []

@app.route('/')
def ana_sayfa():
    return render_template_string('''
    <h1 style="text-align:center; color:#2c3e50; margin-top:30px;">📚 Sınıf Satış</h1>
    <p style="text-align:center; font-size:18px;">Elden veya IBAN ile • Sadece bizim sınıf 😎</p>
    
    <div style="max-width:700px; margin:auto; padding:10px;">
    {% for urun in urunler %}
        <div style="background:#f9f9f9; border:1px solid #ddd; border-radius:12px; padding:20px; margin:20px 0; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
            <h3 style="margin:0 0 10px 0;">{{ urun.ad }}</h3>
            <p style="margin:5px 0; color:#27ae60; font-size:20px; font-weight:bold;">{{ urun.fiyat }}</p>
            <p style="margin:5px 0; color:#7f8c8d;">Satıcı: {{ urun.satici }}</p>
            
            <form action="/siparis/{{ urun.id }}" method="post">
                <input type="text" name="isim" placeholder="Adın Soyadın" required 
                       style="width:100%; padding:12px; margin:10px 0; border:1px solid #ccc; border-radius:8px; font-size:16px;">
                
                <select name="odeme" required 
                        style="width:100%; padding:12px; margin:10px 0; border:1px solid #ccc; border-radius:8px; font-size:16px;">
                    <option value="iban">IBAN ile ödeyeceğim</option>
                    <option value="elden">Elden vereceğim</option>
                </select>
                
                <button type="submit" 
                        style="width:100%; padding:14px; background:#3498db; color:white; border:none; border-radius:8px; font-size:18px; cursor:pointer;">
                    🚀 Sipariş Ver
                </button>
            </form>
        </div>
    {% endfor %}
    </div>
    
    <footer style="text-align:center; margin:40px 0; color:#95a5a6;">
        Güvenli alışveriş knklar ❤️
    </footer>
    ''', urunler=urunler)

@app.route('/siparis/<int:urun_id>', methods=['POST'])
def siparis_ver(urun_id):
    urun = next((u for u in urunler if u['id'] == urun_id), None)
    if not urun:
        return "Ürün bulunamadı!"

    isim = request.form['isim'].strip()
    odeme = "IBAN ile" if request.form['odeme'] == "iban" else "Elden"

    yeni_siparis = {
        "urun": urun['ad'],
        "fiyat": urun['fiyat'],
        "alan": isim,
        "odeme": odeme,
        "satici": urun['satici']
    }
    bekleyen_siparisler.append(yeni_siparis)

    return f'''
    <div style="text-align:center; margin:50px; font-size:18px;">
        <h2 style="color:#27ae60;">✅ Sipariş alındı {isim}!</h2>
        <p>Satıcıyla görüş, <b>{odeme}</b> şeklinde ödeme yap.<br><br>
        Admin onaylayınca işlem tamamlanır 😊</p>
        <a href="/" style="padding:12px 24px; background:#3498db; color:white; text-decoration:none; border-radius:8px;">← Ana Sayfaya Dön</a>
    </div>
    '''

# Admin giriş sayfası
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    hata = None
    if request.method == 'POST':
        sifre = request.form['sifre']
        if sifre == ADMIN_SIFRE:
            session['logged_in'] = True
            return redirect('/admin')
        else:
            hata = "Yanlış şifre knk! Tekrar dene."

    return render_template_string('''
    <div style="text-align:center; margin:100px auto; max-width:400px;">
        <h2>🔐 Admin Girişi</h2>
        {% if hata %}
            <p style="color:red;">{{ hata }}</p>
        {% endif %}
        <form method="post">
            <input type="password" name="sifre" placeholder="Şifreyi gir" required 
                   style="width:100%; padding:12px; margin:15px 0; border-radius:8px; font-size:18px;"><br>
            <button type="submit" 
                    style="width:100%; padding:14px; background:#2ecc71; color:white; border:none; border-radius:8px; font-size:18px;">
                Giriş Yap
            </button>
        </form>
        <br><a href="/">← Ana Sayfa</a>
    </div>
    ''')

# Admin paneli (şifre kontrolü var)
@app.route('/admin')
def admin_panel():
    if not session.get('logged_in'):
        return redirect('/admin_login')

    return render_template_string('''
    <div style="max-width:800px; margin:auto; padding:20px;">
        <h1 style="text-align:center;">🔐 Admin Paneli</h1>
        <p style="text-align:center;"><a href="/admin_cikis">Çıkış yap</a></p>

        <h2 style="color:#e67e22;">Bekleyen Siparişler ({{ bekleyen|length }})</h2>
        {% if bekleyen %}
            {% for s in bekleyen %}
                <div style="background:#fff; border:1px solid #ccc; padding:15px; margin:15px 0; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                    <b>Ürün:</b> {{ s.urun }} ({{ s.fiyat }})<br>
                    <b>Alan Kişi:</b> {{ s.alan }}<br>
                    <b>Ödeme:</b> {{ s.odeme }}<br>
                    <b>Satıcı:</b> {{ s.satici }}<br><br>
                    <form action="/onayla/{{ loop.index0 }}" method="post" style="display:inline;">
                        <button type="submit" style="background:#27ae60; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer;">✅ Onayla</button>
                    </form>
                </div>
            {% endfor %}
        {% else %}
            <p>Şu an bekleyen sipariş yok knk 😎</p>
        {% endif %}

        <h2 style="color:#27ae60;">Onaylanan Siparişler</h2>
        {% if onaylanan %}
            {% for s in onaylanan %}
                <div style="background:#e8f5e8; padding:12px; margin:10px 0; border-radius:8px;">
                    ✅ {{ s.alan }} → {{ s.urun }} ({{ s.odeme }})
                </div>
            {% endfor %}
        {% else %}
            <p>Henüz onaylanan sipariş yok.</p>
        {% endif %}

        <br><a href="/">← Ana Sayfa</a>
    </div>
    ''', bekleyen=bekleyen_siparisler, onaylanan=onaylanan_siparisler)

# Onaylama
@app.route('/onayla/<int:index>', methods=['POST'])
def onayla(index):
    if not session.get('logged_in'):
        return redirect('/admin_login')
    
    if 0 <= index < len(bekleyen_siparisler):
        onaylanan = bekleyen_siparisler.pop(index)
        onaylanan_siparisler.append(onaylanan)
    
    return redirect('/admin')

# Çıkış
@app.route('/admin_cikis')
def admin_cikis():
    session.pop('logged_in', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))