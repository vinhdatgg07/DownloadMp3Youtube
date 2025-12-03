#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool tải video YouTube từ playlist dưới dạng MP3
"""

import os
import sys
from pathlib import Path
import yt_dlp
from colorama import init, Fore, Style
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import queue
import subprocess
import shutil
import platform

# Khởi tạo colorama cho Windows
init(autoreset=True)


def close_browser(browser_name):
    """
    Đóng trình duyệt đang chạy để giải phóng cookies database
    
    Args:
        browser_name (str): Tên trình duyệt ('chrome', 'edge', 'firefox', etc.)
    
    Returns:
        bool: True nếu đóng thành công, False nếu không
    """
    try:
        system = platform.system()
        
        if system == 'Windows':
            process_names = {
                'chrome': 'chrome.exe',
                'edge': 'msedge.exe',
                'firefox': 'firefox.exe',
                'brave': 'brave.exe',
                'opera': 'opera.exe',
            }
            
            exe_name = process_names.get(browser_name.lower())
            if not exe_name:
                return False
            
            # Đóng tiến trình
            cmd = f'taskkill /F /IM {exe_name} /T 2>nul'
            result = subprocess.run(cmd, shell=True, capture_output=True)
            
            return result.returncode == 0
        
        # Chưa hỗ trợ macOS/Linux
        return False
        
    except Exception:
        return False


def check_ytdlp_version():
    """Kiểm tra phiên bản yt-dlp và cảnh báo nếu cũ"""
    try:
        version = yt_dlp.version.__version__
        # Parse version (format: YYYY.MM.DD)
        year, month, day = map(int, version.split('.'))
        version_date = datetime(year, month, day)
        current_date = datetime.now()
        
        # Cảnh báo nếu phiên bản cũ hơn 30 ngày
        days_old = (current_date - version_date).days
        
        if days_old > 30:
            print(f"{Fore.YELLOW}⚠ Cảnh báo: yt-dlp phiên bản {version} đã cũ ({days_old} ngày)")
            print(f"{Fore.YELLOW}  YouTube thay đổi liên tục, có thể gặp lỗi HTTP 403 hoặc nsig extraction")
            print(f"{Fore.CYAN}  Khuyến nghị cập nhật: {Style.BRIGHT}pip install --upgrade yt-dlp")
            print()
        else:
            print(f"{Fore.GREEN}✓ yt-dlp phiên bản {version} (mới nhất)")
            print()
    except Exception:
        # Nếu không check được thì thôi, không làm gián đoạn chương trình
        pass


def check_disk_space(path, required_gb=2.0):
    """
    Kiểm tra dung lượng ổ đĩa còn trống
    
    Args:
        path (Path): Đường dẫn thư mục cần kiểm tra
        required_gb (float): Dung lượng tối thiểu cần thiết (GB)
    
    Returns:
        bool: True nếu đủ dung lượng, False nếu không đủ
    """
    try:
        # Lấy thông tin dung lượng ổ đĩa
        stat = shutil.disk_usage(path)
        free_gb = stat.free / (1024 ** 3)  # Convert bytes to GB
        total_gb = stat.total / (1024 ** 3)
        used_gb = stat.used / (1024 ** 3)
        
        print(f"{Fore.CYAN}💾 Thông tin ổ đĩa:")
        print(f"{Fore.CYAN}   • Tổng: {total_gb:.1f} GB")
        print(f"{Fore.CYAN}   • Đã dùng: {used_gb:.1f} GB")
        print(f"{Fore.CYAN}   • Còn trống: {Style.BRIGHT}{free_gb:.1f} GB")
        
        if free_gb < required_gb:
            print(f"\n{Fore.RED}⚠️  CẢNH BÁO: Dung lượng ổ đĩa SẮP HẾT!")
            print(f"{Fore.YELLOW}   Cần tối thiểu: {required_gb:.1f} GB")
            print(f"{Fore.YELLOW}   Còn lại: {free_gb:.1f} GB")
            print(f"\n{Fore.CYAN}💡 Giải pháp:")
            print(f"{Fore.CYAN}   1. Dọn dẹp file không cần thiết")
            print(f"{Fore.CYAN}   2. Chuyển thư mục sang ổ đĩa khác")
            print(f"{Fore.CYAN}   3. Xóa file webm/m4a cũ (nếu có)")
            
            # Hỏi có muốn tiếp tục không
            choice = input(f"\n{Fore.YELLOW}Bạn có muốn tiếp tục? (y/N): {Style.BRIGHT}").strip().lower()
            if choice not in ['y', 'yes', 'có']:
                return False
        
        print()
        return True
        
    except Exception as e:
        print(f"{Fore.YELLOW}⚠️  Không thể kiểm tra dung lượng ổ đĩa: {e}")
        print()
        return True  # Cho phép tiếp tục nếu không check được


class YouTubePlaylistDownloader:
    """Class để tải playlist YouTube và chuyển đổi sang MP3"""
    
    def __init__(self, output_dir="downloads", keep_original=False, max_workers=10, cookies_file=None):
        """
        Khởi tạo downloader với 2-pipeline architecture
        
        Args:
            output_dir (str): Thư mục lưu file MP3 (mặc định: 'downloads')
            keep_original (bool): Giữ file gốc (webm/m4a) ngoài MP3 (mặc định: False)
            max_workers (int): Số thread convert song song (mặc định: 10)
            cookies_file (str): Đường dẫn file cookies (tùy chọn)
        """
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(exist_ok=True)
        self.keep_original = keep_original
        self.max_workers = max_workers
        self.cookies_file = cookies_file
        
        # Counters (thread-safe)
        self.downloaded_count = 0  # Số file đã tải xong (chưa convert)
        self.converted_count = 0   # Số file đã convert xong MP3
        self.failed_count = 0
        self.lock = threading.Lock()
        
        # Queue để truyền file từ download → convert
        self.convert_queue = queue.Queue(maxsize=max_workers * 2)  # Buffer
        self.download_archive = self.output_dir / '.download_archive.txt'
        
        # Flags
        self.stop_flag = threading.Event()  # Signal để dừng threads
        self.download_finished = threading.Event()  # Signal download xong
        
        # Hiển thị thông tin
        print(f"{Fore.GREEN}📁 Thư mục lưu file: {Style.BRIGHT}{self.output_dir}")
        if self.keep_original:
            print(f"{Fore.YELLOW}💾 Sẽ giữ cả file gốc và MP3")
        else:
            print(f"{Fore.CYAN}💾 Chỉ giữ file MP3 (xóa file gốc sau khi convert)")
        
        print(f"{Fore.MAGENTA}⚡ Pipeline 2 luồng:")
        print(f"{Fore.CYAN}   • Luồng tải: Liên tục tải video từ YouTube")
        print(f"{Fore.CYAN}   • Luồng convert: {Style.BRIGHT}{max_workers} {Fore.CYAN}thread xử lý MP3 song song")
        print(f"{Fore.GREEN}   → Tải và convert ĐỒNG THỜI, nhanh gấp nhiều lần!")
        
        # Kiểm tra file đã tải
        existing_mp3 = list(self.output_dir.glob("*.mp3"))
        if existing_mp3:
            print(f"{Fore.YELLOW}📋 Tìm thấy {len(existing_mp3)} file MP3 đã có")
            print(f"{Fore.CYAN}   → Sẽ tự động bỏ qua!")
        
        # Dọn dẹp file tạm (.part) từ lần tải trước
        part_files = list(self.output_dir.glob("*.part"))
        if part_files:
            print(f"{Fore.YELLOW}🧹 Tìm thấy {len(part_files)} file tạm (.part) từ lần tải trước")
            cleaned = 0
            freed_mb = 0
            for part_file in part_files:
                try:
                    size_mb = part_file.stat().st_size / (1024 * 1024)
                    part_file.unlink()
                    cleaned += 1
                    freed_mb += size_mb
                except:
                    pass
            if cleaned > 0:
                print(f"{Fore.GREEN}   ✓ Đã xóa {cleaned} file tạm, giải phóng {freed_mb:.1f} MB!")
        
        print()
        
        # Kiểm tra dung lượng ổ đĩa
        if not check_disk_space(self.output_dir, required_gb=2.0):
            print(f"{Fore.RED}❌ Hủy tải do không đủ dung lượng!")
            sys.exit(1)
        
    def convert_to_mp3(self, audio_file):
        """
        Convert file audio sang MP3 bằng FFmpeg
        
        Args:
            audio_file (Path): Đường dẫn file audio gốc
        """
        try:
            mp3_file = audio_file.with_suffix('.mp3')
            
            # Nếu MP3 đã tồn tại, skip
            if mp3_file.exists():
                if not self.keep_original:
                    audio_file.unlink(missing_ok=True)
                return True
            
            # Convert bằng FFmpeg
            cmd = [
                'ffmpeg',
                '-loglevel', 'error',  # Chỉ hiện lỗi
                '-i', str(audio_file),
                '-vn',  # Không có video
                '-ar', '44100',  # Sample rate
                '-ac', '2',  # Stereo
                '-b:a', '192k',  # Bitrate 192k
                '-y',  # Overwrite
                str(mp3_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and mp3_file.exists():
                # Convert thành công
                with self.lock:
                    self.converted_count += 1
                    count = self.converted_count
                
                print(f"{Fore.GREEN}✅ [{count}] Hoàn tất: {mp3_file.name}")
                print(f"{Fore.CYAN}   📂 Đã lưu: {mp3_file}")
                
                # Xóa file gốc nếu không giữ
                if not self.keep_original:
                    audio_file.unlink(missing_ok=True)
                
                return True
            else:
                raise Exception(f"FFmpeg error: {result.stderr}")
                
        except Exception as e:
            with self.lock:
                self.failed_count += 1
            print(f"{Fore.RED}✗ Lỗi convert {audio_file.name}: {str(e)}")
            return False
    
    def convert_worker(self):
        """
        Worker thread để convert MP3 từ queue
        """
        while not self.stop_flag.is_set():
            try:
                # Lấy file từ queue với timeout
                audio_file = self.convert_queue.get(timeout=1)
                
                if audio_file is None:  # Poison pill
                    break
                
                # Convert sang MP3
                self.convert_to_mp3(audio_file)
                
                self.convert_queue.task_done()
                
            except queue.Empty:
                # Nếu download đã xong và queue rỗng → thoát
                if self.download_finished.is_set():
                    break
                continue
            except Exception as e:
                print(f"{Fore.RED}✗ Lỗi worker: {str(e)}")
    
    def _check_cookies_file(self):
        """
        Kiểm tra xem có file cookies không
        
        Returns:
            bool: True nếu tìm thấy file cookies hợp lệ
        """
        # Danh sách file cookies có thể có
        possible_files = [
            'youtube_cookies.txt',
            'cookies.txt',
            'youtube.txt',
        ]
        
        # Nếu user chỉ định file cookies cụ thể
        if self.cookies_file:
            possible_files.insert(0, self.cookies_file)
        
        for cookie_file in possible_files:
            cookie_path = Path(cookie_file)
            
            # Kiểm tra file tồn tại
            if cookie_path.exists() and cookie_path.is_file():
                # Kiểm tra file không rỗng
                if cookie_path.stat().st_size > 0:
                    print(f"{Fore.GREEN}🍪 Tìm thấy file cookies: {Style.BRIGHT}{cookie_file}")
                    print(f"{Fore.CYAN}   → Sẽ sử dụng cookies từ file!")
                    print(f"{Fore.GREEN}   ✓ Không cần lấy cookies từ trình duyệt")
                    self.cookies_file = str(cookie_path)
                    return True
        
        # Không tìm thấy file cookies
        return False
    
    def _get_browser_cookies(self):
        """
        Tự động phát hiện và lấy cookies từ các trình duyệt
        
        Returns:
            tuple hoặc None: ('browser_name',) nếu tìm thấy, None nếu không
        """
        # Edge trước vì ít bị lỗi DPAPI hơn Chrome
        browsers = ['edge', 'firefox', 'chrome', 'brave', 'opera']
        
        print(f"{Fore.CYAN}🍪 Đang tìm cookies từ trình duyệt...")
        
        chrome_locked = False
        
        for browser in browsers:
            try:
                # Test THỰC SỰ bằng cách extract info từ một video YouTube test
                test_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'cookiesfrombrowser': (browser,),
                    'extract_flat': False,
                }
                
                # Test với một video ngắn public
                test_url = 'https://www.youtube.com/watch?v=jNQXAC9IVRw'  # Me at the zoo - video đầu tiên của YouTube
                
                with yt_dlp.YoutubeDL(test_opts) as ydl:
                    # Thử extract info thực sự (không download)
                    ydl.extract_info(test_url, download=False)
                
                print(f"{Fore.GREEN}   ✓ Cookies từ {browser.title()} hoạt động!")
                return (browser,)
            except Exception as e:
                # Hiển thị lỗi để người dùng biết
                error_msg = str(e).lower()
                
                if 'dpapi' in error_msg or 'decrypt' in error_msg:
                    print(f"{Fore.YELLOW}   ✗ {browser.title()}: Lỗi giải mã cookies (DPAPI)")
                elif 'could not copy' in error_msg or 'database' in error_msg:
                    print(f"{Fore.YELLOW}   ✗ {browser.title()}: Đang mở (file cookies bị khóa)")
                    
                    # Hỏi có muốn tự động đóng không
                    print(f"{Fore.CYAN}      💡 Tự động đóng {browser.title()} và thử lại?")
                    choice = input(f"{Fore.WHITE}      Đóng {browser.title()}? (Y/n): {Style.BRIGHT}").strip().lower()
                    
                    if choice in ['', 'y', 'yes', 'có']:
                        print(f"{Fore.CYAN}      → Đang đóng {browser.title()}...")
                        if close_browser(browser):
                            print(f"{Fore.GREEN}      ✓ Đã đóng {browser.title()}!")
                            print(f"{Fore.CYAN}      → Thử lại...")
                            
                            # Thử lại sau khi đóng
                            try:
                                time.sleep(1)  # Chờ file unlock
                                with yt_dlp.YoutubeDL(test_opts) as ydl:
                                    ydl.extract_info(test_url, download=False)
                                print(f"{Fore.GREEN}   ✓ Cookies từ {browser.title()} hoạt động!")
                                return (browser,)
                            except Exception as retry_error:
                                retry_msg = str(retry_error).lower()
                                if 'could not copy' in retry_msg:
                                    print(f"{Fore.YELLOW}      ✗ Vẫn bị khóa, thử trình duyệt khác...")
                                else:
                                    print(f"{Fore.YELLOW}      ✗ Vẫn lỗi, thử trình duyệt khác...")
                        else:
                            print(f"{Fore.YELLOW}      ✗ Không thể đóng tự động")
                    
                    if browser == 'chrome':
                        chrome_locked = True
                else:
                    # Lỗi khác, không hiển thị
                    pass
                continue
        
        print(f"{Fore.YELLOW}   ⚠ Không tìm thấy cookies hợp lệ")
        print(f"{Fore.CYAN}   💡 Giải pháp:")
        
        if chrome_locked:
            print(f"{Fore.CYAN}      1. ĐÓNG TẤT CẢ TRÌNH DUYỆT CHROMIUM (Chrome, Edge, Brave)")
            print(f"{Fore.CYAN}      2. Hoặc chạy: {Style.BRIGHT}dong_chrome_va_chay.bat")
            print(f"{Fore.CYAN}      3. Hoặc dùng Firefox (không bị lỗi này)")
        else:
            print(f"{Fore.CYAN}      1. Đăng nhập YouTube trên Edge/Firefox")
            print(f"{Fore.CYAN}      2. ĐÓNG trình duyệt trước khi chạy tool")
            print(f"{Fore.CYAN}      3. Hoặc thử không dùng cookies (có thể bị giới hạn)")
        
        return None
    
    def download_playlist(self, playlist_url):
        """
        Tải playlist YouTube với 2-pipeline architecture
        
        Args:
            playlist_url (str): URL của playlist YouTube
        """
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}🎵 Tool Tải MP3 từ YouTube Playlist 🎵")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        # QUAN TRỌNG: Ưu tiên KHÔNG dùng cookies vì iOS/Android client tốt hơn!
        print(f"{Fore.YELLOW}💡 Lưu ý: YouTube đã thay đổi, client Android/iOS (không cookies) ổn định hơn!")
        print(f"{Fore.CYAN}   Tool sẽ dùng Android client (không cần cookies, không cần Node.js)")
        print()
        
        # Không dùng cookies nữa để tránh xung đột
        cookies_from_file = False
        browser_cookies = None
        
        # Cấu hình yt-dlp - CHỈ TẢI, KHÔNG CONVERT
        ydl_opts = {
            # Android client trả về format opus/m4a/webm
            'format': 'bestaudio/best',
            'outtmpl': str(self.output_dir / '%(playlist_index)s - %(title)s.%(ext)s'),
            'download_archive': str(self.download_archive),
            'ignoreerrors': True,
            'no_warnings': False,
            'quiet': True,  # Ít log hơn để dễ đọc
            'extract_flat': False,
            'progress_hooks': [self._progress_hook],
            'retries': 5,
            'fragment_retries': 5,
            'skip_unavailable_fragments': True,
            'extractor_retries': 5,
            'file_access_retries': 3,
            'throttledratelimit': 100000,
            
            # ✅ FIX: Dùng Android client - Ổn định nhất, không cần cookies, không cần Node.js
            # Android client trả về format m4a/webm sẵn, không bị SABR streaming
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],  # Chỉ Android, đơn giản nhất
                }
            },
            
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
        }
        
        # KHÔNG dùng cookies để tương thích với Android client
        print(f"{Fore.GREEN}✓ Sử dụng Android client (không cần cookies)")
        
        try:
            print(f"{Fore.YELLOW}📥 Khởi động 2-Pipeline...\n")
            print(f"{Fore.CYAN}💡 Nhấn Ctrl+C để dừng bất kỳ lúc nào\n")
            
            # Khởi động thread pool convert
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Start convert workers
                convert_futures = [executor.submit(self.convert_worker) for _ in range(self.max_workers)]
                
                # Bắt đầu download trong main thread
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([playlist_url])
                
                # Download xong, signal cho workers
                self.download_finished.set()
                
                # Chờ queue xử lý hết
                print(f"\n{Fore.YELLOW}⏳ Đang chờ convert các file còn lại...")
                self.convert_queue.join()
                
                # Gửi poison pills để dừng workers
                for _ in range(self.max_workers):
                    self.convert_queue.put(None)
                
                # Chờ tất cả workers kết thúc
                for future in as_completed(convert_futures):
                    future.result()
            
            # Tính toán kết quả
            total_mp3 = len(list(self.output_dir.glob("*.mp3")))
            
            print(f"\n{Fore.GREEN}{'='*60}")
            print(f"{Fore.GREEN}✓ Hoàn tất!")
            print(f"{Fore.GREEN}✓ Convert xong: {Style.BRIGHT}{self.converted_count} {Fore.GREEN}bài hát")
            if total_mp3 > self.converted_count:
                skipped = total_mp3 - self.converted_count
                print(f"{Fore.CYAN}⏭ Đã có sẵn (bỏ qua): {Style.BRIGHT}{skipped} {Fore.CYAN}bài")
            print(f"{Fore.GREEN}📊 Tổng cộng: {Style.BRIGHT}{total_mp3} {Fore.GREEN}file MP3")
            if self.failed_count > 0:
                print(f"{Fore.YELLOW}⚠ Bỏ qua (lỗi): {Style.BRIGHT}{self.failed_count} {Fore.YELLOW}video")
            print(f"{Fore.GREEN}✓ Lưu tại: {Style.BRIGHT}{self.output_dir.absolute()}")
            print(f"{Fore.GREEN}{'='*60}")
                    
        except KeyboardInterrupt:
            self.stop_flag.set()
            self.download_finished.set()
            
            total_mp3 = len(list(self.output_dir.glob("*.mp3")))
            
            print(f"\n\n{Fore.YELLOW}{'='*60}")
            print(f"{Fore.YELLOW}⚠ Đã dừng bởi người dùng!")
            print(f"{Fore.GREEN}✓ Convert xong: {Style.BRIGHT}{self.converted_count} {Fore.GREEN}bài hát")
            print(f"{Fore.GREEN}📊 Tổng cộng: {Style.BRIGHT}{total_mp3} {Fore.GREEN}file MP3")
            print(f"{Fore.CYAN}💡 Chạy lại để tiếp tục tải các file còn lại!")
            print(f"{Fore.YELLOW}{'='*60}")
            sys.exit(0)
        except Exception as e:
            self.stop_flag.set()
            print(f"\n{Fore.RED}❌ Lỗi: {str(e)}")
            print(f"{Fore.YELLOW}Convert được: {self.converted_count} bài hát")
            sys.exit(1)
    
    def _progress_hook(self, d):
        """Hook để hiển thị tiến trình tải và đẩy vào convert queue"""
        if d['status'] == 'downloading':
            # Skip progress bar để output sạch
            pass
        elif d['status'] == 'finished':
            # File tải xong, đẩy vào queue để convert
            audio_file = Path(d['filename'])
            filename = audio_file.name
            
            with self.lock:
                self.downloaded_count += 1
                count = self.downloaded_count
            
            print(f"{Fore.CYAN}⬇ [{count}] Đã tải: {filename}")
            
            # Kiểm tra xem đã có MP3 chưa
            mp3_file = audio_file.with_suffix('.mp3')
            if not mp3_file.exists():
                # Đẩy vào queue để convert
                print(f"{Fore.YELLOW}   → Thêm vào hàng đợi convert...")
                self.convert_queue.put(audio_file)
            else:
                print(f"{Fore.GREEN}   ✓ MP3 đã tồn tại, bỏ qua convert")
                # Xóa file audio gốc nếu không giữ
                if not self.keep_original:
                    audio_file.unlink(missing_ok=True)
                    
        elif d['status'] == 'error':
            with self.lock:
                self.failed_count += 1
            filename = d.get('filename', 'Unknown')
            print(f"{Fore.RED}✗ Lỗi tải: {filename}")


def main():
    """Hàm chính"""
    try:
        print(f"{Fore.MAGENTA}{Style.BRIGHT}")
        print("""
    ██╗   ██╗████████╗    ███╗   ███╗██████╗ ██████╗ 
    ╚██╗ ██╔╝╚══██╔══╝    ████╗ ████║██╔══██╗╚════██╗
     ╚████╔╝    ██║       ██╔████╔██║██████╔╝ █████╔╝
      ╚██╔╝     ██║       ██║╚██╔╝██║██╔═══╝  ╚═══██╗
       ██║      ██║       ██║ ╚═╝ ██║██║     ██████╔╝
       ╚═╝      ╚═╝       ╚═╝     ╚═╝╚═╝     ╚═════╝ 
        """)
        print(f"{Style.RESET_ALL}")
        
        # Kiểm tra phiên bản yt-dlp
        check_ytdlp_version()
        
        # Kiểm tra xem có arguments không
        if len(sys.argv) >= 2:
            # Chế độ command line (cũ)
            playlist_url = sys.argv[1]
            output_dir = "downloads"
            keep_original = False
            max_workers = 10
            
            # Kiểm tra các tham số
            i = 2
            while i < len(sys.argv):
                arg = sys.argv[i]
                if arg == "--keep":
                    keep_original = True
                elif arg == "--threads" or arg == "-t":
                    # Tham số số luồng: --threads 15 hoặc -t 15
                    if i + 1 < len(sys.argv):
                        try:
                            max_workers = int(sys.argv[i + 1])
                            max_workers = max(5, min(20, max_workers))
                            i += 1  # Skip next arg
                        except:
                            pass
                elif not arg.startswith("--") and not arg.startswith("-"):
                    output_dir = arg
                i += 1
        else:
            # Chế độ interactive (mới)
            print(f"{Fore.CYAN}{'='*60}")
            print(f"{Fore.CYAN}🎵 Chào mừng đến với YouTube MP3 Downloader! 🎵")
            print(f"{Fore.CYAN}{'='*60}\n")
            
            # Hỏi URL
            print(f"{Fore.YELLOW}📝 Nhập URL playlist hoặc video YouTube:")
            print(f"{Fore.CYAN}   Ví dụ: https://www.youtube.com/playlist?list=PLxxxxxx")
            print(f"{Fore.CYAN}   Hoặc: https://www.youtube.com/watch?v=xxxxxx")
            playlist_url = input(f"\n{Fore.WHITE}URL: {Style.BRIGHT}").strip()
            
            if not playlist_url:
                print(f"{Fore.RED}❌ URL không được để trống!")
                sys.exit(1)
            
            # Hỏi thư mục lưu
            print(f"\n{Fore.YELLOW}📁 Nhập thư mục lưu file MP3:")
            print(f"{Fore.CYAN}   (Nhấn Enter để dùng thư mục 'downloads')")
            output_input = input(f"\n{Fore.WHITE}Thư mục: {Style.BRIGHT}").strip()
            output_dir = output_input if output_input else "downloads"
            
            # Hỏi có giữ file gốc không
            print(f"\n{Fore.YELLOW}💾 Bạn có muốn giữ cả file gốc (webm/m4a) không?")
            print(f"{Fore.CYAN}   (Mặc định chỉ giữ MP3, xóa file gốc để tiết kiệm dung lượng)")
            keep_input = input(f"\n{Fore.WHITE}Giữ file gốc? (y/N): {Style.BRIGHT}").strip().lower()
            keep_original = keep_input in ['y', 'yes', 'có']
            
            # Hỏi số luồng song song
            print(f"\n{Fore.YELLOW}⚡ Số luồng tải/convert song song:")
            print(f"{Fore.CYAN}   Càng nhiều = càng nhanh, nhưng tốn RAM/CPU hơn")
            print(f"{Fore.CYAN}   Khuyến nghị: 5-15 luồng (mặc định: 10)")
            workers_input = input(f"\n{Fore.WHITE}Số luồng (5-20): {Style.BRIGHT}").strip()
            try:
                max_workers = int(workers_input) if workers_input else 10
                max_workers = max(5, min(20, max_workers))  # Giới hạn 5-20
            except:
                max_workers = 10
            
            print()  # Dòng trống
        
        # Tạo downloader và bắt đầu tải
        downloader = YouTubePlaylistDownloader(output_dir, keep_original, max_workers)
        downloader.download_playlist(playlist_url)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Đã hủy bỏ!")
        sys.exit(0)
    except EOFError:
        print(f"\n{Fore.RED}Đã hủy bỏ!")
        sys.exit(0)


if __name__ == "__main__":
    main()

