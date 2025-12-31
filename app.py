from flask import Flask, request, render_template_string, redirect, session
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'vortex_gizli_anahtar_1453_2025')

ADMIN_SIFRE = "Vortex1453"

# Senin IBAN bilgisi
IBAN_BILGISI = """
<b>IBAN:</b> TR350006400000163002969560<br>
<b>Alıcı Adı:</b> Haşim Seviniş<br>
<b>Banka:</b> Garanti BBVA<br><br>
<span style="color:#ff4444; font-weight:bold;">
⚠️ Açıklama kısmına MUTLAKA ADINIZI ve SOYADINIZI yazın!<br>
Yazmazsanız para geri döner ve sipariş geçersiz sayılır!
</span>
"""

# Ürünler (stoklu)
urunler = [
    {"id": 1, "ad": "10. Sınıf Fizik Kitabı", "fiyat": "100 TL", "satici": "Ali", "stok": 1},
    {"id": 2, "ad": "Kablosuz Kulaklık", "fiyat": "300 TL", "satici": "Ayşe", "stok": 2},
    {"id": 3, "ad": "Matematik Notları", "fiyat": "50 TL", "satici": "Mehmet", "stok": 3},
]

bekleyen_siparisler = []
onaylanan_siparisler = []

son_urun_id = max([u['id'] for u in urunler] if urunler else [0])

# Dark tema stil
DARK_STYLE = """
<style>
    body { background:#000000; color:#00ff00; font-family: 'Segoe UI', sans-serif; margin:0; padding:0; }
    h1, h2, h3 { color:#00ff41; text-align:center; }
    a { color:#00ff00; text-decoration:none; }
    input, select { background:#111; color:#00ff00; border:1px solid #00ff00; border-radius:8px; }
    button { background:#00aa00; color:#000; font-weight:bold; border:none; }
    button:hover { background:#00ff00; }
    .kart { background:#0a0a0a; border:1px solid #00ff00; box-shadow:0 0 10px #00ff0044; }
    .uyari { background:#330000; border:1px solid #ff4444; }
    .onay { background:#003300; border:1px solid #00ff00; }
    footer { color:#006600; }
</style>
"""

@app.route('/')
def ana_sayfa():
    gosterilecek_urunler = [u for u in urunler if u['stok'] > 0]
    
    return render_template_string(f'''
    {DARK_STYLE}
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <div style="min-height:100vh; padding:20px 10px;">
        <h1>📚 Sınıf Satış</h1>
        <p style="text-align:center;">Elden veya IBAN • Güvenli Alışveriş 😎</p>
        
        <div style="max-width:500px; margin:auto;">
        {% if gosterilecek_urunler %}
            {% for urun in gosterilecek_urunler %}
                <div class="kart" style="padding:20px; margin:20px 0; border-radius:15px;">
                    <h3>{{ urun.ad }}</h3>
                    <p style="font-size:22px; margin:10px 0;"><b>{{ urun.fiyat }}</b></p>
                    <p>Satıcı: {{ urun.satici }} • Stok: {{ urun.stok }}</p>
                    
                    <form action="/siparis/{{ urun.id }}" method="post">
                        <input type="text" name="isim" placeholder="Ad Soyad (zorunlu)" required 
                               style="width:100%; padding:14px; margin:10px 0; font-size:16px;">
                        
                        <select name="odeme" id="odeme_{{ urun.id }}" onchange="eldenKontrol({{ urun.id }})" required 
                                style="width:100%; padding:14px; margin:10px 0; font-size:16px;">
                            <option value="elden">Elden vereceğim</option>
                            <option value="iban">IBAN ile ödeyeceğim</option>
                        </select>
                        
                        <div id="tel_div_{{ urun.id }}" style="margin:10px 0;">
                            <input type="tel" name="telefon" placeholder="05xxxxxxxxx" 
                                   style="width:100%; padding:14px; font-size:16px;">
                            <p style="color:#ff4444; margin:5px 0;">
                                ⚠️ Elden için telefon zorunlu!<br>
                                Yanlış girersen sipariş geçersiz olabilir.
                            </p>
                        </div>
                        
                        <button type="submit" style="width:100%; padding:16px; margin-top:10px; font-size:18px; border-radius:12px;">
                            🚀 Sipariş Ver
                        </button>
                    </form>
                    
                    <script>
                    function eldenKontrol(id) {{
                        var secim = document.getElementById("odeme_" + id).value;
                        var div = document.getElementById("tel_div_" + id);
                        if (secim == "elden") {{
                            div.style.display = "block";
                            div.querySelector("input").required = true;
                        }} else {{
                            div.style.display = "none";
                            div.querySelector("input").required = false;
                        }}
                    }}
                    eldenKontrol({{ urun.id }});
                    </script>
                </div>
            {% endfor %}
        {% else %}
            <p style="text-align:center; font-size:20px; padding:50px;">😢 Şu an ürün yok<br>Yeni ilanlar yakında!</p>
        {% endif %}
        </div>
        
        <footer style="text-align:center; padding:30px; font-size:14px;">
            Sınıfın Güvenli Pazarı • 2025 ❤️
        </footer>
    </div>
    ''', gosterilecek_urunler=gosterilecek_urunler)

@app.route('/siparis/<int:urun_id>', methods=['POST'])
def siparis_ver(urun_id):
    urun = next((u for u in urunler if u['id'] == urun_id), None)
    if not urun or urun['stok'] <= 0:
        return f"{DARK_STYLE}<h2 style='color:#ff4444; text-align:center; padding:100px;'>Ürün stokta yok!</h2><a href='/'>← Ana Sayfa</a>"

    isim = request.form['isim'].strip()
    odeme_secimi = request.form['odeme']
    telefon = request.form.get('telefon', '').strip()

    if odeme_secimi == "elden" and not telefon:
        return f"{DARK_STYLE}<h2 style='color:#ff4444; text-align:center; padding:100px;'>⚠️ Telefon numarası zorunlu!</h2><a href='/'>← Geri</a>"

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

    if odeme_secimi == "iban":
        ekstra = f"<div class='uyari' style='padding:20px; margin:20px; border-radius:12px;'>{IBAN_BILGISI}</div>"
    else:
        ekstra = f"<p>Satıcı iletişime geçecek<br><b>Telefon:</b> {telefon}</p>"

    return f'''
    {DARK_STYLE}
    <div style="text-align:center; padding:50px 20px; min-height:100vh;">
        <h2 style="color:#00ff00; font-size:28px;">✅ Sipariş Alındı {isim}!</h2>
        <p style="font-size:18px;">{urun['ad']} için siparişin kaydedildi.</p>
        <p><b>Ödeme:</b> {odeme_metni}</p>
        {ekstra}
        <p style="margin-top:30px;">Admin onaylayınca tamamdır.</p>
        <a href="/" style="display:inline-block; padding:16px 32px; background:#00aa00; color:black; font-size:18px; border-radius:12px; margin-top:20px;">← Ana Sayfa</a>
    </div>
    '''

# Diğer route'lar (admin_login, admin, urun_ekle vs.) aynı kalıyor, sadece DARK_STYLE ekledim
# (Yer tasarrufu için kısalttım ama önceki kodundaki gibi devam ediyor, sadece her sayfaya {DARK_STYLE} ekle)

# ... (admin_login, admin_panel, urun_ekle, urun_sil, onayla, admin_cikis aynı, sadece render_template_string'lere {DARK_STYLE} ekle)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))