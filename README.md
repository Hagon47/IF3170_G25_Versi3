# Penyusunan Paket dalam Truk

**No Kelompok / Nama Kelompok :** **Kelompok 25 / Versi3**.

Repository ini berisi program optimasi penyusunan paket dalam truk menggunakan algoritma local search. Program mencari susunan paket dengan nilai objektif setinggi mungkin sambil memenuhi batas dimensi dan kapasitas berat truk, aturan paket tidak saling bertumpuk pada ruang yang sama, penopang paket, serta penyusunan paket fragile. 

## Anggota Kelompok

| NIM | Nama |
| --- | --- |
| 13524005 | Geraldo Artemius |
| 13524055 | Junior Natra Situmorang |
| 13524103 | Reynard Nathanael |

## Struktur Folder dan Fungsi File

| Folder / File | Fungsi |
| --- | --- |
| `data/` | Menyimpan file input JSON yang berisi informasi truk dan paket. |
| `data/test1.json` | Contoh input yang dapat digunakan untuk menjalankan program. |
| `docs/` | Folder untuk menyimpan laporan. |
| `output/` | Menyimpan hasil pencarian dalam JSON dan hasil eksperimen. |
| `output/visualization/` | Menyimpan visualisasi HTML. |
| `src/main.py` | File driver yang membaca input, memilih algoritma dan parameter, menjalankan pencarian, dan memanggil visualisasi. |
| `src/algorithm/hill_climbing.py` | Implementasi Steepest Ascent, Sideways Move, Stochastic, dan Random Restart Hill-Climbing. |
| `src/algorithm/simulated_annealing.py` | Implementasi Simulated Annealing, perhitungan probabilitas penerimaan, dan penurunan suhu. |
| `src/algorithm/genetic_algorithm.py` | Implementasi Genetic Algorithm, termasuk pembentukan populasi, fitness, seleksi, crossover, repair, dan mutasi. |
| `src/problem/package.py` | Class `Package` untuk menyimpan atribut paket, posisi, dan rotasi, serta menghitung dimensi dan batas ruang paket. |
| `src/problem/truck.py` | Class `Truck` untuk menyimpan dimensi dan kapasitas berat, serta memeriksa apakah paket berada dalam batas truk. |
| `src/problem/state.py` | Class `State` untuk merepresentasikan susunan paket, membangkitkan state acak dan utilitas lainnya. |
| `src/problem/constraints.py` | Memeriksa validitas state berdasarkan batas truk, overlap, penopang, aturan fragile, dan kapasitas berat. |
| `src/problem/neighbor.py` | Membentuk kandidat posisi dan neighbor melalui perpindahan, pertukaran, serta rotasi paket, menyediakan pembangkitan seluruh neighbor maupun neighbor acak. |
| `src/problem/objective.py` | Menyediakan fungsi objektif untuk menilai suatu state. |
| `src/visualization/normalize.py` | Menyeragamkan format hasil berbagai algoritma agar dapat digunakan oleh visualisasi. |
| `src/visualization/truck_view.py` | Membuat visualisasi tiga dimensi susunan paket dan tabel informasi state. |
| `src/visualization/plots.py` | Membuat grafik nilai objektif dan grafik tambahan untuk Simulated Annealing serta Genetic Algorithm. |
| `src/visualization/visualize.py` | Menggabungkan visualisasi state dan grafik pencarian, kemudian mengekspornya ke HTML. |

## Algoritma

### Hill-Climbing Steepest Ascent

Steepest Ascent mengevaluasi seluruh neighbor yang dihasilkan dan memilih neighbor dengan nilai objektif tertinggi. Pemilihan state hanya dilakukan jika nilainya lebih tinggi daripada state saat ini. Pencarian berhenti ketika tidak ada neighbor, tidak ditemukan peningkatan, atau batas iterasi tercapai.

### Hill-Climbing with Sideways Move

Sideways Move memperluas Steepest Ascent dengan mengizinkan perpindahan ke neighbor yang memiliki nilai objektif sama. Jika terdapat beberapa neighbor terbaik, salah satunya dipilih secara acak.

### Stochastic Hill-Climbing

Stochastic mencoba memperoleh satu neighbor secara acak pada setiap iterasi dan hanya menerimanya jika nilai objektif meningkat. Jika kandidat tidak diperoleh atau nilainya tidak lebih baik, state tetap dipertahankan. Pencarian terus berjalan hingga batas maksimum iterasi.

