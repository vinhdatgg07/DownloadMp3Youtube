# 🎵 YouTube Playlist to MP3 Downloader

Tool tải video YouTube từ playlist và chuyển đổi thành file MP3 chất lượng cao.

## ✨ Tính năng

- 🔥 **Multi-Threading** - Tải và convert song song 10-20 luồng → Nhanh gấp 10-15 lần!
- 💾 **Kiểm tra dung lượng ổ đĩa** - Cảnh báo trước nếu sắp hết dung lượng!
- 🧹 **Tự động dọn file tạm** - Xóa file .part từ lần tải trước để giải phóng dung lượng!
- ✅ **Chế độ Interactive** - Chạy trước, nhập URL sau (dễ dàng cho người mới!)
- ✅ **Chế độ Command Line** - Truyền URL trực tiếp (nhanh cho người có kinh nghiệm)
- ✅ **Tự động Resume/Continue** - Bỏ qua file đã tải, tiếp tục tải file còn lại!
- ✅ Tải toàn bộ playlist YouTube
- ✅ Tự động chuyển đổi sang MP3 (192kbps)
- ✅ **Lưu ngay vào folder** khi tải xong từng bài
- ✅ Hiển thị đường dẫn file đầy đủ sau khi lưu
- ✅ Hiển thị tiến trình tải chi tiết
- ✅ Đặt tên file theo thứ tự trong playlist
- ✅ Bỏ qua video lỗi và tiếp tục tải
- ✅ Hỗ trợ tải video đơn lẻ
- ✅ Giao diện màu sắc đẹp mắt, dễ theo dõi
- ✅ **Xử lý Ctrl+C mượt mà** - Dừng bất kỳ lúc nào và xem đã tải được bao nhiêu
- ✅ **Tự động retry** - Thử lại 5 lần khi gặp lỗi tạm thời
- ✅ **Đếm số lượng** - Hiển thị số bài hát đã tải thành công và thất bại
- ✅ **Tùy chọn giữ file gốc** - Giữ cả webm/m4a nếu cần
- ✅ **Kiểm tra phiên bản** - Cảnh báo tự động nếu yt-dlp cũ

## 📋 Yêu cầu

- Python 3.7 trở lên
- FFmpeg (cần thiết để chuyển đổi sang MP3)

## 🔧 Cài đặt

### 1. Cài đặt Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Cài đặt FFmpeg

#### Windows:
1. Tải FFmpeg từ: https://ffmpeg.org/download.html
2. Giải nén và thêm đường dẫn vào PATH
3. Hoặc sử dụng Chocolatey:
```bash
choco install ffmpeg
```

#### macOS:
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

## 🚀 Cách sử dụng

Tool hỗ trợ **2 chế độ**: Interactive (nhập URL sau khi chạy) và Command Line (truyền URL trực tiếp).

---

### 🎯 Chế độ 1: Interactive (Khuyến nghị cho người mới)

Chạy chương trình trước, sau đó nhập thông tin khi được hỏi:

```bash
python download_youtube_mp3.py
```

**Chương trình sẽ hỏi:**

```
🎵 Chào mừng đến với YouTube MP3 Downloader! 🎵

📝 Nhập URL playlist hoặc video YouTube:
   Ví dụ: https://www.youtube.com/playlist?list=PLxxxxxx

URL: [Nhập URL ở đây]

📁 Nhập thư mục lưu file MP3:
   (Nhấn Enter để dùng thư mục 'downloads')

Thư mục: [Nhập tên hoặc Enter]

💾 Bạn có muốn giữ cả file gốc (webm/m4a) không?
   (Mặc định chỉ giữ MP3, xóa file gốc để tiết kiệm dung lượng)

Giữ file gốc? (y/N): [y hoặc n]
```

**Ưu điểm:**
- ✅ Dễ dàng, không cần nhớ cú pháp
- ✅ Có hướng dẫn chi tiết từng bước
- ✅ Phù hợp cho người mới sử dụng

---

### ⚡ Chế độ 2: Command Line (Nhanh cho người có kinh nghiệm)

Truyền URL trực tiếp qua tham số:

**Cú pháp:**
```bash
python download_youtube_mp3.py <PLAYLIST_URL> [OUTPUT_DIR] [--keep] [--threads N]
```

**Tham số:**
- `<PLAYLIST_URL>`: URL của playlist hoặc video YouTube (bắt buộc)
- `[OUTPUT_DIR]`: Thư mục lưu file (mặc định: `downloads`)
- `[--keep]`: Giữ cả file gốc (webm/m4a) ngoài MP3
- `[--threads N]` hoặc `[-t N]`: Số luồng song song (5-20, mặc định: 10)

