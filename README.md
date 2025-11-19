# Uptime Kuma Provisioning

Script otomatis untuk setup Uptime Kuma dengan Docker Compose dan provisioning monitor menggunakan Python API.

## 📋 Daftar Isi

- [Fitur](#fitur)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Konfigurasi](#konfigurasi)
- [Penggunaan](#penggunaan)
- [Struktur File](#struktur-file)
- [Troubleshooting](#troubleshooting)

## ✨ Fitur

- 🐳 Docker Compose setup untuk Uptime Kuma
- 📝 Provisioning otomatis monitor dari file `domain.txt`
- 🔔 Integrasi Microsoft Teams webhook untuk notifikasi
- 🔄 Deteksi duplikasi monitor (skip jika sudah ada)
- 📊 Summary report setelah provisioning

## 📦 Prerequisites

Sebelum memulai, pastikan Anda sudah menginstall:

- **Docker** dan **Docker Compose**
- **Python 3.7+**
- **pip** (Python package manager)

### Install Docker (jika belum ada)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (optional, untuk menghindari sudo)
sudo usermod -aG docker $USER
```

## 🚀 Setup

### 1. Clone atau Download Project

```bash
cd /home/nurahmat/uptime
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

atau menggunakan virtual environment (disarankan):

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 3. Setup Environment Variables

Copy file `.env.example` ke `.env`:

```bash
cp .env.example .env
```

Edit file `.env` dan isi dengan konfigurasi Anda:

```env
UPTIME_KUMA_URL=http://localhost:3001
UPTIME_KUMA_USERNAME=admin
UPTIME_KUMA_PASSWORD=your_secure_password_here
TEAMS_WEBHOOK=https://your-teams-webhook-url-here
```

**Catatan Penting:**
- Ganti `your_secure_password_here` dengan password yang aman untuk Uptime Kuma
- Ganti `your-teams-webhook-url-here` dengan webhook URL Microsoft Teams Anda

### 4. Setup Domain List

Edit file `domain.txt` dan tambahkan URL yang ingin dimonitor (satu URL per baris):

```txt
https://alt.qoin.id/health
https://api.qoinhub.id/health
https://payout-apipg.qoin.id/health
https://e-wallet-api.qoin.id/health
https://mini-api.qoin.id/health
https://next-gen-e-wallet-api.qoin.id/health
https://saas-api.qoin.id/health
```

## ⚙️ Konfigurasi

### Environment Variables (.env)

| Variable | Deskripsi | Default | Required |
|----------|-----------|---------|----------|
| `UPTIME_KUMA_URL` | URL Uptime Kuma instance | `http://localhost:3001` | No |
| `UPTIME_KUMA_USERNAME` | Username untuk login Uptime Kuma | - | Yes |
| `UPTIME_KUMA_PASSWORD` | Password untuk login Uptime Kuma | - | Yes |
| `TEAMS_WEBHOOK` | Microsoft Teams webhook URL | - | Yes |

### Domain List (domain.txt)

Format: Satu URL per baris, baris kosong dan komentar (dimulai dengan `#`) akan diabaikan.

```txt
https://example.com/health
https://api.example.com/health
# https://test.example.com/health  # Ini akan diabaikan
```

## 📖 Penggunaan

### 1. Start Uptime Kuma dengan Docker Compose

```bash
docker-compose up -d
```

Ini akan:
- Download image Uptime Kuma latest
- Create container dengan nama `uptime-kuma`
- Expose port `3001`
- Mount volume `./uptime-kuma-data` untuk persist data

### 2. Setup Initial Admin Account

Akses Uptime Kuma di browser:
```
http://localhost:3001
```

Setup akun admin pertama kali (username dan password harus sesuai dengan yang ada di `.env`).

**Penting:** Pastikan username dan password yang Anda buat di web interface sama dengan yang ada di file `.env`.

### 3. Run Provisioning Script

Setelah Uptime Kuma running dan akun admin sudah dibuat, jalankan script provisioning:

```bash
python3 provision.py
```

Script akan:
1. ✅ Connect ke Uptime Kuma
2. ✅ Login dengan credentials dari `.env`
3. ✅ Check/create Teams notification channel
4. ✅ Read URLs dari `domain.txt`
5. ✅ Create monitor untuk setiap URL yang belum ada
6. ✅ Link semua monitor ke Teams notification
7. ✅ Tampilkan summary report

### 4. Check Status

Lihat status container:

```bash
docker-compose ps
```

Lihat logs:

```bash
docker-compose logs -f
```

Stop container:

```bash
docker-compose down
```

Stop dan hapus volume (⚠️ **Hapus semua data**):

```bash
docker-compose down -v
```

## 📁 Struktur File

```
uptime/
├── docker-compose.yml      # Docker Compose configuration
├── provision.py            # Python provisioning script
├── domain.txt              # List URL yang akan dimonitor
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (jangan commit!)
├── .env.example           # Template environment variables
├── .gitignore             # Git ignore rules
├── README.md              # Dokumentasi ini
└── uptime-kuma-data/      # Data volume (auto-created)
    └── kuma.db            # SQLite database
```

## 🔧 Troubleshooting

### Error: "UPTIME_KUMA_USERNAME is not set in .env file"

**Solusi:** Pastikan file `.env` ada dan berisi semua variable yang diperlukan.

```bash
# Check file .env
cat .env

# Pastikan format benar (tidak ada spasi di sekitar =)
UPTIME_KUMA_USERNAME=admin
```

### Error: "domain.txt not found"

**Solusi:** Pastikan file `domain.txt` ada di direktori yang sama dengan `provision.py`.

```bash
ls -la domain.txt
```

### Error: "Connection refused" atau "Failed to connect"

**Solusi:** Pastikan Uptime Kuma sudah running:

```bash
# Check container status
docker-compose ps

# Start jika belum running
docker-compose up -d

# Check logs untuk error
docker-compose logs
```

### Error: "Login failed" atau "Invalid credentials"

**Solusi:** 
1. Pastikan username dan password di `.env` sesuai dengan yang dibuat di web interface
2. Pastikan sudah setup admin account di `http://localhost:3001`
3. Coba login manual di web interface untuk verifikasi

### Error: "Notification ID is None"

**Solusi:** Script akan otomatis retry dengan mengambil dari notifications list. Jika masih error, cek:
- Teams webhook URL valid
- Uptime Kuma API response

### Monitor tidak muncul di Uptime Kuma

**Solusi:**
1. Refresh browser
2. Check logs script untuk error
3. Verify monitor sudah dibuat dengan:
   ```bash
   # Check database (optional)
   sqlite3 uptime-kuma-data/kuma.db "SELECT name, url FROM monitor;"
   ```

### Port 3001 sudah digunakan

**Solusi:** Edit `docker-compose.yml` dan ubah port mapping:

```yaml
ports:
  - "3002:3001"  # Gunakan port 3002 di host
```

Jangan lupa update `UPTIME_KUMA_URL` di `.env` juga.

## 🔐 Security Notes

- ⚠️ **Jangan commit file `.env`** ke git (sudah ada di `.gitignore`)
- ⚠️ **Gunakan password yang kuat** untuk Uptime Kuma
- ⚠️ **Jangan expose Uptime Kuma** ke internet tanpa authentication tambahan
- ⚠️ **Backup data** secara berkala dari folder `uptime-kuma-data`

## 📝 Contoh Output

```
Found 7 URLs to monitor
Connecting to Uptime Kuma at http://localhost:3001...
Logging in as admin...
Login successful!
Checking for existing Teams notification...
Found existing Teams notification with ID: 1
Checking existing monitors...
➕ Adding monitor for https://alt.qoin.id/health...
   ✓ Monitor 'Alt Health Check' created with ID: 1
➕ Adding monitor for https://api.qoinhub.id/health...
   ✓ Monitor 'Api Health Check' created with ID: 2
⏭️  Skipping https://payout-apipg.qoin.id/health (already exists)
...

============================================================
Provisioning completed!
  Created: 6 monitors
  Skipped: 1 monitors (already exist)
  Total:   7 URLs processed
============================================================
```

## 🤝 Contributing

Jika menemukan bug atau ingin menambahkan fitur, silakan buat issue atau pull request.

## 📄 License

MIT License

## 🔗 Links

- [Uptime Kuma Documentation](https://github.com/louislam/uptime-kuma)
- [Uptime Kuma API Python Library](https://uptime-kuma-api.readthedocs.io/)

