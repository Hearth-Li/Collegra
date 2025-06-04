import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from . import mycerts
from .models import db, Certificate

# 配置文件上传
UPLOAD_FOLDER = 'uploads/certificates'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@mycerts.route('/mycerts')
def mycerts_main():
    """主界面路由"""
    # 获取统计数据
    stats = Certificate.get_stats(1)  # 这里需要替换为实际的用户ID
    # 获取最近上传的记录
    recent_uploads = Certificate.query.order_by(Certificate.created_at.desc()).limit(5).all()
    return render_template('mycerts/prototype/main.html', stats=stats, recent_uploads=recent_uploads)

@mycerts.route('/mycerts/upload', methods=['GET', 'POST'])
def mycerts_upload():
    """上传页面路由"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 确保上传目录存在
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # 创建证书记录
            certificate = Certificate(
                name=request.form['name'],
                category=request.form['category'],
                start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
                end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date(),
                description=request.form.get('description', ''),
                file_path=file_path,
                file_type=filename.rsplit('.', 1)[1].lower(),
                file_size=os.path.getsize(file_path),
                volunteer_hours=float(request.form.get('volunteer_hours', 0)) if request.form['category'] == 'volunteer' else None,
                user_id=1  # 这里需要替换为实际的用户ID
            )
            
            db.session.add(certificate)
            db.session.commit()
            
            flash('Certificate uploaded successfully')
            return redirect(url_for('mycerts.mycerts_main'))
            
    return render_template('mycerts/prototype/upload.html')

@mycerts.route('/mycerts/list')
def mycerts_list():
    """列表页面路由"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    sort = request.args.get('sort', 'date-desc')
    
    query = Certificate.query
    
    if category:
        query = query.filter_by(category=category)
    
    # 排序
    if sort == 'date-desc':
        query = query.order_by(Certificate.created_at.desc())
    elif sort == 'date-asc':
        query = query.order_by(Certificate.created_at.asc())
    elif sort == 'name-asc':
        query = query.order_by(Certificate.name.asc())
    elif sort == 'name-desc':
        query = query.order_by(Certificate.name.desc())
    
    certificates = query.paginate(page=page, per_page=10)
    return render_template('mycerts/prototype/list.html', certificates=certificates)

@mycerts.route('/mycerts/detail/<int:id>')
def mycerts_detail(id):
    """详情页面路由"""
    certificate = Certificate.query.get_or_404(id)
    return render_template('mycerts/prototype/detail.html', certificate=certificate)

@mycerts.route('/mycerts/export', methods=['GET', 'POST'])
def mycerts_export():
    """导出页面路由"""
    if request.method == 'POST':
        categories = request.form.getlist('categories')
        format = request.form.get('format', 'pdf')
        
        # 获取选中的证书
        certificates = Certificate.query.filter(Certificate.category.in_(categories)).all()
        
        # TODO: 实现导出逻辑
        # 这里需要实现PDF或Word文档的生成逻辑
        
        return jsonify({'message': 'Export completed'})
        
    return render_template('mycerts/prototype/export.html')

@mycerts.route('/mycerts/download/<int:id>')
def mycerts_download(id):
    """下载证书文件"""
    certificate = Certificate.query.get_or_404(id)
    return send_file(certificate.file_path, as_attachment=True) 