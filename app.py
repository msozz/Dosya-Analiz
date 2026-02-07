#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dosya Analiz Web Uygulaması
===========================
Flask tabanlı web arayüzü ile proje klasörlerini analiz eder.
"""

import os
import sys
import json
import tempfile
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename

# Kendi modülümüzü import et
from dosya_analiz import (
    analyze_excel, analyze_word, analyze_pdf,
    build_tree, categorize_files, generate_folder_report,
    generate_master_report, format_size,
    HAS_OPENPYXL, HAS_DOCX, HAS_PDF, HAS_XLRD,
    EXCEL_EXTENSIONS, EXCEL_OLD_EXTENSIONS, WORD_EXTENSIONS, PDF_EXTENSIONS,
    RAPOR_KLASOR_ADI, RAPOR_DOSYA_ADI, IGNORED_DIRS
)

# ─── Flask Uygulaması ─────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dosya-analiz-secret-key-2024')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB max upload
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp(prefix='dosya_analiz_')

# İzin verilen dosya uzantıları
ALLOWED_EXTENSIONS = (
    EXCEL_EXTENSIONS | EXCEL_OLD_EXTENSIONS | 
    WORD_EXTENSIONS | PDF_EXTENSIONS | 
    {'.zip', '.tar', '.gz'}
)


def allowed_file(filename):
    """Dosya uzantısının izin verilip verilmediğini kontrol eder."""
    return '.' in filename and Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def cleanup_temp_folder(folder_path):
    """Geçici klasörü temizler."""
    try:
        if Path(folder_path).exists():
            shutil.rmtree(folder_path)
    except Exception:
        pass


# ─── Web Rotaları ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    """Ana sayfa."""
    library_status = {
        'openpyxl': HAS_OPENPYXL,
        'xlrd': HAS_XLRD,
        'python-docx': HAS_DOCX,
        'pdfplumber': HAS_PDF
    }
    return render_template('index.html', library_status=library_status)


@app.route('/upload', methods=['POST'])
def upload_file():
    """Tek dosya yükleme ve analiz."""
    if 'file' not in request.files:
        return jsonify({'error': 'Dosya seçilmedi'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Bu dosya türü desteklenmiyor'}), 400
    
    filename = secure_filename(file.filename)
    temp_dir = tempfile.mkdtemp(dir=app.config['UPLOAD_FOLDER'])
    filepath = os.path.join(temp_dir, filename)
    file.save(filepath)
    
    try:
        ext = Path(filename).suffix.lower()
        result = {
            'filename': filename,
            'size': format_size(os.path.getsize(filepath)),
            'type': ext,
            'analysis': None
        }
        
        if ext in EXCEL_EXTENSIONS or ext in EXCEL_OLD_EXTENSIONS:
            result['analysis'] = analyze_excel(filepath)
            result['category'] = 'excel'
        elif ext in WORD_EXTENSIONS:
            result['analysis'] = analyze_word(filepath)
            result['category'] = 'word'
        elif ext in PDF_EXTENSIONS:
            result['analysis'] = analyze_pdf(filepath)
            result['category'] = 'pdf'
        elif ext == '.zip':
            # ZIP dosyasını çıkar ve analiz et
            extract_dir = os.path.join(temp_dir, 'extracted')
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Klasör analizi yap
            result['analysis'] = analyze_folder_web(extract_dir)
            result['category'] = 'folder'
        else:
            result['analysis'] = 'Bu dosya türü için detaylı analiz mevcut değil.'
            result['category'] = 'other'
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': f'Analiz hatası: {str(e)}'}), 500
    
    finally:
        # Geçici dosyaları temizle
        cleanup_temp_folder(temp_dir)


@app.route('/upload-folder', methods=['POST'])
def upload_folder():
    """ZIP olarak klasör yükleme ve analiz."""
    if 'folder' not in request.files:
        return jsonify({'error': 'Dosya seçilmedi'}), 400
    
    file = request.files['folder']
    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi'}), 400
    
    if not file.filename.lower().endswith('.zip'):
        return jsonify({'error': 'Lütfen ZIP dosyası yükleyin'}), 400
    
    filename = secure_filename(file.filename)
    temp_dir = tempfile.mkdtemp(dir=app.config['UPLOAD_FOLDER'])
    filepath = os.path.join(temp_dir, filename)
    file.save(filepath)
    
    try:
        # ZIP'i çıkar
        extract_dir = os.path.join(temp_dir, 'project')
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # __MACOSX gibi klasörleri sil
        macosx_dir = os.path.join(extract_dir, '__MACOSX')
        if os.path.exists(macosx_dir):
            shutil.rmtree(macosx_dir)
        
        # Eğer tek bir ana klasör varsa, ona in
        subdirs = [d for d in os.listdir(extract_dir) if os.path.isdir(os.path.join(extract_dir, d))]
        if len(subdirs) == 1 and not os.listdir(extract_dir) == subdirs:
            files_in_root = [f for f in os.listdir(extract_dir) if os.path.isfile(os.path.join(extract_dir, f))]
            if not files_in_root:
                extract_dir = os.path.join(extract_dir, subdirs[0])
        
        # Analiz yap
        analysis_result = analyze_folder_full(extract_dir)
        
        return jsonify(analysis_result)
    
    except zipfile.BadZipFile:
        return jsonify({'error': 'Geçersiz ZIP dosyası'}), 400
    except Exception as e:
        return jsonify({'error': f'Analiz hatası: {str(e)}'}), 500
    finally:
        cleanup_temp_folder(temp_dir)


@app.route('/upload-folder-files', methods=['POST'])
def upload_folder_files():
    """Klasör seçici ile yüklenen dosyaları analiz et."""
    if 'files' not in request.files:
        return jsonify({'error': 'Dosya seçilmedi'}), 400
    
    files = request.files.getlist('files')
    if not files or len(files) == 0:
        return jsonify({'error': 'Dosya seçilmedi'}), 400
    
    temp_dir = tempfile.mkdtemp(dir=app.config['UPLOAD_FOLDER'])
    
    try:
        # Dosyaları yapıyı koruyarak kaydet
        for file in files:
            if file.filename:
                # Göreli yolu al ve güvenli hale getir
                relative_path = file.filename
                # Klasör yapısını oluştur
                file_dir = os.path.join(temp_dir, os.path.dirname(relative_path))
                os.makedirs(file_dir, exist_ok=True)
                # Dosyayı kaydet
                file_path = os.path.join(temp_dir, relative_path)
                file.save(file_path)
        
        # Ana klasörü bul (ilk seviye klasör)
        subdirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
        if len(subdirs) == 1:
            extract_dir = os.path.join(temp_dir, subdirs[0])
        else:
            extract_dir = temp_dir
        
        # Analiz yap
        analysis_result = analyze_folder_full(extract_dir)
        
        return jsonify(analysis_result)
    
    except Exception as e:
        return jsonify({'error': f'Analiz hatası: {str(e)}'}), 500
    finally:
        cleanup_temp_folder(temp_dir)

@app.route('/analyze-path', methods=['POST'])
def analyze_path():
    """Yerel klasör yolunu analiz et (sunucu tarafı)."""
    data = request.get_json()
    if not data or 'path' not in data:
        return jsonify({'error': 'Klasör yolu belirtilmedi'}), 400
    
    folder_path = data['path']
    
    if not os.path.exists(folder_path):
        return jsonify({'error': f'Klasör bulunamadı: {folder_path}'}), 404
    
    if not os.path.isdir(folder_path):
        return jsonify({'error': 'Belirtilen yol bir klasör değil'}), 400
    
    try:
        analysis_result = analyze_folder_full(folder_path)
        return jsonify(analysis_result)
    except Exception as e:
        return jsonify({'error': f'Analiz hatası: {str(e)}'}), 500


@app.route('/library-status')
def library_status():
    """Kütüphane durumlarını döndürür."""
    return jsonify({
        'openpyxl': {'installed': HAS_OPENPYXL, 'description': 'Excel .xlsx dosyaları için'},
        'xlrd': {'installed': HAS_XLRD, 'description': 'Eski Excel .xls dosyaları için'},
        'python-docx': {'installed': HAS_DOCX, 'description': 'Word .docx dosyaları için'},
        'pdfplumber': {'installed': HAS_PDF, 'description': 'PDF dosyaları için'}
    })


# ─── Yardımcı Fonksiyonlar ────────────────────────────────────────────────────
def analyze_folder_web(folder_path):
    """Web için klasör analizi yapar."""
    result = []
    folder = Path(folder_path)
    
    # Klasör ağacı
    tree = build_tree(str(folder))
    result.append("## 🌳 Klasör Yapısı\n```")
    result.append("\n".join(tree))
    result.append("```\n")
    
    # Dosyaları kategorize et
    categories = categorize_files(folder_path)
    
    # Özet
    result.append("## 📊 Özet\n")
    total = sum(len(v) for v in categories.values())
    result.append(f"- **Toplam Dosya:** {total}")
    for cat, files in categories.items():
        if files:
            result.append(f"- **{cat.title()}:** {len(files)}")
    
    # Detaylı analizler
    if categories['excel']:
        result.append("\n## 📊 Excel Dosyaları\n")
        for f in categories['excel']:
            result.append(f"### {f.name}\n")
            result.append(analyze_excel(str(f)))
    
    if categories['word']:
        result.append("\n## 📝 Word Dosyaları\n")
        for f in categories['word']:
            result.append(f"### {f.name}\n")
            result.append(analyze_word(str(f)))
    
    if categories['pdf']:
        result.append("\n## 📕 PDF Dosyaları\n")
        for f in categories['pdf']:
            result.append(f"### {f.name}\n")
            result.append(analyze_pdf(str(f)))
    
    return "\n".join(result)


def analyze_folder_full(folder_path):
    """Tam klasör analizi yapar ve sonuçları JSON olarak döndürür."""
    root = Path(folder_path).resolve()
    
    # İstatistikler
    total_files = 0
    total_dirs = 0
    total_size = 0
    file_type_stats = {}
    
    for dirpath, dirnames, filenames in os.walk(str(root)):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS 
                       and not d.startswith('.') and d != RAPOR_KLASOR_ADI]
        total_dirs += len(dirnames)
        for fname in filenames:
            if not fname.startswith('.') and fname != RAPOR_DOSYA_ADI:
                total_files += 1
                fpath = os.path.join(dirpath, fname)
                try:
                    total_size += os.path.getsize(fpath)
                except:
                    pass
                ext = Path(fname).suffix.lower()
                if ext:
                    file_type_stats[ext] = file_type_stats.get(ext, 0) + 1
    
    # Klasör ağacı
    tree = build_tree(str(root))
    
    # Ana klasör analizi
    main_report = generate_folder_report(str(root), str(root))
    
    # Alt klasör analizleri
    folder_reports = []
    for dirpath, dirnames, filenames in os.walk(str(root)):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS 
                       and not d.startswith('.') and d != RAPOR_KLASOR_ADI]
        
        real_files = [f for f in filenames if not f.startswith('.') and f != RAPOR_DOSYA_ADI]
        if real_files and dirpath != str(root):
            folder = Path(dirpath)
            try:
                relative = str(folder.relative_to(root))
            except:
                relative = folder.name
            
            report = generate_folder_report(dirpath, str(root))
            folder_reports.append({
                'path': relative,
                'name': folder.name,
                'report': report
            })
    
    return {
        'name': root.name,
        'path': str(root),
        'stats': {
            'total_files': total_files,
            'total_dirs': total_dirs,
            'total_size': format_size(total_size),
            'total_size_bytes': total_size
        },
        'file_types': file_type_stats,
        'tree': "\n".join(tree),
        'main_report': main_report,
        'folder_reports': folder_reports,
        'timestamp': datetime.now().isoformat()
    }


# ─── Hata Yakalama ────────────────────────────────────────────────────────────
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Dosya çok büyük (maksimum 500 MB)'}), 413


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Sunucu hatası'}), 500


# ─── Uygulama Başlatma ────────────────────────────────────────────────────────
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Dosya Analiz Web Uygulaması')
    parser.add_argument('--host', default='127.0.0.1', help='Sunucu adresi (varsayılan: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='Port numarası (varsayılan: 5000)')
    parser.add_argument('--debug', action='store_true', help='Debug modunu etkinleştir')
    
    args = parser.parse_args()
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║         📁 Dosya Analiz Web Uygulaması                  ║
╚══════════════════════════════════════════════════════════╝

🌐 Sunucu: http://{args.host}:{args.port}
📦 Kütüphaneler:
   {'✅' if HAS_OPENPYXL else '❌'} openpyxl (Excel .xlsx)
   {'✅' if HAS_XLRD else '❌'} xlrd (Excel .xls)
   {'✅' if HAS_DOCX else '❌'} python-docx (Word)
   {'✅' if HAS_PDF else '❌'} pdfplumber (PDF)

Tarayıcınızda açın: http://{args.host}:{args.port}
Durdurmak için Ctrl+C
""")
    
    app.run(host=args.host, port=args.port, debug=args.debug)