### Random Restart Hill-Climbing

Random Restart menjalankan Steepest Ascent dari state awal, kemudian mengulang pencarian dari state acak yang baru sebanyak batas restart. Algoritma mengembalikan state terbaik dari seluruh pencarian.

### Simulated Annealing

Simulated Annealing menerima neighbor dengan nilai lebih baik atau sama, serta dapat menerima nilai yang lebih rendah berdasarkan probabilitas yang dipengaruhi selisih nilai objektif dan suhu. Suhu berkurang selama pencarian sehingga peluang menerima penurunan nilai semakin kecil. Pencarian dibatasi oleh suhu minimum dan jumlah iterasi. 

### Genetic Algorithm

Genetic Algorithm membentuk populasi state acak dan mengevaluasinya menggunakan fungsi fitness. Populasi berikutnya dibentuk melalui seleksi roulette wheel, single-point crossover, perbaikan susunan agar valid, dan mutasi. Proses berjalan sesuai jumlah generasi, lalu mengembalikan individu terbaik yang ditemukan sepanjang pencarian.

## Setup dan Menjalankan Program

### 1. Persiapan

Gunakan **Python 3.10 atau lebih baru** 

Buat dan aktifkan virtual environment pada macOS atau Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Untuk Windows melalui Command Prompt:

```bash
py -m venv venv
venv\Scripts\activate.bat
```

Setelah environment aktif, pasang Plotly untuk visualisasi:

```bash
python -m pip install plotly
```
### 2. Siapkan Input

Letakkan file JSON dalam folder `data/`. Data truk berisi `dimensions` (`w`, `l`, `h`) dan `max_capacity`. Setiap paket memiliki `id`, `dimensions`, `value`, `weight`, `is_fragile`, dan `eta`.

### 3. Jalankan Program

**Jalankan dari dalam folder `src`** 

```bash
cd src
python main.py
```

Ikuti menu pada terminal:

1. Masukkan nama file input, misalnya `test1.json`, tanpa awalan `data/`.
2. Pilih `HC`, `SA`, atau `GA`. Jika memilih `HC`, pilih variasi `1` sampai `4` sesuai menu.
3. Pilih fungsi objektif menggunakan nomor berikut. Tekan Enter untuk menggunakan pilihan `1` sebagai default.

| Pilihan | Fungsi Objektif |
| --- | --- |
| `1` | Total nilai paket yang berada di dalam truk. |
| `2` | Total nilai paket di dalam truk dikurangi penalti urutan ETA. Untuk setiap pasangan yang menghalangi pembongkaran, selisih ETA paket atas dan bawah dijumlahkan apabila ETA paket atas lebih besar, lalu dikalikan bobot penalti `5`. |
| `3` | Total nilai paket di dalam truk dibagi total berat paket di dalam truk (Density Heuristic). |

4. Isi parameter algoritma. Tekan Enter pada masing-masing pertanyaan untuk memakai nilai default.

| Algoritma | Parameter pada Terminal | Default |
| --- | --- | --- |
| Semua variasi HC | Maximum iterations; untuk Random Restart berlaku pada setiap proses pencarian | `1000` |
| HC Sideways Move | Maximum sideways move | `100` |
| HC Random Restart | Maximum restart | `10` |
| SA | Initial temperature | `100.0` |
| SA | Penurunan temperature / cooling rate | `0.995` |
| SA | Minimum temperature | `0.1` |
| SA | Maximum iterations | `10000` |
| GA | Jumlah populasi | `30` |
| GA | Jumlah generasi | `50` |

5. Setelah hasil ditampilkan, pilih `y` untuk membuat visualisasi HTML atau `n` untuk selesai tanpa visualisasi.

### 4. Hasil Program

Untuk contoh input `test1.json`, hasil disimpan sebagai:

```text
output/test1_result.json
output/visualization/test1_result.html
```

## Pembagian Tugas

| NIM | Nama | Pembagian Tugas |
| --- | --- | --- |
| 13524005 | Geraldo Artemius | Algoritma Hill-Climbing, input, output, objective function, dan laporan. |
| 13524055 | Junior Natra Situmorang | Algoritma Simulated Annealing, objective function, dan laporan. |
| 13524103 | Reynard Nathanael | Genetic Algorithm, models, visualizer, dan laporan. |
