from flask import Flask, request, render_template_string
from twilio.rest import Client
import os

app = Flask(__name__)

# Twilio ayarları - Render Environment Variables'tan çekiyoruz
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
MESSAGING_SERVICE_SID = os.getenv('MESSAGING_SERVICE_SID')  # MG7edc83f39d571739e3dfece9c46334a9
ADMIN_NUMARASI = os.getenv('ADMIN_NUMARASI')  # +90 ile senin numaran

# Twilio client
client = Client(TWILIO_SID, TWILIO_TOKEN)

# Ürün listesi - istediğin kadar ekleyebilirsin
urunler = [
    {"id": 1, "ad": "10. Sınıf Fizik Kitabı", "fiyat": "100 TL", "satici": "Ali"},
    {"id": 2, "ad": "Kablosuz Kulaklık", "fiyat": "300 TL", "satici": "Ayşe"},
    {"id": 3, "ad": "Matematik Notları (Fotokopi)", "fiyat": "50 TL", "satici": "Mehmet"},
    {"id": 4, "ad": "Elden PS4 Kol", "fiyat": "500 TL", "satici": "Can"},
    {"id": 5, "ad": "Yedek Şarj Aleti", "fiyat": "150 TL", "satici": "Zeynep"},
]

# Siparişleri hafızada tut (restart olursa silinir, sınıf için yeterli)
siparisler = []

@app.route('/')
def ana_sayfa():
    return render_template_string('''
    <h1 style="text-align:center; color:#2c3e50; margin-top:30px;">📚 Sınıf Satış</h1>
    <p style="text-align:center; font-size:18px;">Sadece bizim sınıf kullanır • Elden veya IBAN ile ödeme 😎</p>
    
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
        Sınıfın ikinci el pazarı • Güvenli alışveriş knklar ❤️
    </footer>
    ''', urunler=urunler)

@app.route('/siparis/<int:urun_id>', methods=['POST'])
def siparis_ver(urun_id):
    urun = next((u for u in urunler if u['id'] == urun_id), None)
    if not urun:
        return "<h2>Ürün bulunamadı!</h2><a href='/'>← Geri dön</a>"

    isim = request.form['isim'].strip()
    odeme_secimi = request.form['odeme']
    odeme_metni = "IBAN ile" if odeme_secimi == "iban" else "Elden"

    # Siparişi kaydet
    yeni_siparis = {
        "urun": urun['ad'],
        "fiyat": urun['fiyat'],
        "alan": isim,
        "odeme": odeme_metni,
        "satici": urun['satici']
    }
    siparisler.append(yeni_siparis)

    # Sana SMS gönder
    try:
        mesaj = f"""🚨 YENİ SİPARİŞ KNKK!

Ürün: {yeni_siparis['urun']}
Fiyat: {yeni_siparis['fiyat']}
Alan Kişi: {isim}
Ödeme Şekli: {odeme_metni}
Satıcı: {yeni_siparis['satici']}

Onaylamak için bu mesaja sadece 'X' yazıp gönder."""

        client.messages.create(
            messaging_service_sid=MESSAGING_SERVICE_SID,
            body=mesaj,
            to=ADMIN_NUMARASI
        )
        sms_durum = "✅ SMS başarıyla gönderildi! Yakında sana bildirim gelecek."
    except Exception as e:
        sms_durum = f"⚠️ SMS gönderilirken hata oldu: {str(e)}<br>Ama sipariş kaydedildi, manuel kontrol et."

    return f'''
    <div style="text-align:center; margin:50px; font-size:18px;">
        <h2 style="color:#27ae60;">✅ Sipariş alındı {isim}!</h2>
        <p>Satıcıya bilgi verildi.<br>
        <b>{odeme_metni}</b> şeklinde ödeme yapacaksın.</p>
        <p>{sms_durum}</p>
        <br>
        <a href="/" style="padding:12px 24px; background:#3498db; color:white; text-decoration:none; border-radius:8px;">← Ana Sayfaya Dön</a>
    </div>
    '''

# Sen "X" yazınca onaylama webhook'u
@app.route('/sms_webhook', methods=['POST'])
def sms_webhook():
    gelen_mesaj = request.values.get('Body', '').strip().upper()
    gonderen_numara = request.values.get('From')

    if gonderen_numara == ADMIN_NUMARASI and gelen_mesaj == 'X' and siparisler:
        son_siparis = siparisler[-1]
        
        onay_mesaj = f"""✅ SİPARİŞ ONAYLANDI!

{son_siparis['alan']} adlı kişi
{son_siparis['urun']} ürününü aldı.

Ödeme: {son_siparis['odeme']}
Satıcı: {son_siparis['satici']}

Hayırlı olsun knk! 🎉"""

        try:
            client.messages.create(
                messaging_service_sid=MESSAGING_SERVICE_SID,
                body=onay_mesaj,
                to=ADMIN_NUMARASI
            )
        except:
            pass  # Onay SMS'i başarısız olsa bile devam

    return '', 200

# Render için port ayarı
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)