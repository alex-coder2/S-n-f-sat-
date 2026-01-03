# templates.py - Tüm HTML şablonları (app.py ile aynı klasöre koy)

# IBAN uyarısı
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
</div>
"""

# Karanlık tema CSS - uzun ve detaylı
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
        transition: background 0.3s;
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
        transition: transform 0.2s;
    }
    .card:hover { 
        transform: translateY(-5px); 
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

# Ana sayfa şablonu
ANA_SAYFA = STYLE + """
<div class='header'>
    {% if session.user %}
        <span>{{ session.user }} (İlan Hakkı: {{ hak }})</span>
        <a href='/ilan_ac'>İlan Aç</a>
        <a href='/ilanlarim'>İlanlarım</a>
        <a href='/cikis'>Çıkış</a>
    {% else %}
        <a href='/kayit'>Kayıt Ol</a>
        <a href='/giris'>Giriş Yap</a>
    {% endif %}
</div>
<div class='content'>
    <h1>📚 Sınıf Pazarı</h1>
    <p style='text-align:center; font-size:18px; margin-bottom:40px;'>Güvenli ikinci el alışveriş platformu</p>
    
    {% if ilanlar %}
        {% for i in ilanlar %}
            <div class='card'>
                <h3>{{ i.ad }} {% if i.one_cikar %} ⭐ Öne Çıkarılmış {% endif %}</h3>
                <p><b>Fiyat:</b> {{ i.fiyat }}</p>
                <p><b>Satıcı:</b> {{ i.satici }}</p>
                <p><b>Kalan Stok:</b> {{ i.stok }}</p>
                {% if session.user and session.user != i.satici %}
                    <form action='/satin_al/{{ i.id }}' method='post'>
                        <button class='buy-button'>Satın Al</button>
                    </form>
                {% endif %}
            </div>
        {% endfor %}
    {% else %}
        <p style='text-align:center; padding:100px 0; font-size:18px;'>
            😢 Şu an satılık ilan bulunmamaktadır.<br>
            Yeni ilanlar yakında eklenecek!
        </p>
    {% endif %}
    
    <footer>Sınıf Pazarı © 2026 - Tüm hakları saklıdır.</footer>
</div>
"""

# Kayıt ol şablonu
KAYIT = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2>Kayıt Ol</h2>
    <p>Lütfen bilgilerini girerek kayıt ol.</p>
    <form method='post'>
        <input name='username' placeholder='Kullanıcı Adı' required>
        <input type='password' name='password' placeholder='Şifre' required>
        <input name='telefon' placeholder='Telefon (05xxxxxxxxxx)' required>
        <button>Kayıt Ol</button>
    </form>
    <br><p>Zaten hesabın var mı? <a href='/giris'>Giriş Yap</a></p>
</div>
"""

# Giriş yap şablonu
GIRIS = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2>Giriş Yap</h2>
    <p>Hesabına giriş yap.</p>
    <form method='post'>
        <input name='username' placeholder='Kullanıcı Adı' required>
        <input type='password' name='password' placeholder='Şifre' required>
        <button>Giriş Yap</button>
    </form>
    <br><p>Hesabın yok mu? <a href='/kayit'>Kayıt Ol</a></p>
</div>
"""

# İlan aç şablonu
ILAN_AC = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2>Yeni İlan Aç</h2>
    <p>İlan bilgilerini gir.</p>
    <form method='post'>
        <input name='ad' placeholder='İlan Başlığı (örn: 1 aylık Netflix)' required>
        <input name='fiyat' placeholder='Fiyat (örn: 250 TL)' required>
        <input type='number' name='stok' placeholder='Stok Miktarı' value='1' min='1' required>
        <button>İlanı Yayınla</button>
    </form>
</div>
"""

