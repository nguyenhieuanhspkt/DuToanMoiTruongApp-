import os
import sys
import subprocess

# 1. Tự động xác định đường dẫn thư mục gốc của dự án (DuToanMoiTruongApp)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Từ backend/exporters/ lùi lên 2 cấp để về thư mục gốc DuToanMoiTruongApp
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))

print(f"📁 Thư mục gốc dự án: {root_dir}")

# 2. Đường dẫn tuyệt đối đến tệp generate_f1_100pct.py cần chạy
target_script = os.path.join(root_dir, "backend", "scripts", "generate_f1_100pct.py")

if not os.path.exists(target_script):
    print(f"❌ Không tìm thấy tệp tại đường dẫn: {target_script}")
else:
    print(f"🚀 Đang tiến hành chạy tệp: {target_script}\n" + "-"*50)
    
    # 3. Tạo môi trường giả lập có chứa PYTHONPATH trỏ về thư mục gốc
    env = os.environ.copy()
    env["PYTHONPATH"] = root_dir

    # 4. Thực thi tệp script mục tiêu thông qua tiến trình con của Python
    result = subprocess.run([sys.executable, target_script], env=env)
    
    print("-" * 50)
    if result.returncode == 0:
        print("✅ Chạy tệp script thành công rực rỡ!")
    else:
        print(f"⚠️ Quá trình chạy kết thúc với mã lỗi: {result.returncode}")