from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess
import os
import sys
import tempfile
import uuid
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__)

# تنظیمات پیشرفته لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('execution.log'),
        logging.StreamHandler()
    ]
)

# تنظیمات encoding
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

def execute_js_safely(code):
    """تابع ایمن برای اجرای کد JavaScript با Node.js"""
    try:
        # ایجاد فایل موقت با نام تصادفی
        with tempfile.NamedTemporaryFile(suffix='.js', delete=False) as tmp:
            tmp.write(code.encode('utf-8'))
            tmp_path = tmp.name
        
        # اجرای کد با Node.js
        result = subprocess.run(
            ['node', tmp_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=10
        )
        
        # حذف فایل موقت
        os.unlink(tmp_path)
        
        if result.stderr:
            return {'error': result.stderr.strip()}
        return {'output': result.stdout.strip() or 'کد با موفقیت اجرا شد (بدون خروجی)'}
        
    except subprocess.TimeoutExpired:
        return {'error': 'زمان اجرای کد به پایان رسید'}
    except Exception as e:
        return {'error': f'خطای سیستم: {str(e)}'}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get('code', '')
    if not code.strip():
        return jsonify({'error': 'کد JavaScript خالی است'}), 400
    
    return jsonify(execute_js_safely(code))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)