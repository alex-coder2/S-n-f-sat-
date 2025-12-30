
from flask import Flask, request, render_template_string, redirect, session
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'vortex_gizli_anahtar_1453_2025')

# Admin şifresi (istediğin gibi değiştirilebilir ama şu an Vortex1453)
ADMIN_SIFRE = "Vortex1453"

# Senin IBAN bilgilerin (burayı kendi IBAN'ınla doldur)
IBAN_BILGISI = """
<b>IBAN:</b> TR350006400000163002969560<br>
<b>Alıcı Adı:</b> Haşim Seviniş<br>
<b>Banka:</b> Ziraat Bankası <br><br>
<span style="color:red; font-weight:bold;">
⚠️ Mutlaka açıklama kısmına ADINIZI ve SOYADINIZI yazın!<br>
Yoksa para geri döner ve sipariş geçersiz sayılır!
</span>
"""

# Dinamik ürün listesi
urunler = [
    {"id": 1, "ad": "10. Sınıf Fizik Kitabı", "fiyat": "100 TL", "satici": "Ali"},
    {"id": 2, "ad": "Kablosuz Kulaklık", "fiyat": "300 TL", "satici": "Ayşe"},
    {"id": 3, "ad": "Matematik Notları", "fiyat": "50 TL", "satici": "Mehmet"},
]

bekleyen_siparisler = []
onaylanan_siparisler = []

son_urun_id = max([u['id'] for u in urunler] if urunler else [0])

@app.route('/')
def ana_sayfa():
    return render_template_string('''
    <h1 style="text-align:center; color:#2c3e50; margin-top:30px;">📚 Sınıf Satış</h1>
    <p style="text-align:center; font-size:18px;">Elden veya IBAN ile • Güvenli alışveriş 😎</p>
    
    <div style="max-width:700px; margin:auto; padding:10px;">
    {% if urunler %}
        {% for urun in urunler %}
            <div style="background:#f9f9f9; border:1px solid #ddd; border-radius:12px; padding:20px; margin:20px 0; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                <h3>{{ urun.ad }}</h3>
                <p style="color:#27ae60; font-weight:bold; font-size:20px;">{{ urun.fiyat }}</p>
                <p style="color:#7f8c8d;">Satıcı: {{ urun.satici }}</p>
                
                <form action="/siparis/{{ urun.id }}" method="post">
                    <input type="text" name="isim" placeholder="Adın Soyadın (IBAN için zorunlu!)" required 
                           style="width:100%; padding:12px; margin:10px 0; border-radius:8px;">
                    
                    <select name="odeme" required style="width:100%; padding:12px; margin:10px 0; border-radius:8px;">
                        <option value="elden">Elden vereceğim</option>
                        <option value="iban">IBAN ile ödeyeceğim</option>
                    </select>
                    
                    <button type="submit" style="width:100%; padding:14px; background:#3498db; color:white; border:none; border-radius:8px; font-size:18px;">
                        🚀 Sipariş Ver
                    </button>
                </form>
            </div>
        {% endfor %}
    {% else %}
        <p style="text-align:center; color:#95a5a6; font-size:20px;">😢 Şu an satılık ürün yok.<br>Yakında yeni ilanlar gelir!</p>
    {% endif %}
    </div>
    ''', urunler=urunler)

@app.route('/siparis/<int:urun_id>', methods=['POST'])
def siparis_ver(urun_id):
    urun = next((u for u in urunler if u['id'] == urun_id), None)
    if not urun:
        return "<h2>Ürün satıldı veya kaldırıldı!</h2><a href='/'>← Ana Sayfa</a>"

    isim = request.form['isim'].strip()
    odeme_secimi = request.form['odeme']
    odeme_metni = "IBAN ile" if odeme_secimi == "iban" else "Elden"

    # Siparişi kaydet
    yeni_siparis = {
        "urun_id": urun['id'],
        "urun": urun['ad'],
        "fiyat": urun['fiyat'],
        "alan": isim,
        "odeme": odeme_metni,
        "satici": urun['satici']
    }
    bekleyen_siparisler.append(yeni_siparis)

    # IBAN seçildiyse bilgi göster
    if odeme_secimi == "iban":
        ekstra_bilgi = f"<div style='background:#fff3cd; padding:15px; border-radius:10px; margin:20px 0; border:1px solid #ffeaa7;'>{IBAN_BILGISI}</div>"
    else:
        ekstra_bilgi = "<p>Elden ödeme için satıcıyla görüş.</p>"

    return f'''
    <div style="text-align:center; margin:50px; font-size:18px;">
        <h2 style="color:#27ae60;">✅ Sipariş alındı {isim}!</h2>
        <p><b>{urun['ad']}</b> için siparişin alındı.<br>
        Ödeme: <b>{odeme_metni}</b></p>
        {ekstra_bilgi}
        <p>Admin onaylayınca işlem tamamlanır. Teşekkürler!</p>
        <br>
        <a href="/" style="padding:12px 24px; background:#3498db; color:white; text-decoration:none; border-radius:8px;">← Ana Sayfa</a>
    </div>
    '''

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    hata = None
    if request.method == 'POST':
        if request.form['sifre'] == ADMIN_SIFRE:
            session['logged_in'] = True
            return redirect('/admin')
        else:
            hata = "Yanlış şifre!"
    return render_template_string('''
    <div style="text-align:center; margin:100px auto; max-width:400px;">
        <h2>🔐 Admin Girişi</h2>
        {% if hata %}<p style="color:red;">{{ hata }}</p>{% endif %}
        <form method="post">
            <input type="password" name="sifre" placeholder="Şifre" required style="width:100%; padding:12px; margin:15px 0; border-radius:8px;">
            <button type="submit" style="width:100%; padding:14px; background:#2ecc71; color:white; border:none; border-radius:8px;">Giriş Yap</button>
        </form>
    </div>
    ''')

