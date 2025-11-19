# 1. Python 3.9'un hafif (slim) sürümünü baz alıyoruz
FROM python:3.9-slim

# 2. Konteyner içindeki çalışma dizinini belirliyoruz
WORKDIR /app

# 3. Önce sadece gereksinimleri kopyalayıp yüklüyoruz
# (Bu adım, kodunuz değişse bile kütüphaneleri tekrar yüklememek için cache kullanır)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Kalan tüm proje dosyalarını (main.py vb.) kopyalıyoruz
COPY . .

# 5. FastAPI'nin varsayılan portunu belirtiyoruz
EXPOSE 8000

# 6. Uygulamayı başlatıyoruz
# ÖNEMLİ: host 0.0.0.0 olmalı, yoksa tarayıcıdan erişemezsiniz.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
