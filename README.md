# WaveSecure - Digital Image Watermarking (Metode DWT-DCT)

WaveSecure adalah aplikasi antarmuka pengguna grafis (GUI) untuk menyisipkan (embed) dan mengekstraksi (extract) watermark digital pada gambar menggunakan metode gabungan Discrete Wavelet Transform (DWT) dan Discrete Cosine Transform (DCT). Proyek ini mengimplementasikan pendekatan spesifik di mana watermark disisipkan ke dalam koefisien DCT dari subband LL (Aproksimasi) yang diperoleh setelah menerapkan DWT pada gambar asli.

Aplikasi ini menyediakan fungsi untuk memilih gambar asli dan gambar watermark, melakukan proses penyisipan dan ekstraksi, menyimpan hasil, menguji ketahanan terhadap noise, dan menghitung metrik kualitas gambar seperti PSNR.

## Fitur

* **Pilihan Gambar:** Memilih gambar sampul (cover image) asli dan gambar watermark dengan mudah melalui dialog file.
* **Penyisipan Watermark DWT-DCT:** Menyisipkan gambar watermark (grayscale) ke dalam gambar asli (grayscale) menggunakan algoritma spesifik berbasis DWT-DCT.
* **Parameter yang Dapat Disesuaikan:**
    * Memilih **Model Wavelet** dari pilihan yang tersedia untuk langkah DWT (meskipun kode utama menggunakan logika DWT-DCT spesifik, UI memungkinkan pilihan model wavelet yang berbeda).
    * Memilih **Tingkat Dekomposisi (Decomposition Level)** untuk DWT.
    * Menyesuaikan parameter **Alpha (Kekuatan)** untuk mengontrol visibilitas dan ketahanan watermark yang disisipkan.
* **Ekstraksi Watermark:**
    * **Ekstraksi dari Gambar Ter-Watermark Aplikasi:** Mengekstrak watermark langsung dari gambar ter-watermark yang dihasilkan dalam sesi aplikasi saat ini. Mendukung ekstraksi blind (tanpa gambar asli) dan non-blind (dengan gambar asli) tergantung ketersediaan gambar asli yang dimuat.
    * **Ekstraksi dari File:** Mengekstrak watermark dari file gambar ter-watermark lainnya yang dimuat dari sistem Anda. Juga mendukung ekstraksi blind dan non-blind.
* **Simpan Hasil:** Menyimpan gambar ter-watermark yang dihasilkan dan gambar watermark yang diekstraksi ke dalam file.
* **Pengujian Ketahanan (Robustness):** Mensimulasikan penambahan noise Gaussian pada gambar ter-watermark dan mencoba mengekstrak watermark untuk mengevaluasi ketahanannya terhadap serangan noise.
* **Perhitungan Imperceptibility (PSNR):** Menghitung Peak Signal-to-Noise Ratio (PSNR) antara gambar asli dan gambar ter-watermark untuk mengukur distorsi visual yang disebabkan oleh proses penyisipan.
* **GUI Intuitif:** Dibangun dengan `customtkinter` untuk antarmuka yang modern dan mudah digunakan.

## Cara Kerja: Metode DWT-DCT (sesuai implementasi dalam kode ini)

Aplikasi ini menggunakan teknik watermarking hybrid DWT-DCT spesifik yang berfokus pada komponen frekuensi rendah gambar untuk penyisipan.

1.  **Pra-pemrosesan Gambar:**
    * Gambar sampul asli dan gambar watermark dimuat dan dikonversi menjadi skala abu-abu (grayscale).
    * Gambar asli diubah ukurannya ke ukuran tetap (misalnya, 512x512).
    * Gambar watermark diubah ukurannya ke ukuran tetap yang lebih kecil (misalnya, 128x128). Ukuran-ukuran ini dikodekan secara permanen (hardcoded) dalam fungsi `convert_image` dan `embed_watermark_dwtdct`/`extract_watermark_dwtdct`, secara spesifik menentukan ukuran watermark relatif terhadap ukuran subband LL.

2.  **Discrete Wavelet Transform (DWT):**
    * DWT diterapkan pada gambar asli skala abu-abu hingga **Tingkat Dekomposisi** yang ditentukan. Ini memecah gambar menjadi subband frekuensi yang berbeda: subband Aproksimasi (LL) dan subband Detail (LH, HL, HH) di setiap tingkat.
    * Subband LL mengandung sebagian besar energi gambar dan informasi frekuensi rendah, menjadikannya kandidat yang cocok untuk watermarking yang kuat karena modifikasi di sini kurang terlihat tetapi lebih tahan terhadap berbagai serangan.

