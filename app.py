import os
import uuid
import time
import numpy as np
import cv2
from PIL import Image
from flask import Flask, request, jsonify, send_from_directory, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
DELETE_AFTER_SECONDS = 20 * 60  # 20 minutes

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# ── Cleanup scheduler ─────────────────────────────────────────────────────────

def cleanup_old_files():
    now = time.time()
    for fname in os.listdir(UPLOAD_FOLDER):
        fpath = os.path.join(UPLOAD_FOLDER, fname)
        if os.path.isfile(fpath) and (now - os.path.getmtime(fpath)) > DELETE_AFTER_SECONDS:
            try:
                os.remove(fpath)
                print(f'[cleanup] Deleted {fname}')
            except OSError as e:
                print(f'[cleanup] Error deleting {fname}: {e}')

scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_old_files, 'interval', minutes=5)
scheduler.start()

# ── Helpers ───────────────────────────────────────────────────────────────────

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def inpaint_image(image_path, mask_path, result_path):
    """OpenCV TELEA inpainting — user-drawn mask drives removal."""
    img_pil  = Image.open(image_path).convert('RGB')
    arr_rgb  = np.array(img_pil, dtype=np.uint8)

    mask_pil = Image.open(mask_path).convert('L')
    if mask_pil.size != img_pil.size:
        mask_pil = mask_pil.resize(img_pil.size, Image.NEAREST)
    mask_arr = np.array(mask_pil, dtype=np.uint8)

    _, mask_u8 = cv2.threshold(mask_arr, 10, 255, cv2.THRESH_BINARY)
    kernel     = np.ones((5, 5), dtype=np.uint8)
    mask_u8    = cv2.dilate(mask_u8, kernel, iterations=2)

    arr_bgr       = cv2.cvtColor(arr_rgb, cv2.COLOR_RGB2BGR)
    inpainted_bgr = cv2.inpaint(arr_bgr, mask_u8, inpaintRadius=15, flags=cv2.INPAINT_TELEA)
    inpainted_rgb = cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2RGB)

    Image.fromarray(inpainted_rgb).save(result_path, 'PNG')

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html', active='home')

@app.route('/about')
def about():
    return render_template('about.html', active='about')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html', active='privacy')

@app.route('/blog')
def blog():
    return render_template('blog.html', active='blog')

@app.route('/blog/how-to-remove-watermark-from-image')
def blog_watermark():
    return render_template('blog_watermark.html', active='blog')

@app.route('/blog/remove-logo-from-image-online')
def blog_logo():
    return render_template('blog_logo.html', active='blog')

@app.route('/blog/remove-text-from-photo-free')
def blog_text():
    return render_template('blog_text.html', active='blog')

@app.route('/blog/what-is-image-inpainting-ai')
def blog_inpainting():
    return render_template('blog_inpainting.html', active='blog')

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/remove', methods=['POST'])
def remove_object():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided.'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported format. Please upload JPEG, PNG, or WebP.'}), 400

    if 'mask' not in request.files or request.files['mask'].filename == '':
        return jsonify({'error': 'Please paint over the object area first.'}), 400

    ext           = file.filename.rsplit('.', 1)[1].lower()
    uid           = uuid.uuid4().hex
    original_name = f'orig_{uid}.{ext}'
    mask_name     = f'mask_{uid}.png'
    result_name   = f'result_{uid}.png'
    original_path = os.path.join(UPLOAD_FOLDER, original_name)
    mask_path     = os.path.join(UPLOAD_FOLDER, mask_name)
    result_path   = os.path.join(UPLOAD_FOLDER, result_name)

    file.save(original_path)
    request.files['mask'].save(mask_path)

    try:
        inpaint_image(original_path, mask_path, result_path)
    except Exception as e:
        for p in [original_path, mask_path, result_path]:
            if os.path.exists(p): os.remove(p)
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

    return jsonify({
        'original': f'/uploads/{original_name}',
        'result':   f'/uploads/{result_name}',
    })


if __name__ == '__main__':
    cleanup_old_files()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
