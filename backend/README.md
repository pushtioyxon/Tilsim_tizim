# Tilsim Test — Backend (FastAPI + SQLite)

Ushbu backend [backend/database.md](file:///c:/Users/user/Desktop/tilsim/backend/database.md) ma'lumotlar bazasi loyihasi asosida FastAPI va SQLite yordamida yaratilgan.

## Imkoniyatlar:
- **FastAPI**: Yuqori tezlikdagi asinxron API va avtomatik Swagger UI (`/docs`).
- **SQLite + SQLAlchemy 2.0**: Ma'lumotlarni faylda saqlash (`tilsim.db`), kelajakda birgina sozlama orqali PostgreSQL'ga o'tish imkoniyati.
- **Autentifikatsiya**: Telefon raqam va parol bilan ro'yxatdan o'tish, bcrypt bilan xeshlanish, JWT bearer tokenlar.
- **Testlar va savollar**: Oddiy (single), ko'p tanlovli (multiple) va moslashtirish (matching pairs) savol turlari.
- **Test topshirish & Natija**: Test boshlash, javob topshirish va yakuniy ball/foizni avtomatik hisoblash.
- **Fayllar & Media**: Rasm/video/audio yuklash, o'lchamlarini aniqlash va rasmlar uchun avtomatik thumbnail yaratish.

---

## Ishga tushirish (Local Setup):

### 1. Virtual muhit yaratish va faollashtirish:
```powershell
cd c:\Users\user\Desktop\tilsim\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Kutubxonalarni o'rnatish:
```powershell
pip install -r requirements.txt
```

### 3. Serverni ishga tushirish:
```powershell
uvicorn app.main:app --reload --port 8000
```

### 4. API hujjatlari (Swagger):
Brauzerda oching:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