3.  **Discrete Cosine Transform (DCT) pada Subband LL:**
    * DCT diterapkan secara spesifik pada subband LL yang diperoleh dari DWT.
    * DCT mengubah koefisien domain spasial dari subband LL menjadi koefisien domain frekuensi.

4.  **Penyisipan Watermark:**
    * Nilai piksel watermark skala abu-abu (dinormalisasi atau diskalakan) disisipkan ke dalam *wilayah spesifik* di dalam koefisien DCT dari subband LL.
    * Menurut kode, penyisipan terjadi secara *multiplikatif* dalam sebuah blok yang dimulai sekitar 1/4 dari dimensi koefisien LL_dct (`LL_dct[embed_row_start + i, embed_col_start + j] = LL_dct[embed_row_start + i, embed_col_start + j] * (1.0 + alpha * watermark_float[i, j] / 255.0)`). Ini menargetkan wilayah frekuensi menengah dalam koefisien DCT dari blok LL.
    * Parameter **Alpha** mengontrol kekuatan penyisipan. Nilai alpha yang lebih tinggi meningkatkan visibilitas watermark (berpotensi mengurangi imperceptibility) tetapi dapat meningkatkan ketahanan.

5.  **Inverse DCT (IDCT) pada Subband LL yang Dimodifikasi:**
    * IDCT diterapkan pada koefisien DCT yang dimodifikasi dari subband LL untuk mengubahnya kembali ke domain spasial.

6.  **Inverse DWT (IDWT):**
    * IDWT diterapkan menggunakan koefisien subband LL yang dimodifikasi dan koefisien subband detail asli dari DWT awal.
    * Ini merekonstruksi gambar ter-watermark di domain spasial.
    * Nilai piksel gambar akhir dipotong (clipped) ke rentang yang valid [0, 255].

7.  **Ekstraksi Watermark:**
    * Proses ekstraksi melibatkan penerapan DWT dan kemudian DCT pada subband LL dari gambar ter-watermark (atau versi yang mungkin sudah diserang).
    * Koefisien LL_dct asli diperlukan untuk **Ekstraksi Non-Blind**. Jika gambar asli dimuat, kode menghitung LL_dct asli dan menggunakan formula `((w_coeff / o_coeff) - 1.0) / alpha * 255.0` untuk membalikkan proses penyisipan dan memulihkan nilai piksel watermark.
    * Untuk **Ekstraksi Blind** (ketika gambar asli *tidak* disediakan), kode mengaproksimasi koefisien asli dengan menggunakan *rata-rata* dari koefisien di wilayah penyisipan dari blok LL_dct gambar ter-watermark. Formula ekstraksi yang digunakan adalah `(w_LL_dct[...]- mean_coeff) * 5.0 + 128.0`. Ini adalah aproksimasi spesifik yang diimplementasikan dalam kode.
    * Nilai yang diekstraksi kemudian dipotong (clipped) dan dikonversi kembali menjadi gambar.

## Instalasi

1.  **Clone repositori atau unduh file kode**.
2.  **Pastikan Anda telah menginstal Python**.
3.  **Instal pustaka yang diperlukan**:

    ```bash
    pip install customtkinter Pillow opencv-python numpy PyWavelets scipy
    ```

## Penggunaan

1.  **Jalankan skrip Python:**
    ```bash
    python app.py
    ```

2.  **Penggunaan GUI:**
    * Jendela utama akan muncul dengan tiga area tampilan gambar (Original Image, Watermark, Watermarked Image) dan panel kontrol.
    * Gunakan tombol **"Select Original"** untuk memuat gambar sampul.
    * Gunakan tombol **"Select Watermark"** untuk memuat gambar yang ingin Anda sematkan sebagai watermark.
    * Pilih **Model Wavelet**, **Decomposition Level**, dan nilai **Alpha** yang diinginkan dari bagian parameter.
    * Klik **"Embed Watermark"** untuk melakukan proses penyisipan. Hasilnya akan ditampilkan di panel "Watermarked Image" dan disimpan sebagai `watermarked_image.jpg` di direktori yang sama dengan skrip.
    * Klik **"Save Watermarked"** untuk menyimpan gambar ter-watermark yang sedang ditampilkan ke lokasi yang ditentukan.
    * Untuk mengekstrak watermark:
        * Jika Anda ingin mengekstrak dari gambar yang *baru saja dibuat* oleh aplikasi, pastikan gambar asli masih dimuat dan klik **"Extract From App"**. Ini akan melakukan ekstraksi non-blind. Jika gambar asli *tidak* dimuat, itu akan mencoba ekstraksi blind menggunakan aproksimasi yang diimplementasikan. Watermark yang diekstraksi akan ditampilkan di panel "Watermark".
        * Jika Anda ingin mengekstrak dari *file gambar ter-watermark lainnya*, klik **"Extract From File"** dan pilih file tersebut. Sekali lagi, ekstraksi akan bersifat non-blind jika gambar asli dimuat, atau blind jika tidak.
    * Klik **"Save Extracted"** untuk menyimpan gambar watermark yang diekstraksi yang sedang ditampilkan.
    * Klik **"Test Robustness"** (setelah melakukan penyisipan) untuk menambahkan noise pada gambar ter-watermark dan mencoba ekstraksi dari versi ber-noise tersebut.
    * Klik **"Calculate PSNR"** (setelah melakukan penyisipan) untuk menghitung PSNR antara gambar asli dan gambar ter-watermark.