**Ví dụ:**

```bash
# 1. Tải playlist vào thư mục "downloads" (mặc định)
python download_youtube_mp3.py "https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxx"

# 2. Tải vào thư mục tùy chỉnh "my_music"
python download_youtube_mp3.py "https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxx" my_music

# 3. Giữ cả file gốc và MP3
python download_youtube_mp3.py "https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxx" downloads --keep

# 4. Sử dụng 15 luồng để tải nhanh hơn (KHUYẾN NGHỊ!)
python download_youtube_mp3.py "https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxx" downloads --threads 15

# 5. Tải video đơn lẻ với tốc độ tối đa
python download_youtube_mp3.py "https://www.youtube.com/watch?v=xxxxxxxxxx" -t 15
```

**Ưu điểm:**
- ⚡ Nhanh, không cần tương tác
- ⚡ Dễ tạo script tự động
- ⚡ Dễ chạy lại lệnh cũ (lịch sử terminal)
- 🚀 **Tải và convert song song** - Nhanh gấp nhiều lần!

### 📂 File được lưu ngay khi convert xong!

Mỗi khi một bài hát được tải và convert xong MP3, file sẽ **xuất hiện ngay lập tức** trong thư mục bạn chọn:

```
✅ [1] Hoàn tất: 1 - Tên bài hát.mp3
   📂 Đã lưu: D:\Tool Trick Nha Lam\DownloadYoutubeMp3\downloads\1 - Tên bài hát.mp3
✅ [2] Hoàn tất: 2 - Tên bài hát.mp3
   📂 Đã lưu: D:\Tool Trick Nha Lam\DownloadYoutubeMp3\downloads\2 - Tên bài hát.mp3
```

Bạn có thể **mở folder và nghe ngay** trong khi tool vẫn đang tải các bài tiếp theo!

---

### ⚡ Tối ưu tốc độ với 2-Pipeline Architecture

Tool sử dụng **kiến trúc 2 pipeline** để tải và convert ĐỒNG THỜI!

#### So sánh tốc độ:

| Chế độ | Playlist 96 bài | Tốc độ |
|--------|----------------|--------|
| **1 luồng** (cũ) | ~8-12 giờ | 1x |
| **10 luồng** (mặc định) | ~1-2 giờ | 5-8x nhanh hơn 🚀 |
| **15 luồng** (khuyến nghị) | ~40-80 phút | 8-12x nhanh hơn 🔥 |
| **20 luồng** (max) | ~30-60 phút | 10-15x nhanh hơn ⚡ |

#### Kiến trúc 2-Pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│ PIPELINE 1: DOWNLOAD (1 luồng, liên tục)                   │
│                                                              │
│  YouTube → Tải video 1 → Tải video 2 → Tải video 3 → ...   │
│                 ↓              ↓              ↓              │
│             [Queue] ──────────────────────────────────────┐ │
└───────────────────────────────────────────────────────────┼─┘
                                                            │
┌───────────────────────────────────────────────────────────┼─┐
│ PIPELINE 2: CONVERT (10-20 luồng, song song)             │ │
│                                                            ↓ │
│  Thread 1: Convert video 1 → MP3 ────────────────────────→ │
│  Thread 2: Convert video 2 → MP3 ────────────────────────→ │
│  Thread 3: Convert video 3 → MP3 ────────────────────────→ │
│  ...                                                         │
│  Thread N: Convert video N → MP3 ────────────────────────→ │
└─────────────────────────────────────────────────────────────┘
```

**Ưu điểm:**
- ✅ **Download liên tục** - Không chờ convert xong mới tải tiếp
- ✅ **Convert song song** - 10-20 file cùng lúc
- ✅ **Tối ưu tài nguyên** - Download nhẹ, Convert nặng được phân tách
- ✅ **Không bị blocking** - 2 pipeline độc lập hoàn toàn

**Cách hoạt động:**

**Trước (1 luồng, tuần tự):**
```
Tải video 1 → Convert MP3 1 → Tải video 2 → Convert MP3 2 → ...
❌ Convert chậm → Blocking download → Mất thời gian!
```

**Bây giờ (2-Pipeline, song song):**
```
Pipeline 1: Tải 1 → Tải 2 → Tải 3 → Tải 4 → ... (không dừng!)
Pipeline 2: Convert 1, 2, 3 ... 10 cùng lúc (10-20 thread)
✅ Tải và convert ĐỒNG THỜI → Cực nhanh!
```

#### Lựa chọn số luồng:

- **5 luồng**: Máy yếu, RAM < 4GB
- **10 luồng**: Mặc định, cân bằng tốc độ và tài nguyên
- **15 luồng**: Khuyến nghị cho máy trung bình (RAM 8GB+)
- **20 luồng**: Máy mạnh (RAM 16GB+, CPU 8+ cores)

#### Lưu ý:

- ✅ Càng nhiều luồng = càng nhanh
- ⚠️ Nhưng tốn nhiều RAM và CPU hơn
- ⚠️ Nếu máy lag → Giảm số luồng xuống
- ✅ Tool tự động giới hạn 5-20 luồng để an toàn

---

### 🛑 Dừng giữa chừng:

Bạn có thể nhấn **Ctrl+C** bất kỳ lúc nào để dừng tải. Tool sẽ hiển thị:
- Số bài hát đã tải thành công
- Số video bị lỗi (nếu có)
- Đường dẫn thư mục chứa file MP3

Các file đã tải sẽ được giữ lại và bạn có thể tiếp tục tải sau!

---

### 🔄 Tính năng Resume/Continue (TỰ ĐỘNG!)

Tool **tự động phát hiện** file đã tải và bỏ qua chúng! Bạn không cần làm gì cả.

#### Kịch bản 1: Tải bị dừng giữa chừng

```bash
# Lần 1: Tải được 20/96 bài, nhấn Ctrl+C
python download_youtube_mp3.py "PLAYLIST_URL"
# Đã tải: 20 bài

