MLOps CI/CD: "No Docker on Local" ke Cloud Run🎯 Brief SingkatProject ini mendemonstrasikan alur MLOps modern untuk men-deploy model tanpa Docker atau Dockerfile di laptop developer.Filosofi Utama:Developer Lokal: Cukup Python + Git.Admin / Platform: Cukup setup GCP + GitHub Secrets sekali.CI/CD: Dikerjakan 100% oleh GitHub Actions.Container Build: Otomatis oleh Google Cloud Build (--source).Serving: Google Cloud Run.Metode ini aman, sederhana, dan sangat cocok untuk lingkungan enterprise yang ingin men-standarisasi proses deploy tanpa membebani developer dengan skill containerisasi.🚀 Alur KerjaAlur kerja MLOps yang digunakan dalam project ini:Developer (Lokal):Melatih ulang model (train.py).Mengubah API (app.py).git commit & git push ke GitHub.GitHub Actions (CI/CD):Trigger berjalan otomatis saat ada push ke branch main.Otentikasi ke GCP menggunakan Service Account.Menjalankan gcloud run deploy --source .Google Cloud Build (Otomatis):Menerima source code dari GitHub Actions.Membangun container image secara otomatis (tanpa Dockerfile).Google Cloud Run (Serving):Menerima image baru dari Cloud Build.Men-deploy revisi baru dan menyajikan model yang telah di-update.📁 Struktur ProjectStruktur file sengaja dibuat minimalis.Bashmlops-cloudrun-no-docker/
├── app.py             # API (FastAPI) untuk serving model
├── train.py           # Script untuk training & menyimpan model
├── requirements.txt   # Dependensi Python
├── model.pkl          # File model (hasil dari train.py)
└── .github/
    └── workflows/
        └── deploy-cloudrun.yml # Definisi CI/CD
Catatan Penting:Tidak ada Dockerfile di repositori ini. Cloud Run akan menggunakan Google Cloud Buildpacks untuk mendeteksi requirements.txt dan app.py (dengan Gunicorn/Uvicorn) dan membangun container yang sesuai secara otomatis.1. Development di Local (Simulasi On-Prem)Bagian ini mensimulasikan apa yang developer lakukan di laptop mereka. Mereka tidak perlu tahu apa-apa soal container atau gcloud.1.1. Setup Virtual EnvironmentBash# Buat virtual environment
python3 -m venv venv

# Aktifkan (Mac/Linux)
source venv/bin/activate

# Aktifkan (Windows)
# venv\Scripts\activate

# Install dependensi
pip install --upgrade pip
pip install -r requirements.txt
1.2. Latih ModelJalankan script training untuk menghasilkan file model.pkl.Bashpython train.py
Output yang diharapkan:✅ Model trained and saved to model.pkl1.3. Jalankan API Secara LokalGunakan uvicorn untuk menjalankan FastAPI dari file app.py.Bashuvicorn app:app --reload
1.4. Tes Endpoint LokalBuka terminal lain dan tes menggunakan curl.Tes endpoint root:Bashcurl http://localhost:8000/
Tes endpoint prediksi:Bashcurl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"x": 10}'
Output yang diharapkan (jika modelnya y = 2x):{"x": 10.0, "predicted_y": 20.0}2. Setup GCP (Sekali Saja oleh Admin)Info: Bagian ini cukup dilakukan sekali oleh Admin/Platform Engineer yang memiliki akses ke project GCP.2.1. Aktifkan APIMasuk ke Google Cloud Console dan aktifkan API berikut untuk project Anda:Cloud Run APICloud Build APIArtifact Registry API2.2. Buat Artifact Registry (Opsional)Meskipun kita menggunakan deploy --source, image container yang dihasilkan tetap perlu disimpan di suatu tempat.Region: asia-southeast2 (atau region Anda)Nama Repo: mlops-repoFormat: Docker2.3. Buat Service Account (SA) untuk GitHub ActionsIni adalah akun "robot" yang akan digunakan GitHub Actions untuk berinteraksi dengan GCP.Buka IAM & Admin → Service Accounts → Create.Nama: github-actions-deployerBeri Roles (Peran):Cloud Run Admin (Untuk mendeploy service)Cloud Build Editor (Untuk menjalankan build)Artifact Registry Writer (Untuk menyimpan image)Service Account User (Dibutuhkan agar Cloud Build bisa bertindak atas nama SA Cloud Run)Buat Key (Kunci):Pilih SA yang baru dibuat → tab Keys.Klik Add Key → Create new key → JSON.File JSON akan ter-download. Jaga kerahasiaan file ini!3. Setup GitHub Repo & Secrets3.1. Inisialisasi Git & PushDi folder project Anda:Bashgit init
git add .
git commit -m "Initial no-docker MLOps demo"
git branch -M main
git remote add origin https://github.com/<ORGANISASI>/<REPO>.git
git push -u origin main
(Ganti <ORGANISASI> dan <REPO> dengan nama repo Anda)3.2. Tambah GitHub SecretsMasuk ke repositori GitHub Anda: Settings → Secrets and variables → Actions.Buat 4 repository secrets berikut:SecretDeskripsiContoh NilaiGCP_PROJECT_IDProject ID di GCPastra-mlops-demoGCP_REGIONRegion GCP yang digunakanasia-southeast2GCP_SA_KEYSeluruh isi file JSON Service AccountSalin-tempel semua teks dari file .jsonCLOUD_RUN_SERVICENama service yang akan dibuat di Cloud Runmlops-no-docker-demo4. CI/CD Workflow (GitHub Actions)File .github/workflows/deploy-cloudrun.yml adalah otak dari CI/CD ini.Pipeline ini akan:Berjalan setiap kali ada git push ke branch main.Melakukan checkout kode.Login ke Google Cloud menggunakan Secret yang kita buat.Menjalankan perintah inti:Bashgcloud run deploy $CLOUD_RUN_SERVICE \
  --source . \
  --region $GCP_REGION \
  --allow-unauthenticated