@app.route('/admin')
def admin_panel():
    if not session.get('logged_in'):
        return redirect('/admin_login')

    global son_urun_id
    return render_template_string('''
    <div style="max-width:900px; margin:auto; padding:20px;">
        <h1 style="text-align:center;">🔐 Admin Paneli (Vortex)</h1>
        <p style="text-align:center;"><a href="/admin_cikis">Çıkış yap</a></p>

        <!-- Yeni Ürün Ekle -->
        <h2 style="color:#3498db;">🆕 Yeni İlan Ekle</h2>
        <form action="/urun_ekle" method="post" style="background:#ecf0f1; padding:20px; border-radius:10px; margin:20px 0;">
            <input type="text" name="ad" placeholder="Ürün adı" required style="width:100%; padding:12px; margin:10px 0; border-radius:8px;">
            <input type="text" name="fiyat" placeholder="Fiyat (örn: 250 TL)" required style="width:100%; padding:12px; margin:10px 0; border-radius:8px;">
            <input type="text" name="satici" placeholder="Satıcı adı" required style="width:100%; padding:12px; margin:10px 0; border-radius:8px;">
            <button type="submit" style="width:100%; padding:14px; background:#e74c3c; color:white; border:none; border-radius:8px;">+ Ürün Ekle</button>
        </form>

        <!-- Mevcut Ürünler (Silme ile) -->
        <h2 style="color:#9b59b6;">📦 Mevcut İlanlar ({{ urunler|length }})</h2>
        {% for urun in urunler %}
            <div style="background:#f8f9fa; padding:15px; margin:15px 0; border-radius:10px; border:1px solid #dee2e6; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <b>{{ urun.ad }}</b> - {{ urun.fiyat }} ({{ urun.satici }})
                </div>
                <form action="/urun_sil/{{ urun.id }}" method="post">
                    <button type="submit" style="background:#e74c3c; color:white; padding:8px 16px; border:none; border-radius:5px;">🗑️ Sil</button>
                </form>
            </div>
        {% endfor %}

        <!-- Bekleyen Siparişler -->
        <h2 style="color:#e67e22;">⏳ Bekleyen Siparişler ({{ bekleyen|length }})</h2>
        {% if bekleyen %}
            {% for s in bekleyen %}
                <div style="background:#fff; border:1px solid #ccc; padding:15px; margin:15px 0; border-radius:10px;">
                    <b>Ürün:</b> {{ s.urun }} ({{ s.fiyat }})<br>
                    <b>Alan:</b> {{ s.alan }}<br>
                    <b>Ödeme:</b> {{ s.odeme }}<br>
                    <b>Satıcı:</b> {{ s.satici }}<br><br>
                    <form action="/onayla/{{ loop.index0 }}" method="post">
                        <button type="submit" style="background:#27ae60; color:white; padding:12px 24px; border:none; border-radius:5px; font-size:16px;">✅ Onayla ve Satıştan Kaldır</button>
                    </form>
                </div>
            {% endfor %}
        {% else %}
            <p>Bekleyen sipariş yok.</p>
        {% endif %}

        <h2 style="color:#27ae60;">✅ Onaylananlar</h2>
        {% for s in onaylanan %}
            <div style="background:#e8f5e8; padding:12px; margin:10px 0; border-radius:8px;">
                {{ s.alan }} → {{ s.urun }} ({{ s.odeme }})
            </div>
        {% else %}
            <p>Henüz onaylanan yok.</p>
        {% endfor %}

        <br><a href="/">← Ana Sayfa</a>
    </div>
    ''', urunler=urunler, bekleyen=bekleyen_siparisler, onaylanan=onaylanan_siparisler)

@app.route('/urun_ekle', methods=['POST'])
def urun_ekle():
    if not session.get('logged_in'): return redirect('/admin_login')
    global son_urun_id
    son_urun_id += 1
    urunler.append({
        "id": son_urun_id,
        "ad": request.form['ad'].strip(),
        "fiyat": request.form['fiyat'].strip(),
        "satici": request.form['satici'].strip()
    })
    return redirect('/admin')

@app.route('/urun_sil/<int:urun_id>', methods=['POST'])
def urun_sil(urun_id):
    if not session.get('logged_in'): return redirect('/admin_login')
    global urunler
    urunler = [u for u in urunler if u['id'] != urun_id]
    return redirect('/admin')

@app.route('/onayla/<int:index>', methods=['POST'])
def onayla(index):
    if not session.get('logged_in'): return redirect('/admin_login')
    if 0 <= index < len(bekleyen_siparisler):
        onaylanan = bekleyen_siparisler.pop(index)
        onaylanan_siparisler.append(onaylanan)
        # Ürünü listeden kaldır (satıldı)
        global urunler
        urunler = [u for u in urunler if u['id'] != onaylanan['urun_id']]
    return redirect('/admin')

@app.route('/admin_cikis')
def admin_cikis():
    session.pop('logged_in', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))