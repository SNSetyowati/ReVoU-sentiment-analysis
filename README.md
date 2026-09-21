# ReVoU Sentiment Analysis

Proyek analisis sentimen (sentiment analysis) yang dikembangkan sebagai bagian dari program ReVoU. Proyek ini bertujuan untuk mengklasifikasikan teks (misalnya ulasan, komentar, atau postingan media sosial) ke dalam kategori sentimen seperti positif, negatif, dan netral.

## Deskripsi

Analisis sentimen adalah teknik Natural Language Processing (NLP) yang digunakan untuk mengidentifikasi dan mengekstrak opini atau emosi dari data teks. Proyek ini mencakup proses mulai dari pengumpulan data, pembersihan data (data cleaning), eksplorasi data (EDA), hingga pembangunan model machine learning/deep learning untuk memprediksi sentimen.

## Fitur

- Preprocessing teks (cleaning, tokenization, stopword removal, stemming/lemmatization)
- Exploratory Data Analysis (EDA) untuk memahami distribusi data
- Pelatihan model klasifikasi sentimen
- Evaluasi performa model
- Visualisasi hasil analisis

## Struktur Proyek

```
ReVoU-sentiment-analysis/
├── data/           # Dataset mentah dan hasil preprocessing
├── notebooks/      # Jupyter notebooks untuk eksplorasi dan eksperimen
├── src/            # Kode sumber (preprocessing, training, evaluasi)
├── models/         # Model yang telah dilatih
└── README.md
```

## Cara Menjalankan

1. Clone repository ini:
   ```bash
   git clone https://github.com/SNSetyowati/ReVoU-sentiment-analysis.git
   cd ReVoU-sentiment-analysis
   ```

2. Buat virtual environment dan install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Jalankan notebook atau script sesuai kebutuhan.

## Teknologi

- Python
- Pandas, NumPy
- Scikit-learn
- NLTK / Sastrawi (untuk teks Bahasa Indonesia)
- Jupyter Notebook

## Lisensi

Proyek ini dibuat untuk keperluan pembelajaran di program ReVoU.
