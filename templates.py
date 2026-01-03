# templates.py - Tüm HTML şablonları burada (app.py ile aynı klasöre koy)

IBAN_UYARI = """
<b>IBAN:</b> TR350006400000163002969560<br>
<b>Alıcı Adı:</b> Haşim Seviniş<br>
<b>Banka:</b> Garanti BBVA<br><br>
<span style="color:#ff4444; font-weight:bold;">
⚠️ Açıklama kısmına MUTLAKA KULLANICI ADINI yaz!<br>
Yazmazsan ödeme onaylanmaz ve ilan açamazsın!
</span>
<p>İlan açtırma parası: 25 TL</p>
"""

STYLE = """
<style>
    body { background:#000000; color:#00ff00; font-family:Arial, sans-serif; margin:0; padding:0; min-height:100vh; box-sizing:border-box; }
    h1 { color:#00ff41; text-align:center; margin:30px 0 50px; font-size:28px; }
    h2 { color:#00ff41; text-align:center; margin:20px 0; font-size:24px; }
    h3 { color:#00ff41; margin:15px 0; font-size:20px; }
    p { line-height:1.6; font-size:16px; margin:10px 0; }
    a { color:#00ff00; text-decoration:none; font-weight:bold; }
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
    button:hover { background:#00ff00; }
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
        .header a, .header span { padding:6px 12px; font-size:13px; margin-left:5px; }
        h1 { font-size:24px; }
    }
</style>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
"""

# Ana sayfa şablonu
ANA_SAYFA = STYLE + """
<div class='header'>
    {% if session.user %}
        <span>{{ session.user }} (Hak: {{ hak }})</span>
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
    {% if ilanlar %}
        {% for i in ilanlar %}
            <div class='card'>
                <h3>{{ i.ad }} {% if i.one_cikar %}⭐{% endif %}</h3>
                <p><b>Fiyat:</b> {{ i.fiyat }}</p>
                <p><b>Satıcı:</b> {{ i.satici }}</p>
                <p><b>Stok:</b> {{ i.stok }}</p>
                {% if session.user and session.user != i.satici %}
                    <form action='/satin_al/{{ i.id }}' method='post'>
                        <button class='buy-button'>Satın Al</button>
                    </form>
                {% endif %}
            </div>
        {% endfor %}
    {% else %}
        <p style='text-align:center; padding:100px 0; font-size:18px;'>😢 Şu an ilan yok.</p>
    {% endif %}
    <footer>Sınıf Pazarı © 2026</footer>
</div>
"""

# Kayıt şablonu
KAYIT = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2>Kayıt Ol</h2>
    <form method='post'>
        <input name='username' placeholder='Kullanıcı Adı' required>
        <input type='password' name='password' placeholder='Şifre' required>
        <input name='telefon' placeholder='Telefon (05xxxxxxxxxx)' required>
        <button>Kayıt Ol</button>
    </form>
    <br><a href='/giris'>Giriş Yap</a>
</div>
"""

# Giriş şablonu
GIRIS = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2>Giriş Yap</h2>
    <form method='post'>
        <input name='username' placeholder='Kullanıcı Adı' required>
        <input type='password' name='password' placeholder='Şifre' required>
        <button>Giriş Yap</button>
    </form>
    <br><a href='/kayit'>Kayıt Ol</a>
</div>
"""

# İlan aç şablonu
ILAN_AC = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2>Yeni İlan Aç</h2>
    <form method='post'>
        <input name='ad' placeholder='İlan Başlığı' required>
        <input name='fiyat' placeholder='Fiyat (örn: 250 TL)' required>
        <input type='number' name='stok' placeholder='Stok Miktarı' value='1' min='1' required>
        <button>İlan Aç</button>
    </form>