# Lần 2: Chạy lại lệnh y hệt
python download_youtube_mp3.py "PLAYLIST_URL"
# → Tool tự động bỏ qua 20 bài đã có
# → Chỉ tải 76 bài còn lại!
```

#### Kịch bản 2: Playlist có thêm video mới

```bash
# Lần 1: Tải hết 96 bài
python download_youtube_mp3.py "PLAYLIST_URL"

# Sau 1 tuần, playlist có thêm 10 bài mới (tổng 106 bài)
python download_youtube_mp3.py "PLAYLIST_URL"
# → Tool tự động bỏ qua 96 bài cũ
# → Chỉ tải 10 bài mới!
```

#### Hiển thị khi có file đã tải:

```
📁 Thư mục lưu file: D:\...\downloads
📋 Tìm thấy 20 file MP3 đã có trong thư mục
   → Sẽ tự động bỏ qua các file đã tải!

[Downloading playlist: skipping downloaded items...]
⏭ Bỏ qua: 01 - Bài hát 1.mp3 (đã có)
⏭ Bỏ qua: 02 - Bài hát 2.mp3 (đã có)
...
⏭ Bỏ qua: 20 - Bài hát 20.mp3 (đã có)
⬇ Tải: 21 - Bài hát 21.mp3 [Mới tải]

✓ Hoàn tất!
✓ Tải mới lần này: 76 bài hát
⏭ Đã có sẵn (bỏ qua): 20 bài
📊 Tổng cộng trong thư mục: 96 file MP3
```

#### Cơ chế hoạt động:

Tool tạo file ẩn `.download_archive.txt` trong thư mục output để tracking:
```
youtube d9jdiiIfZEk
youtube nuGz5XOlHmc
youtube seHfSWxvWqQ
...
```

**Lưu ý:**
- ⚠️ **KHÔNG XÓA** file `.download_archive.txt` nếu muốn tiếp tục resume
- ✅ Nếu muốn tải lại từ đầu → Xóa toàn bộ thư mục output
- ✅ File này rất nhỏ (vài KB) và an toàn

## 📁 Cấu trúc file

```
DownloadYoutubeMp3/
├── download_youtube_mp3.py    # File chính
├── requirements.txt           # Dependencies
├── README.md                  # Hướng dẫn
├── TROUBLESHOOTING.md         # Xử lý lỗi chi tiết
├── FIX_DISK_FULL.md          # Xử lý lỗi hết dung lượng ổ đĩa
├── clean_temp_files.bat       # Script xóa file tạm (.part)
└── downloads/                 # Thư mục chứa MP3 (tự động tạo)
    ├── .download_archive.txt  # File tracking (ẩn, tự động tạo)
    ├── 1 - Tên bài hát 1.mp3
    ├── 2 - Tên bài hát 2.mp3
    └── ...
