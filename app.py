import os
import uuid
import time
import io
import numpy as np
import cv2
from PIL import Image, ImageFilter, ImageOps
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

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml', mimetype='application/xml')

@app.route('/ads.txt')
def ads_txt():
    return send_from_directory('static', 'ads.txt', mimetype='text/plain')

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

@app.route('/remove-background')
def bg_remover():
    return render_template('bg_remover.html', active='tools')

@app.route('/image-editor')
def image_editor():
    return render_template('image_editor.html', active='tools')

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


@app.route('/api/remove-bg', methods=['POST'])
def remove_bg():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided.'}), 400
    file = request.files['image']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported format. Use JPEG, PNG, or WebP.'}), 400

    try:
        from rembg import remove as rembg_remove
    except ImportError:
        return jsonify({'error': 'Background removal library not installed.'}), 500

    uid = uuid.uuid4().hex
    ext = file.filename.rsplit('.', 1)[1].lower()
    orig_name   = f'orig_{uid}.{ext}'
    result_name = f'bgrem_{uid}.png'
    orig_path   = os.path.join(UPLOAD_FOLDER, orig_name)
    result_path = os.path.join(UPLOAD_FOLDER, result_name)

    file.save(orig_path)
    try:
        with open(orig_path, 'rb') as f:
            output = rembg_remove(f.read())
        with open(result_path, 'wb') as f:
            f.write(output)
    except Exception as e:
        for p in [orig_path, result_path]:
            if os.path.exists(p): os.remove(p)
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

    return jsonify({'original': f'/uploads/{orig_name}', 'result': f'/uploads/{result_name}'})


@app.route('/api/edit', methods=['POST'])
def edit_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided.'}), 400
    file   = request.files['image']
    action = request.form.get('action', '')

    uid         = uuid.uuid4().hex
    result_name = f'edit_{uid}.png'
    result_path = os.path.join(UPLOAD_FOLDER, result_name)
    out_ext     = 'png'

    try:
        img = Image.open(file.stream).convert('RGBA')

        if action == 'resize':
            unit = request.form.get('unit', 'px')
            w = int(request.form.get('width', img.width))
            h = int(request.form.get('height', img.height))
            if unit == 'pct':
                w = int(img.width * w / 100)
                h = int(img.height * h / 100)
            img = img.resize((max(1, w), max(1, h)), Image.LANCZOS)

        elif action == 'crop':
            left = int(request.form.get('left', 0))
            top  = int(request.form.get('top', 0))
            w    = int(request.form.get('width', img.width))
            h    = int(request.form.get('height', img.height))
            img  = img.crop((left, top, left + w, top + h))

        elif action == 'mirror_h':
            img = ImageOps.mirror(img)

        elif action == 'mirror_v':
            img = ImageOps.flip(img)

        elif action == 'rotate_90':
            img = img.rotate(-90, expand=True)

        elif action == 'rotate_180':
            img = img.rotate(180, expand=True)

        elif action == 'rotate_270':
            img = img.rotate(90, expand=True)

        elif action == 'compress':
            quality = int(request.form.get('quality', 80))
            result_name = f'edit_{uid}.jpg'
            result_path = os.path.join(UPLOAD_FOLDER, result_name)
            out_ext = 'jpg'
            img.convert('RGB').save(result_path, 'JPEG', quality=quality, optimize=True)
            return jsonify({'result': f'/uploads/{result_name}', 'ext': out_ext})

        elif action == 'convert':
            fmt = request.form.get('format', 'jpeg').lower()
            ext_map = {'jpeg': 'jpg', 'png': 'png', 'webp': 'webp'}
            out_ext = ext_map.get(fmt, 'jpg')
            result_name = f'edit_{uid}.{out_ext}'
            result_path = os.path.join(UPLOAD_FOLDER, result_name)
            save_img = img if fmt == 'png' else img.convert('RGB')
            pil_fmt = {'jpg': 'JPEG', 'png': 'PNG', 'webp': 'WEBP'}.get(out_ext, 'JPEG')
            save_img.save(result_path, pil_fmt)
            return jsonify({'result': f'/uploads/{result_name}', 'ext': out_ext})

        elif action == 'pixelate':
            pixel_size = max(2, int(request.form.get('pixel_size', 10)))
            small = img.resize(
                (max(1, img.width // pixel_size), max(1, img.height // pixel_size)),
                Image.BOX
            )
            img = small.resize(img.size, Image.NEAREST)

        elif action == 'bw':
            img = ImageOps.grayscale(img).convert('RGBA')

        img.save(result_path, 'PNG')
        return jsonify({'result': f'/uploads/{result_name}', 'ext': out_ext})

    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500


if __name__ == '__main__':
    cleanup_old_files()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