</div>
"""

# İlanlarım şablonu
ILANLARIM = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2>İlanlarım</h2>
    {% if ilanlar %}
        {% for i in ilanlar %}
            <div class='card'>
                <h3>{{ i.ad }}</h3>
                <p><b>Fiyat:</b> {{ i.fiyat }}</p>
                <p><b>Stok:</b> {{ i.stok }}</p>
                <p><b>Satın Alanlar:</b></p>
                {% if i.satin_alanlar %}
                    {% for alici in i.satin_alanlar %}
                        {% set alici_user = users|selectattr('username', 'equalto', alici.alan)|first %}
                        <p>{{ alici.alan }} - Tel: {{ alici_user.telefon if alici_user else 'Bilinmiyor' }}</p>
                    {% endfor %}
                {% else %}
                    <p>Yok</p>
                {% endif %}
                <form action='/ilan_sil/{{ i.id }}' method='post'>
                    <button class='delete-button'>İlanı Sil (Hak geri)</button>
                </form>
            </div>
        {% endfor %}
    {% else %}
        <p style='text-align:center; padding:100px 0;'>Henüz ilanın yok.</p>
    {% endif %}
    <a href='/ilan_ac'>Yeni İlan Aç</a>
</div>
"""

# Satın al başarılı şablonu
SATIN_AL_BASARILI = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2 style='color:#00ff41;'>Satın Alındı!</h2>
    <p>{{ ilan_ad }} satın alındı.</p>
    <p><b>Satıcı Tel:</b> {{ satici_tel }}</p>
    <a href='/'>Ana Sayfa</a>
</div>
"""

# Ödeme gerekli şablonu
ODEME_GEREKLI = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2>İlan Hakkın Yok</h2>
    {{ IBAN_UYARI | safe }}
    <p>Ödeme yapınca admin onaylayacak.</p>
    <a href='/'>Ana Sayfa</a>
</div>
"""

# Hata şablonu
HATA = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2 style='color:#ff4444;'>Hata!</h2>
    <p>{{ mesaj }}</p>
    <a href='/'>Ana Sayfa</a>
</div>
"""

# Admin giriş şablonu
ADMIN_LOGIN = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2>🔐 Admin Girişi</h2>
    <form method='post'>
        <input type='password' name='sifre' placeholder='Şifre' required>
        <button>Giriş Yap</button>
    </form>
</div>
"""

# Admin panel şablonu
ADMIN = STYLE + """
<div class='header'><a href='/admin_cikis'>Çıkış</a></div>
<div class='content'>
    <h1>🔐 Admin Paneli</h1>
    
    <h2>⏳ Bekleyen Ödemeler</h2>
    {% if bekleyen_odemeler %}
        {% for o in bekleyen_odemeler %}
            <div class='card'>
                <p>Kullanıcı: {{ o.username }}</p>
                <form action='/odeme_onayla/{{ o.id }}' method='post'>
                    <button>Onayla</button>
                </form>
            </div>
        {% endfor %}
    {% else %}
        <p>Yok</p>
    {% endif %}
    
    <h2>👥 Kullanıcılar</h2>
    {% for u in users %}
        <div class='card'>
            <p>{{ u.username }} {% if u.banned %}(Banlı){% endif %}</p>
            <p>Tel: {{ u.telefon }}</p>
            <p>Hak: {{ u.ilan_hakki }}</p>
            {% if u.banned %}
                <form action='/ban_kaldir/{{ u.username }}' method='post'>
                    <button>Ban Kaldır</button>
                </form>
            {% else %}
                <form action='/banla/{{ u.username }}' method='post'>
                    <button class='delete-button'>Banla</button>
                </form>
            {% endif %}
        </div>
    {% endfor %}
    
    <h2>📦 İlanlar</h2>
    {% for i in ilanlar %}
        <div class='card'>
            <p>{{ i.ad }} - {{ i.fiyat }} ({{ i.satici }}) {% if i.one_cikar %}⭐{% endif %}</p>
            <p>Stok: {{ i.stok }}</p>
            <form action='/one_cikar/{{ i.id }}' method='post'>
                <button class='highlight-button'>Öne Çıkar</button>
            </form>
            <form action='/ilan_sil_admin/{{ i.id }}' method='post'>
                <button class='delete-button'>Sil</button>
            </form>
        </div>
    {% endfor %}
    
    <a href='/'>Ana Sayfa</a>
</div>
"""