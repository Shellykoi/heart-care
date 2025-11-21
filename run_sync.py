"""
运行数据同步脚本的包装器
"""
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    script_path = Path(__file__).parent / "src" / "backend" / "sync_all_data_to_cloud.py"
    subprocess.run([sys.executable, str(script_path)])



