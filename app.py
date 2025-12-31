from flask import Flask, request, redirect, session
import os
import json

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'vortex_gizli_anahtar_1453_2025')

ADMIN_SIFRE = "Vortex1453"

IBAN_BILGISI = """
<b>IBAN:</b> TR350006400000163002969560<br>
<b>Alıcı Adı:</b> Haşim Seviniş<br>
<b>Banka:</b> Ziraat Bankası<br><br>
<span style="color:#ff4444; font-weight:bold;">
⚠️ Açıklama kısmına MUTLAKA ADINIZI ve SOYADINIZI yazın!<br>
Yazmazsanız para geri döner ve sipariş geçersiz sayılır!
</span>
"""

DARK_STYLE = """
<style>
    body { background:#000000; color:#00ff00; font-family: Arial, sans-serif; margin:0; padding:0; min-height:100vh; }
    h1, h2, h3 { color:#00ff41; text-align:center; margin:20px 0; }
    p { line-height:1.6; font-size:16px; }
    a { color:#00ff00; text-decoration:none; }
    input, select { background:#111111; color:#00ff00; border:2px solid #00ff00; border-radius:12px; padding:14px; font-size:16px; width:100%; box-sizing:border-box; margin:10px 0; }
    button { background:#00aa00; color:black; font-weight:bold; font-size:18px; padding:16px; border:none; border-radius:12px; cursor:pointer; width:100%; margin:10px 0; }
    button:hover { background:#00ff00; }
    .kart { background:#0a0a0a; border:2px solid #00ff00; border-radius:20px; padding:25px; margin:20px 0; box-shadow:0 0 20px rgba(0,255,0,0.3); }
    .uyari { background:#330000; border:2px solid #ff4444; border-radius:15px; padding:20px; margin:20px 0; }
    footer { color:#006600; text-align:center; padding:30px; font-size:14px; }
    @media (max-width: 600px) { .kart { margin:15px 10px; padding:20px; } body { padding:10px; } }
</style>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
"""

DATA_FILE = "data.json"

# Varsayılan veri (dosya yoksa ilk başta bu kullanılır)
default_data = {
    "urunler": [
        {"id": 1, "ad": "10. Sınıf Fizik Kitabı", "fiyat": "100 TL", "satici": "Ali", "stok": 1},
        {"id": 2, "ad": "Kablosuz Kulaklık", "fiyat": "300 TL", "satici": "Ayşe", "stok": 2},
        {"id": 3, "ad": "Matematik Notları", "fiyat": "50 TL", "satici": "Mehmet", "stok": 3},
    ],
    "bekleyen_siparisler": [],
    "onaylanan_siparisler": [],
    "son_urun_id": 3
}

# Verileri dosyadan yükle
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return default_data

# Verileri dosyaya kaydet
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Global veri
data = load_data()
urunler = data["urunler"]
bekleyen_siparisler = data["bekleyen_siparisler"]
onaylanan_siparisler = data["onaylanan_siparisler"]
son_urun_id = data["son_urun_id"]

@app.route('/')
def ana_sayfa():
    gosterilecek_urunler = [u for u in urunler if u['stok'] > 0]
    
    html = DARK_STYLE + "<div style='padding:20px 10px; max-width:600px; margin:auto;'>"
    html += "<h1>📚 Sınıf Satış</h1>"
    html += "<p style='text-align:center; font-size:18px;'>Elden veya IBAN • Güvenli Alışveriş 😎</p>"
    
    if not gosterilecek_urunler:
        html += "<p style='text-align:center; font-size:20px; padding:100px 0;'>😢 Şu an satılık ürün yok<br>Yeni ilanlar yakında!</p>"
    else:
        for urun in gosterilecek_urunler:
            html += f"""
            <div class='kart'>
                <h3>{urun['ad']}</h3>
                <p style='font-size:24px; margin:15px 0;'><b>{urun['fiyat']}</b></p>
                <p>Satıcı: {urun['satici']} • Stok: {urun['stok']}</p>
                
                <form action='/siparis/{urun['id']}' method='post'>
                    <input type='text' name='isim' placeholder='Ad Soyad (zorunlu)' required>
                    
                    <select name='odeme' id='odeme_{urun['id']}' onchange="eldenKontrol({urun['id']})" required>
                        <option value='elden'>Elden vereceğim</option>
                        <option value='iban'>IBAN ile ödeyeceğim</option>
                    </select>
                    
                    <div id='tel_div_{urun['id']}'>
                        <input type='tel' name='telefon' placeholder='05xxxxxxxxxx'>
                        <p style='color:#ff4444; margin:8px 0;'>
                            ⚠️ Elden için telefon zorunlu!<br>
                            Yanlış girersen sipariş geçersiz olabilir.
                        </p>
                    </div>
                    
                    <button type='submit'>🚀 Sipariş Ver</button>
                </form>
                
                <script>
                function eldenKontrol(id) {{
                    var secim = document.getElementById('odeme_' + id).value;
                    var div = document.getElementById('tel_div_' + id);
                    var input = div.querySelector('input');
                    if (secim == 'elden') {{
                        div.style.display = 'block';
                        input.required = true;
                    }} else {{
                        div.style.display = 'none';
                        input.required = false;
                    }}
                }}
                eldenKontrol({urun['id']});
                </script>
            </div>
            """
    
    html += "<footer>Sınıfın Karanlık Pazarı • 2025 ❤️</footer></div>"
    return html

