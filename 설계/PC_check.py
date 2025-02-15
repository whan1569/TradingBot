import psutil
import platform
import shutil
import time
import speedtest
import GPUtil

def get_cpu_info():
    print("🔹 CPU 정보")
    print(f"  - 프로세서: {platform.processor()}")
    print(f"  - 코어 수: {psutil.cpu_count(logical=False)} (물리) / {psutil.cpu_count(logical=True)} (논리)")
    print(f"  - 사용량: {psutil.cpu_percent(interval=1)}%")

def get_ram_info():
    ram = psutil.virtual_memory()
    print("\n🔹 RAM 정보")
    print(f"  - 전체: {ram.total / (1024 ** 3):.2f} GB")
    print(f"  - 사용 중: {ram.used / (1024 ** 3):.2f} GB ({ram.percent}%)")
    print(f"  - 가용: {ram.available / (1024 ** 3):.2f} GB")

def get_gpu_info():
    gpus = GPUtil.getGPUs()
    print("\n🔹 GPU 정보")
    if not gpus:
        print("  - GPU 없음 또는 CUDA 미지원")
    for gpu in gpus:
        print(f"  - 모델: {gpu.name}")
        print(f"  - VRAM 사용량: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB ({gpu.memoryUtil * 100:.2f}%)")
        print(f"  - 온도: {gpu.temperature}°C")

def get_disk_speed():
    print("\n🔹 디스크 속도 테스트 (읽기/쓰기)")
    test_file = "disk_speed_test.tmp"
    
    # 쓰기 속도 측정
    start_time = time.time()
    with open(test_file, "wb") as f:
        f.write(b"\0" * (100 * 1024 * 1024))  # 100MB 더미 파일 생성
    write_speed = 100 / (time.time() - start_time)

    # 읽기 속도 측정
    start_time = time.time()
    with open(test_file, "rb") as f:
        f.read()
    read_speed = 100 / (time.time() - start_time)

    # 파일 삭제
    try:
        shutil.os.remove(test_file)
    except:
        pass

    print(f"  - 쓰기 속도: {write_speed:.2f} MB/s")
    print(f"  - 읽기 속도: {read_speed:.2f} MB/s")

def get_network_speed():
    print("\n🔹 네트워크 속도 테스트 (Ping / 다운로드 / 업로드)")
    st = speedtest.Speedtest()
    
    # 서버 선택
    st.get_best_server()
    
    # 다운로드 속도 측정
    download_speed = st.download() / (1024 * 1024)
    
    # 업로드 속도 측정
    upload_speed = st.upload() / (1024 * 1024)
    
    # Ping 측정
    ping = st.results.ping

    print(f"  - Ping: {ping:.2f} ms")
    print(f"  - 다운로드 속도: {download_speed:.2f} Mbps")
    print(f"  - 업로드 속도: {upload_speed:.2f} Mbps")

if __name__ == "__main__":
    print("🔍 시스템 성능 확인 중...\n")
    get_cpu_info()
    get_ram_info()
    get_gpu_info()
    get_disk_speed()
    get_network_speed()
