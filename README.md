# CICD_MLOPS_Course

Project ini menunjukkan alur MLOps modern tanpa Docker & tanpa Dockerfile di laptop developer:
Developer lokal: cukup Python + Git
Tidak perlu Docker di lokal
Tidak perlu gcloud CLI di lokal
CI/CD dikerjakan oleh GitHub Actions
Build container otomatis oleh Cloud Build
Model serving di Cloud Run
Metode ini aman, sederhana, dan cocok untuk enterprise.

📁 Struktur Project
mlops-cloudrun-no-docker/
├── app.py
├── train.py
├── requirements.txt
└── .github/
    └── workflows/
        └── deploy-cloudrun.yml


Tidak ada Dockerfile.
Cloud Run akan membangun container otomatis dari source code dengan bantuan Cloud Build.

1. Development di Local (Simulasi On-Prem)

Tujuan: developer bisa develop & test di lokal tanpa perlu tahu apa-apa soal container.

1.1. Setup Virtual Environment
python3 -m venv venv
source venv/bin/activate    # di Mac/Linux
# Windows: venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

1.2. Train Model
python train.py

Kalau berhasil, akan muncul:
✅ Model trained and saved to model.pkl

1.3. Run API Lokal
uvicorn app:app --reload

Tes endpoint root:

curl http://localhost:8000/

Tes prediksi:

curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"x": 10}'

Kurang lebih hasilnya:
{"x": 10.0, "predicted_y": 20.0}

Ini mensimulasikan on-prem dev / laptop developer.

2. Setup GCP (Sekali Saja oleh Admin / Platform Engineer)

Bagian ini cukup dilakukan oleh 1–2 orang yang pegang akses GCP.

2.1. Enable API di Google Cloud Console

Aktifkan:

Cloud Run API
Cloud Build API
Artifact Registry API

2.2. Buat Artifact Registry (Opsional tapi direkomendasikan)

Walau kita pakai deploy --source, image tetap akan disimpan.

Contoh:

Region: asia-southeast2
Nama repo: mlops-repo
Format: Docker

2.3. Buat Service Account untuk GitHub Actions

Buka: IAM & Admin → Service Accounts → Create
Nama misalnya: github-actions-deployer
Beri roles:
Cloud Run Admin
Cloud Build Editor
Artifact Registry Writer

Buat key:
Add Key → JSON → download file → simpan (akan dipakai di GitHub Secrets)

3. Setup GitHub Repo & Secrets
3.1. Inisialisasi Git & Push ke GitHub

Di folder mlops-cloudrun-no-docker:

git init
git add .
git commit -m "Initial no-docker MLOps demo"
git branch -M main
git remote add origin https://github.com/<ORG>/<REPO>.git
git push -u origin main

Ganti <ORG> dan <REPO> dengan nama organisasi & repo GitHub masing-masing.

3.2. Tambah GitHub Secrets

Masuk ke:
Repo GitHub → Settings → Secrets and variables → Actions

Buat 4 repository secrets:
GCP_PROJECT_ID
Isi: Project ID di GCP (contoh: astra-mlops-demo)

GCP_REGION
Isi: asia-southeast2 (Jakarta) atau region lain yang dipakai

GCP_SA_KEY
Isi: FULL content file JSON service account tadi
Caranya: buka file .json pakai editor text, copy semua isi, paste ke secret

CLOUD_RUN_SERVICE
Isi: nama service Cloud Run, contoh: mlops-no-docker-demo

4. CI/CD Workflow (GitHub Actions → Cloud Run)

File: .github/workflows/deploy-cloudrun.yml

Pipeline ini akan:
Jalan setiap ada git push ke branch main
Setup gcloud di runner GitHub
Enable API (idempotent, aman di-run berulang)

Menjalankan:
gcloud run deploy <service> --source .

yang akan:
Build container image dari source dengan Cloud Build
Simpan image ke Artifact Registry
Deploy ke Cloud Run

Developer hanya perlu:

git add .
git commit -m "update"
git push

Tidak perlu memikirkan build container.

5. Deploy Pertama ke Cloud Run
5.1. Ubah Pesan di app.py (Opsional tapi enak buat demo)

Di app.py, misalnya di endpoint /:

@app.get("/")
def root():
    return {
        "message": "Hello Astra! 🎉 CI/CD tanpa Dockerfile sudah jalan.",
        "info": "Send POST /predict with JSON {'x': <number>}"
    }

5.2. Commit & Push
git add app.py
git commit -m "Initial deploy for Astra"
git push

5.3. Lihat Pipeline Berjalan
Buka tab Actions di GitHub repo
Akan ada workflow Deploy to Cloud Run (Source-based, No Dockerfile) yang running

5.4. Cek Service di Cloud Run
Buka GCP Console → Cloud Run

Harus muncul service bernama sama seperti CLOUD_RUN_SERVICE
Klik → copy URL endpoint

Tes dari lokal:
curl https://<CLOUD_RUN_URL>/

Tes prediksi:

curl -X POST https://<CLOUD_RUN_URL>/predict \
  -H "Content-Type: application/json" \
  -d '{"x": 10}'

6. Demo “Model Change → CI/CD → Serving Baru”
Ini latihan penting untuk menunjukkan MLOps beneran, bukan cuma “deploy sekali”.

6.1. Ubah Model di train.py
Semula: y = 2x
Kita ubah jadi y = 3x:

data = pd.DataFrame({
    "x": [1, 2, 3, 4, 5],
    "y": [3, 6, 9, 12, 15]
})

6.2. Commit & Push
git commit -am "Change model slope to 3x"
git push

6.3. Pipeline Jalan Lagi Otomatis
Buka tab Actions → lihat workflow jalan lagi

Tunggu sampai statusnya ✅ success

6.4. Tes Ulang Prediksi di Cloud Run
Panggil endpoint yang sama, misalnya:

curl -X POST https://<CLOUD_RUN_URL>/predict \
  -H "Content-Type: application/json" \
  -d '{"x": 10}'

Sebelumnya ~20, sekarang jadi ~30.
Itu bukti:

Kode berubah →
Model dilatih ulang →
Image baru dibuild →

Cloud Run serving model baru tanpa manual login ke server.

7. Kenapa Cocok untuk Enterprise? (Angle Enterprise)

Security
1. Developer tidak simpan credential GCP di laptop
2. Semua akses GCP via service account di GitHub Actions (encrypted secrets)

Simplicity
1. Developer cukup Python + Git
2. Tidak perlu Docker skill untuk ikut flow ini

Governance & Auditability
1. Semua deploy terekam di GitHub Actions & Cloud Build
2. Bisa di-review dulu (pull request) sebelum merge ke main

Scalable
1. Flow yang sama bisa dipakai untuk banyak service
2. Bisa dikembangkan ke multi-environment: dev / staging / prod

8. Next Step / Pengembangan Lanjutan
Kalau ingin dikembangkan lebih lanjut, beberapa ide:
-. Tambah unit tests (pytest) dan jalankan di GitHub Actions sebelum deploy
-. Tambah quality gate: kalau test gagal → tidak boleh deploy

Integrasi dengan:
-. Model registry
-. Vertex AI
-. Monitoring (Cloud Monitoring / Prometheus / Grafana)

Tambah multi-stage environment:
-. dev → staging → prod dengan approval step