```

## 🎨 Định dạng tên file

File MP3 được đặt tên theo format:
```
<STT trong playlist> - <Tên video>.mp3
```

Ví dụ:
```
1 - Shape of You - Ed Sheeran.mp3
2 - Blinding Lights - The Weeknd.mp3
```

## ⚙️ Tùy chỉnh

### Tham số dòng lệnh:

#### `--keep` - Giữ file gốc

Mặc định, tool chỉ giữ file MP3 và xóa file gốc (webm/m4a) sau khi convert. Nếu bạn muốn giữ cả hai:

```bash
python download_youtube_mp3.py <URL> downloads --keep
```

Kết quả:
```
downloads/
├── 1 - Tên bài hát.mp3     ← File MP3 đã convert
├── 1 - Tên bài hát.webm    ← File gốc (giữ lại với --keep)
├── 2 - Tên bài hát.mp3
└── 2 - Tên bài hát.webm
```

**Lưu ý:** Giữ file gốc sẽ tốn gấp đôi dung lượng ổ cứng!

### Chỉnh sửa code:

Bạn có thể chỉnh sửa các tham số trong file `download_youtube_mp3.py`:

- **Chất lượng MP3**: Thay đổi `preferredquality` (mặc định: 192)
  ```python
  'preferredquality': '320',  # Chất lượng cao hơn (320kbps)
  'preferredquality': '128',  # Chất lượng thấp hơn (tiết kiệm dung lượng)
  ```

- **Format tên file**: Thay đổi `outtmpl`
  ```python
  'outtmpl': '%(title)s.%(ext)s',  # Không có số thứ tự
  'outtmpl': '%(artist)s - %(title)s.%(ext)s',  # Thêm tên nghệ sĩ
  ```

## 🐛 Xử lý lỗi

### Các cảnh báo thường gặp:

#### ⚠️ WARNING: Incomplete data received
- **Không nghiêm trọng!** Tool vẫn tải bình thường
- Nguyên nhân: Kết nối mạng, rate limit, hoặc playlist lớn
- Giải pháp: Tool đã tự động retry 5 lần

#### ⚠️ WARNING: nsig extraction failed
- **Tool vẫn tải được**, chỉ chậm hơn (100-500KB/s thay vì tốc độ tối đa)
- Nguyên nhân: YouTube thay đổi thuật toán chống download
- Giải pháp: Cập nhật yt-dlp: `pip install --upgrade yt-dlp`

### Lỗi nghiêm trọng:

#### ❌ ERROR: No space left on device
- **Ổ CỨNG ĐÃ HẾT DUNG LƯỢNG!**
- Nguyên nhân: File video (~200MB/file) lớn hơn dung lượng trống
- **Giải pháp:**
  1. **Xóa file tạm (.part):** Chạy tool sẽ tự động xóa, hoặc dùng `clean_temp_files.bat`
  2. **Chuyển sang ổ khác:** `python download_youtube_mp3.py URL "C:\Music"`
  3. **Dọn dẹp ổ đĩa:** Disk Cleanup hoặc xóa file không cần
- 💡 Tool giờ **TỰ ĐỘNG kiểm tra** dung lượng và cảnh báo trước!
- 📖 Xem thêm: [FIX_DISK_FULL.md](FIX_DISK_FULL.md)

#### ❌ ERROR: HTTP Error 403: Forbidden
- **Lỗi nghiêm trọng nhất!** Không tải được gì cả
- Nguyên nhân: yt-dlp phiên bản CŨ
- **Giải pháp:** `pip install --upgrade yt-dlp` (BẮT BUỘC!)
- Tool giờ sẽ tự động kiểm tra và cảnh báo nếu phiên bản cũ

#### ❌ ERROR: FFmpeg not found
- Đảm bảo FFmpeg đã được cài đặt và thêm vào PATH
- Kiểm tra: `ffmpeg -version`

#### ❌ ERROR: Unable to download (HTTP 429)
- Bị rate limit (tải quá nhiều)
- Chờ 1-2 giờ rồi thử lại hoặc dùng VPN

### 📖 Xem thêm:
Xem file [TROUBLESHOOTING.md](TROUBLESHOOTING.md) để biết chi tiết về tất cả các lỗi và cách khắc phục!

## 📝 Lưu ý

- Tool tuân thủ Terms of Service của YouTube
- Chỉ nên tải nội dung bạn có quyền tải xuống
- Không sử dụng cho mục đích thương mại
- Tốc độ tải phụ thuộc vào kết nối internet

## 🔄 Cập nhật

Để cập nhật tool lên phiên bản mới nhất:

```bash
pip install --upgrade yt-dlp
```

## 📜 License

MIT License - Sử dụng tự do cho mục đích cá nhân.

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Hãy tạo issue hoặc pull request.

## 📧 Liên hệ

Nếu có vấn đề hoặc câu hỏi, vui lòng tạo issue trên GitHub.

---

**Chúc bạn sử dụng vui vẻ! 🎵**