Perintah ini secara ajaib akan:Meng-zip source code.Mengirimnya ke Cloud Build.Cloud Build membangun image.Image disimpan di Artifact Registry.Revisi baru di-deploy ke Cloud Run.Poin Kunci untuk Developer:Developer hanya perlu git push. Mereka tidak perlu memikirkan docker build, docker push, atau gcloud di laptop mereka.5. Deploy Pertama ke Cloud Run5.1. (Opsional) Ubah Pesan di app.pyUntuk menandai deploy pertama Anda, ubah pesan di app.py:Python@app.get("/")
def root():
    return {
        "message": "Hello Astra! 🎉 CI/CD tanpa Dockerfile sudah jalan.",
        "info": "Send POST /predict with JSON {'x': <number>}"
    }
5.2. Commit & PushBashgit add app.py
git commit -m "Initial deploy to Cloud Run"
git push
5.3. Lihat Pipeline BerjalanBuka tab Actions di repo GitHub Anda. Anda akan melihat workflow "Deploy to Cloud Run" berjalan.5.4. Cek Service di Cloud RunSetelah pipeline sukses (✅), buka GCP Console → Cloud Run.Anda akan melihat service baru (contoh: mlops-no-docker-demo).Klik service tersebut dan salin URL endpoint-nya.Tes dari lokal:Bash# Ganti <CLOUD_RUN_URL> dengan URL Anda
curl https://<CLOUD_RUN_URL>/
Tes prediksi:Bashcurl -X POST https://<CLOUD_RUN_URL>/predict \
     -H "Content-Type: application/json" \
     -d '{"x": 10}'
6. Demo "The MLOps Loop" (Perubahan Model)Ini adalah bagian terpenting: menunjukkan bahwa MLOps loop (iterasi) berjalan.6.1. Ubah Model di train.pyKita akan mengubah logika model.Semula: y = 2xKita ubah jadi y = 3x:Python# Di dalam file train.py
...
data = pd.DataFrame({
    "x": [1, 2, 3, 4, 5],
    "y": [3, 6, 9, 12, 15]  # <- DIUBAH DARI [2, 4, 6, 8, 10]
})
...
6.2. Latih Ulang Model (Lokal) & CommitPENTING: Latih ulang model di lokal agar model.pkl ter-update!Bashpython train.py
Output: ✅ Model trained and saved to model.pklSekarang, commit perubahan model dan script training-nya:Bashgit add train.py model.pkl
git commit -m "Update model: change slope to 3x"
git push
6.3. Pipeline Jalan LagiBuka tab Actions di GitHub. Workflow akan berjalan lagi secara otomatis.6.4. Tes Ulang Prediksi (Setelah Deploy Selesai)Tunggu pipeline sukses (✅). Panggil endpoint yang SAMA persis dengan curl:Bashcurl -X POST https://<CLOUD_RUN_URL>/predict \
     -H "Content-Type: application/json" \
     -d '{"x": 10}'
Hasil SEBELUMNYA: {"x": 10.0, "predicted_y": 20.0}Hasil SEKARANG: {"x": 10.0, "predicted_y": 30.0}Ini adalah bukti bahwa:Kode diubah (train.py).Model dilatih ulang (model.pkl).git push memicu CI/CD.Image baru di-build.Cloud Run menyajikan model baru tanpa downtime.7. Mengapa Cocok untuk Enterprise?🛡️ SecurityDeveloper tidak menyimpan credential GCP di laptop mereka.Semua akses GCP dikelola via Service Account yang disimpan di GitHub Secrets terenkripsi.🍰 SimplicityDeveloper hanya butuh 2 skill: Python dan Git.Menghilangkan kompleksitas Docker, docker login, dan gcloud dari alur kerja developer.🔍 Governance & AuditabilitySetiap deployment terekam jejaknya di log GitHub Actions dan Cloud Build.Mudah diintegrasikan dengan Pull Request (PR) approval sebelum merge ke main dan deploy ke production.📈 ScalableAlur kerja yang sama dapat dipakai ulang untuk puluhan microservice model.Mudah dikembangkan untuk multi-environment (dev, staging, prod) dengan branching strategy (misal: git push ke branch staging akan deploy ke service mlops-staging).8. Pengembangan LanjutanFlow ini dapat dikembangkan lebih lanjut dengan:Testing: Menambah pytest dan menjalankannya di GitHub Actions sebelum deploy.Quality Gate: Gagal-kan deploy jika unit test gagal.Integrasi: Sambungkan dengan Model Registry (Vertex AI, MLflow) alih-alih menyimpan model.pkl di Git.Monitoring: Tambahkan monitoring (Cloud Monitoring / Prometheus) untuk melacak performa model.Multi-Stage: Buat workflow yang berbeda untuk environment dev, staging, dan prod dengan approval step manual di GitHub Actions.
