from flask import Flask, request, render_template_string
from twilio.rest import Client
import os

app = Flask(__name__)

# Twilio ayarları (Railway'de Variables olarak ekleyeceksin)
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')  # +19405321759
ADMIN_NUMARASI = os.getenv('ADMIN_NUMARASI')  # Senin +90'lı numaran

client = Client(TWILIO_SID, TWILIO_TOKEN)

# Ürünler (istediğin kadar ekleyebilirsin)
urunler = [
    {"id": 1, "ad": "10. Sınıf Fizik Kitabı", "fiyat": "100 TL", "satici": "Ali"},
    {"id": 2, "ad": "Kablosuz Kulaklık", "fiyat": "300 TL", "satici": "Ayşe"},
    {"id": 3, "ad": "Matematik Notları", "fiyat": "50 TL", "satici": "Mehmet"},
    {"id": 4, "ad": "Elden PS4 Kol", "fiyat": "500 TL", "satici": "Can"},
]

siparisler = []  # Bekleyen siparişler

@app.route('/')
def ana_sayfa():
    return render_template_string('''
    <h1 style="text-align:center; color:#2c3e50;">📚 Sınıf Pazarı</h1>
    <p style="text-align:center;">Sadece bizim sınıf kullanır, güvende kalın knklar 😎</p>
    <div style="max-width:600px; margin:auto;">
    {% for urun in urunler %}
        <div style="border:1px solid #ddd; padding:15px; margin:15px 0; border-radius:10px;">
            <b>{{ urun.ad }}</b> - {{ urun.fiyat }} <br>
            Satıcı: {{ urun.satici }}
            <form action="/siparis/{{ urun.id }}" method="post">
                <input type="text" name="isim" placeholder="Adın Soyadın" required style="width:100%; padding:8px; margin:10px 0;"><br>
                <select name="odeme" required style="width:100%; padding:8px; margin:10px 0;">
                    <option value="iban">IBAN ile ödeyeceğim</option>
                    <option value="elden">Elden vereceğim</option>
                </select><br>
                <button type="submit" style="width:100%; padding:10px; background:#3498db; color:white; border:none; border-radius:5px;">Sipariş Ver</button>
            </form>
        </div>
    {% endfor %}
    </div>
    ''', urunler=urunler)

@app.route('/siparis/<int:urun_id>', methods=['POST'])
def siparis_ver(urun_id):
    urun = next((u for u in urunler if u['id'] == urun_id), None)
    if not urun:
        return "Ürün bulunamadı!"

    isim = request.form['isim']
    odeme = request.form['odeme']
    odeme_metni = "IBAN ile" if odeme == "iban" else "Elden verecek"

    siparis = {
        "urun": urun['ad'],
        "fiyat": urun['fiyat'],
        "alan": isim,
        "odeme": odeme_metni,
        "satici": urun['satici'],
        "onaylandi": False
    }
    siparisler.append(siparis)

    # Sana SMS gönder
    mesaj = f"Yeni sipariş knk!\n\nÜrün: {siparis['urun']}\nAlan: {isim}\nÖdeme: {odeme_metni}\nSatıcı: {siparis['satici']}\n\nOnaylamak için bu mesaja 'X' yazıp gönder."

    client.messages.create(
        body=mesaj,
        from_=TWILIO_NUMBER,
        to=ADMIN_NUMARASI
    )

    return f'''
    <h2 style="color:green; text-align:center;">✅ Sipariş alındı {isim}!</h2>
    <p style="text-align:center;">Satıcıya bilgi verildi.<br>
    {odeme_metni} şeklinde ödeme yapacaksın.<br><br>
    Yakında onaylanınca haberin olur 😊</p>
    <a href="/">← Ana sayfaya dön</a>
    '''

# Twilio'dan gelen SMS (sen "X" yazınca)
@app.route('/sms_webhook', methods=['POST'])
def sms_webhook():
    gelen_mesaj = request.values.get('Body', '').strip().upper()
    from_number = request.values.get('From')

    if from_number == ADMIN_NUMARASI and gelen_mesaj == 'X':
        if siparisler and not siparisler[-1]["onaylandi"]:
            siparisler[-1]["onaylandi"] = True
            onaylanan = siparisler[-1]
            
            onay_mesaj = f"✅ Sipariş onaylandı!\n\n{onaylanan['alan']} adlı kişi {onaylanan['urun']} aldı.\nÖdeme: {onaylanan['odeme']}\nHayırlı olsun knk!"

            client.messages.create(
                body=onay_mesaj,
                from_=TWILIO_NUMBER,
                to=ADMIN_NUMARASI
            )
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))