# İlanlarım şablonu
ILANLARIM = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2>İlanlarım</h2>
    
    <h3>Aktif İlanlar</h3>
    {% if aktif_ilanlar %}
        {% for i in aktif_ilanlar %}
            <div class='card'>
                <h3>{{ i.ad }}</h3>
                <p><b>Fiyat:</b> {{ i.fiyat }}</p>
                <p><b>Kalan Stok:</b> {{ i.stok }}</p>
                <form action='/ilan_sil/{{ i.id }}' method='post'>
                    <button class='delete-button'>İlanı Sil (1 hak geri ver)</button>
                </form>
            </div>
        {% endfor %}
    {% else %}
        <p>Aktif ilanınız bulunmamaktadır.</p>
    {% endif %}
    
    <h3>Tamamlanan Siparişler</h3>
    {% if tamamlanan %}
        {% for s in tamamlanan %}
            <div class='card'>
                <p><b>Ürün:</b> {{ s.ad }}</p>
                <p><b>Fiyat:</b> {{ s.fiyat }}</p>
                <p><b>Alıcı:</b> {{ s.alici }}</p>
                <p><b>Telefon:</b> {{ s.tel }}</p>
                <p><b>Tarih:</b> {{ s.tarih }}</p>
            </div>
        {% endfor %}
    {% else %}
        <p>Tamamlanan siparişiniz bulunmamaktadır.</p>
    {% endif %}
    
    <br><a href='/ilan_ac'>Yeni İlan Aç</a>
</div>
"""

# Satın al başarılı şablonu
SATIN_AL_BASARILI = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2 style='color:#00ff41;'>✅ Satın Alma Başarılı!</h2>
    <p><b>Ürün:</b> {{ ilan_ad }}</p>
    <p>Satıcı ile iletişime geçin:</p>
    <p><b>Telefon:</b> {{ satici_tel }}</p>
    <br><a href='/'>Ana Sayfa'ya Dön</a>
</div>
"""

# Ödeme gerekli şablonu
ODEME_GEREKLI = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2>İlan Hakkın Yok</h2>
    <p>İlan açabilmek için ödeme yapman gerekiyor.</p>
    {{ IBAN_UYARI | safe }}
    <p>Ödeme yaptıktan sonra admin onaylayacak ve ilan açabileceksin.</p>
    <a href='/'>Ana Sayfa</a>
</div>
"""

# Hata şablonu
HATA = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2 style='color:#ff4444;'>Hata!</h2>
    <p>{{ mesaj }}</p>
    <br><a href='/'>Ana Sayfa'ya Dön</a>
</div>
"""

# Admin giriş şablonu
ADMIN_LOGIN = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2>🔐 Admin Girişi</h2>
    <p>Admin şifresi ile giriş yap.</p>
    <form method='post'>
        <input type='password' name='sifre' placeholder='Şifre' required>
        <button>Giriş Yap</button>
    </form>
</div>
"""

# Admin panel şablonu
ADMIN = STYLE + """
<div class='header'><a href='/admin_cikis'>Çıkış Yap</a></div>
<div class='content'>
    <h1>🔐 Admin Paneli</h1>
    
    <h2>⏳ Bekleyen Ödemeler</h2>
    {% if bekleyen_odemeler %}
        {% for o in bekleyen_odemeler %}
            <div class='card'>
                <p><b>Kullanıcı:</b> {{ o.username }}</p>
                <form action='/odeme_onayla/{{ o.id }}' method='post'>
                    <button>Onayla (1 İlan Hakkı Ver)</button>
                </form>
            </div>
        {% endfor %}
    {% else %}
        <p>Bekleyen ödeme bulunmamaktadır.</p>
    {% endif %}
    
    <h2>👥 Kullanıcılar</h2>
    {% if users %}
        {% for u in users %}
            <div class='card'>
                <p><b>{{ u.username }}</b></p>
                <p>Telefon: {{ u.telefon }}</p>
                <p>İlan Hakkı: {{ u.ilan_hakki }}</p>
                <form action='/kullanici_sil/{{ u.username }}' method='post'>
                    <button class='delete-button'>Kullanıcıyı Sil</button>
                </form>
            </div>
        {% endfor %}
    {% else %}
        <p>Kullanıcı bulunmamaktadır.</p>
    {% endif %}
    
    <h2>📦 Tüm İlanlar</h2>
    {% if ilanlar %}
        {% for i in ilanlar %}
            <div class='card'>
                <p><b>{{ i.ad }}</b> - {{ i.fiyat }} ({{ i.satici }}) {% if i.one_cikar %}⭐{% endif %}</p>
                <p>Stok: {{ i.stok }}</p>
                <form action='/one_cikar/{{ i.id }}' method='post'>
                    <button class='highlight-button'>Öne Çıkar</button>
                </form>
                <form action='/ilan_sil_admin/{{ i.id }}' method='post'>
                    <button class='delete-button'>Sil</button>
                </form>
            </div>
        {% endfor %}
    {% else %}
        <p>İlan bulunmamaktadır.</p>
    {% endif %}
    
    <br><a href='/'>← Ana Sayfa</a>
</div>
"""