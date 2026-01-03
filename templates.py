# templates.py - Tüm HTML şablonları (app.py ile aynı klasöre koy)

IBAN_UYARI = """
<b>IBAN:</b> TR350006400000163002969560<br>
<b>Alıcı:</b> Haşim Seviniş<br>
<b>Banka:</b> Garanti BBVA<br><br>
<span style="color:#ff4444; font-weight:bold;">
⚠️ Açıklama kısmına KULLANICI ADINI yaz!<br>
Yazmazsan ödeme onaylanmaz!
</span>
"""

STYLE = """
<style>
    body { background:#000; color:#00ff00; font-family:Arial; margin:0; padding:0; min-height:100vh; }
    h1 { color:#00ff41; text-align:center; margin:30px 0; font-size:28px; }
    .header { position:fixed; top:0; left:0; right:0; background:#000; padding:10px; text-align:right; border-bottom:2px solid #00ff00; z-index:100; }
    .header a { background:#00aa00; color:#000; padding:8px 16px; border-radius:20px; font-size:14px; margin-left:10px; font-weight:bold; }
    .content { padding-top:70px; max-width:600px; margin:auto; padding-left:10px; padding-right:10px; }
    .card { background:#0a0a0a; border:2px solid #00ff00; border-radius:20px; padding:25px; margin:20px 0; box-shadow:0 0 15px rgba(0,255,0,0.3); }
    input { background:#111; color:#00ff00; border:2px solid #00ff00; border-radius:12px; padding:14px; width:100%; margin:10px 0; box-sizing:border-box; font-size:16px; }
    button { background:#00aa00; color:#000; padding:14px; border:none; border-radius:12px; width:100%; font-weight:bold; font-size:18px; margin:10px 0; }
    button:hover { background:#00ff00; }
    .warn { background:#330000; border:2px solid #ff4444; border-radius:15px; padding:20px; margin:20px 0; }
    .buy { background:#ff8800; color:#000; }
    .delete { background:#ff0000; color:#fff; }
    footer { text-align:center; padding:30px; color:#006600; font-size:14px; }
    @media (max-width:600px) { .header a { padding:6px 12px; font-size:13px; } }
</style>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
"""

ANA_SAYFA = STYLE + """
<div class='header'>
    {% if session.user %}
        <b>{{ session.user }}</b> (Hak: {{ hak }}) | <a href='/ilan_ac'>İlan Aç</a> | <a href='/ilanlarim'>İlanlarım</a> | <a href='/cikis'>Çıkış</a>
    {% else %}
        <a href='/kayit'>Kayıt Ol</a> <a href='/giris'>Giriş Yap</a>
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
                        <button class='buy'>Satın Al</button>
                    </form>
                {% endif %}
            </div>
        {% endfor %}
    {% else %}
        <p style='text-align:center; padding:100px 0;'>😢 Şu an ilan yok.</p>
    {% endif %}
    <footer>Sınıf Pazarı © 2026</footer>
</div>
"""

KAYIT = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2>Kayıt Ol</h2>
    <form method='post'>
        <input name='username' placeholder='Kullanıcı Adı' required>
        <input type='password' name='password' placeholder='Şifre' required>
        <input name='telefon' placeholder='Telefon' required>
        <button>Kayıt Ol</button>
    </form>
    <br><a href='/giris'>Giriş Yap</a>
</div>
"""

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

ILAN_AC = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2>Yeni İlan Aç</h2>
    <form method='post'>
        <input name='ad' placeholder='Başlık' required>
        <input name='fiyat' placeholder='Fiyat' required>
        <input type='number' name='stok' placeholder='Stok' value='1' min='1' required>
        <button>İlan Aç</button>
    </form>
</div>
"""

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
                <p><b>Stok:</b> {{ i.stok }}</p>
                <form action='/ilan_sil/{{ i.id }}' method='post'>
                    <button class='delete'>İlanı Sil</button>
                </form>
            </div>
        {% endfor %}
    {% else %}
        <p>Aktif ilan yok.</p>
    {% endif %}
    
    <h3>Tamamlanan Siparişler</h3>
    {% if tamamlanan %}
        {% for s in tamamlanan %}
            <div class='card'>
                <p><b>Ürün:</b> {{ s.ad }}</p>
                <p><b>Alıcı:</b> {{ s.alici }}</p>
                <p><b>Tel:</b> {{ s.tel }}</p>
                <p><b>Tarih:</b> {{ s.tarih }}</p>
            </div>
        {% endfor %}
    {% else %}
        <p>Tamamlanan sipariş yok.</p>
    {% endif %}
    
    <a href='/ilan_ac'>Yeni İlan Aç</a>
</div>
"""

ODEME_GEREKLI = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2>İlan Hakkın Yok</h2>
    {{ IBAN_UYARI | safe }}
    <a href='/'>Ana Sayfa</a>
</div>
"""

HATA = STYLE + """
<div class='header'><a href='/'>Ana Sayfa</a></div>
<div class='content'>
    <h2 style='color:#ff4444;'>Hata!</h2>
    <p>{{ mesaj }}</p>
    <a href='/'>Ana Sayfa</a>
</div>
"""

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
            <p>{{ u.username }} - Tel: {{ u.telefon }} - Hak: {{ u.ilan_hakki }}</p>
            <form action='/kullanici_sil/{{ u.username }}' method='post'>
                <button class='delete'>Kullanıcıyı Sil</button>
            </form>
        </div>
    {% endfor %}
    
    <h2>📦 İlanlar</h2>
    {% for i in ilanlar %}
        <div class='card'>
            <p>{{ i.ad }} - {{ i.fiyat }} ({{ i.satici }}) {% if i.one_cikar %}⭐{% endif %} - Stok: {{ i.stok }}</p>
            <form action='/one_cikar/{{ i.id }}' method='post'>
                <button>Öne Çıkar</button>
            </form>
            <form action='/ilan_sil_admin/{{ i.id }}' method='post'>
                <button class='delete'>Sil</button>
            </form>
        </div>
    {% endfor %}
    
    <a href='/'>Ana Sayfa</a>
</div>
"""