## Penjelasan Parameter

* **Wavelet Model:** Menentukan jenis keluarga wavelet yang digunakan untuk DWT (misalnya, 'haar', 'db1', dll., meskipun pilihan dropdown mencantumkan nama spesifik seperti "Ikhsan Dwt-Dct"). Pilihan ini dapat memengaruhi karakteristik dekomposisi.
* **Decomposition Level:** Menentukan berapa tingkat dekomposisi yang dilakukan oleh DWT. Tingkat yang lebih tinggi menghasilkan subband LL yang lebih kecil, berpotensi memengaruhi di mana watermark disisipkan relatif terhadap ukuran gambar asli. Level 1 sering digunakan untuk kesederhanaan dan ketahanan dalam penyisipan frekuensi rendah.
* **Alpha (Strength):** Faktor pengali yang mengontrol seberapa besar watermark memengaruhi koefisien LL_dct selama penyisipan. Alpha yang lebih tinggi membuat watermark lebih kuat tetapi dapat meningkatkan distorsi visual.

## Ekstraksi Blind vs. Non-Blind

Aplikasi ini mendukung ekstraksi blind maupun non-blind, *tergantung pada apakah gambar asli saat ini dimuat dalam aplikasi saat Anda mengklik tombol ekstraksi*.

* **Ekstraksi Non-Blind:** Terjadi jika gambar asli berhasil dimuat (`self.original_img_path` bukan `None`). Algoritma ekstraksi menggunakan koefisien LL_dct gambar asli sebagai referensi untuk membalikkan proses penyisipan secara akurat.
* **Ekstraksi Blind:** Terjadi jika gambar asli *tidak* dimuat (`self.original_img_path` adalah `None`). Algoritma ekstraksi menggunakan aproksimasi berdasarkan *rata-rata* koefisien di wilayah penyisipan dari blok LL_dct gambar ter-watermark. *Catatan: Efektivitas metode ekstraksi blind ini sangat bergantung pada algoritma aproksimasi spesifik yang diimplementasikan dalam fungsi `extract_watermark_dwtdct`.*

## Pengujian Ketahanan (Robustness)

Fitur "Test Robustness" menerapkan noise Gaussian pada *gambar ter-watermark yang dihasilkan* (`watermarked_image.jpg`). Kemudian mencoba mengekstrak watermark dari versi yang ber-noise ini. Ini menunjukkan ketahanan skema watermarking terhadap serangan gambar umum (noise aditif). Kualitas watermark yang diekstraksi setelah pengujian ini merupakan indikator ketahanan.

## Perhitungan Imperceptibility (PSNR)

Tombol "Calculate PSNR" menghitung Peak Signal-to-Noise Ratio antara gambar asli yang dipilih dan gambar ter-watermark. PSNR adalah metrik standar yang digunakan untuk mengukur kualitas gambar yang direkonstruksi atau dikompresi dibandingkan dengan versi aslinya. Nilai PSNR yang lebih tinggi menunjukkan distorsi yang lebih sedikit, artinya gambar ter-watermark secara visual lebih dekat dengan gambar asli dan watermark lebih tidak terlihat (imperceptible).

## Screenshoot

![image](https://github.com/user-attachments/assets/affe5a06-cdcf-4885-bff7-3d7f7c50d316)

![image](https://github.com/user-attachments/assets/722e2578-c5d8-4815-acdd-2c90c382299d)

![image](https://github.com/user-attachments/assets/fe6bda81-7a0c-4e58-a707-0eb3fb4ac89d)