@app.route('/siparis/<int:urun_id>', methods=['POST'])
def siparis_ver(urun_id):
    global data
    urun = next((u for u in urunler if u['id'] == urun_id), None)
    if not urun or urun['stok'] <= 0:
        return DARK_STYLE + "<div style='text-align:center; padding:100px;'><h2 style='color:#ff4444;'>Ürün stokta yok!</h2><a href='/'>← Ana Sayfa</a></div>"

    isim = request.form['isim'].strip()
    odeme_secimi = request.form['odeme']
    telefon = request.form.get('telefon', '').strip()

    if odeme_secimi == "elden" and not telefon:
        return DARK_STYLE + "<div style='text-align:center; padding:100px;'><h2 style='color:#ff4444;'>⚠️ Telefon zorunlu!</h2><a href='/'>← Geri</a></div>"

    odeme_metni = "IBAN ile" if odeme_secimi == "iban" else "Elden"

    yeni_siparis = {
        "urun_id": urun['id'],
        "urun": urun['ad'],
        "fiyat": urun['fiyat'],
        "alan": isim,
        "telefon": telefon if odeme_secimi == "elden" else "-",
        "odeme": odeme_metni,
        "satici": urun['satici']
    }
    bekleyen_siparisler.append(yeni_siparis)
    urun['stok'] -= 1

    save_data(data)  # Veriyi kaydet

    if odeme_secimi == "iban":
        ekstra = f"<div class='uyari'>{IBAN_BILGISI}</div>"
    else:
        ekstra = f"<p style='font-size:18px;'>Satıcı iletişime geçecek<br><b>Telefon:</b> {telefon}</p>"

    return DARK_STYLE + f"""
    <div style='text-align:center; padding:50px 20px; max-width:600px; margin:auto;'>
        <h2 style='font-size:28px;'>✅ Sipariş Alındı {isim}!</h2>
        <p>{urun['ad']} için siparişin alındı.</p>
        <p><b>Ödeme:</b> {odeme_metni}</p>
        {ekstra}
        <p>Admin onaylayınca tamam.</p>
        <a href='/' style='padding:16px 32px; background:#00aa00; color:black; font-size:18px; border-radius:12px; margin-top:20px; display:inline-block;'>← Ana Sayfa</a>
    </div>
    """

# Diğer route'lar (admin_login, admin, urun_ekle, urun_sil, onayla, admin_cikis) aynı kalıyor
# Sadece her değişiklikte save_data(data) ekle (urun ekle, sil, onayla vs.)

@app.route('/urun_ekle', methods=['POST'])
def urun_ekle():
    if not session.get('logged_in'): return redirect('/admin_login')
    global son_urun_id, data
    son_urun_id += 1
    urunler.append({
        "id": son_urun_id,
        "ad": request.form['ad'].strip(),
        "fiyat": request.form['fiyat'].strip(),
        "satici": request.form['satici'].strip(),
        "stok": int(request.form['stok'])
    })
    data["son_urun_id"] = son_urun_id
    save_data(data)
    return redirect('/admin')

@app.route('/urun_sil/<int:urun_id>', methods=['POST'])
def urun_sil(urun_id):
    if not session.get('logged_in'): return redirect('/admin_login')
    global urunler, data
    urunler = [u for u in urunler if u['id'] != urun_id]
    save_data(data)
    return redirect('/admin')

@app.route('/onayla/<int:index>', methods=['POST'])
def onayla(index):
    if not session.get('logged_in'): return redirect('/admin_login')
    global bekleyen_siparisler, onaylanan_siparisler, data
    if 0 <= index < len(bekleyen_siparisler):
        onaylanan = bekleyen_siparisler.pop(index)
        onaylanan_siparisler.append(onaylanan)
    save_data(data)
    return redirect('/admin')

# admin_login ve admin_cikis aynı

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))