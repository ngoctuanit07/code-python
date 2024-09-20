# app.py

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from models import db, Product, Import, Export
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
import pandas as pd
from werkzeug.utils import secure_filename

# Đường dẫn để lưu file upload
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    allowed_extensions = {'xlsx', 'xls'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

class ProductAdmin(ModelView):
    # Các cài đặt hiển thị của Flask-Admin
    can_create = True
    can_edit = True
    can_delete = True
    column_searchable_list = ['name']
    column_filters = ['name', 'unit_price']

    # Thêm menu import
    @expose('/import/', methods=('GET', 'POST'))
    def import_view(self):
        if request.method == 'POST':
            # Kiểm tra xem có file được upload không
            if 'file' not in request.files:
                flash('Không có file được tải lên.', 'danger')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('Không có file được chọn.', 'danger')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                try:
                    # Đọc file Excel
                    df = pd.read_excel(filepath)
                    required_columns = {'name', 'description', 'unit_price'}
                    if not required_columns.issubset(set(df.columns)):
                        flash(f'File thiếu các cột bắt buộc: {required_columns}', 'danger')
                        return redirect(request.url)
                    
                    # Chuyển đổi dữ liệu và thêm vào cơ sở dữ liệu
                    for index, row in df.iterrows():
                        product = Product(
                            name=row['name'],
                            description=row.get('description', ''),
                            unit_price=row['unit_price']
                        )
                        db.session.add(product)
                    db.session.commit()
                    flash('Import sản phẩm thành công!', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Lỗi trong quá trình import: {e}', 'danger')
                finally:
                    # Xóa file sau khi xử lý
                    os.remove(filepath)
                return redirect(url_for('product.index_view'))
            else:
                flash('Chỉ cho phép file Excel (.xlsx, .xls)', 'danger')
                return redirect(request.url)
        return self.render('admin/import_product.html')

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Tạo bảng nếu chưa tồn tại
with app.app_context():
    db.create_all()

# Thiết lập Flask-Admin
admin = Admin(app, name='Quản Lý Kho', template_mode='bootstrap3')
admin.add_view(ProductAdmin(Product, db.session, name='Sản Phẩm'))
admin.add_view(ModelView(Import, db.session, name='Nhập Kho'))
admin.add_view(ModelView(Export, db.session, name='Xuất Kho'))

# Trang chủ
@app.route('/')
def index():
    query = request.args.get('query')
    if query:
        products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    else:
        products = Product.query.all()
    return render_template('index.html', products=products)

# Route Tìm Kiếm
@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        flash('Vui lòng nhập từ khóa để tìm kiếm.', 'warning')
        return redirect(url_for('index'))
    products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    return render_template('index.html', products=products)

# Nhập kho
@app.route('/import', methods=['GET', 'POST'])
def import_product():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        if not product_id or not quantity:
            flash('Vui lòng nhập đầy đủ thông tin.', 'danger')
            return redirect(url_for('import_product'))
        import_record = Import(product_id=product_id, quantity=int(quantity))
        db.session.add(import_record)
        db.session.commit()
        flash('Nhập kho thành công!', 'success')
        return redirect(url_for('index'))
    products = Product.query.all()
    return render_template('import.html', products=products)

# Xuất kho
@app.route('/export', methods=['GET', 'POST'])
def export_product():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        if not product_id or not quantity:
            flash('Vui lòng nhập đầy đủ thông tin.', 'danger')
            return redirect(url_for('export_product'))
        # Kiểm tra tồn kho
        total_import = db.session.query(db.func.sum(Import.quantity)).filter_by(product_id=product_id).scalar() or 0
        total_export = db.session.query(db.func.sum(Export.quantity)).filter_by(product_id=product_id).scalar() or 0
        inventory = total_import - total_export
        if inventory < int(quantity):
            flash('Không đủ hàng trong kho để xuất.', 'danger')
            return redirect(url_for('export_product'))
        export_record = Export(product_id=product_id, quantity=int(quantity))
        db.session.add(export_record)
        db.session.commit()
        flash('Xuất kho thành công!', 'success')
        return redirect(url_for('index'))
    products = Product.query.all()
    return render_template('export.html', products=products)

# Báo cáo
@app.route('/report', methods=['GET', 'POST'])
def report():
    products = Product.query.all()
    report_data = []
    selected_product = request.args.get('product_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Product.query

    if selected_product:
        query = query.filter(Product.id == selected_product)
    
    if start_date and end_date:
        try:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            flash('Ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD.', 'danger')
            return redirect(url_for('report'))
    else:
        start = end = None

    filtered_products = query.all()

    for product in filtered_products:
        import_query = Import.query.filter_by(product_id=product.id)
        export_query = Export.query.filter_by(product_id=product.id)

        if start and end:
            import_query = import_query.filter(Import.import_date.between(start, end))
            export_query = export_query.filter(Export.export_date.between(start, end))
        
        total_import = import_query.with_entities(db.func.sum(Import.quantity)).scalar() or 0
        total_export = export_query.with_entities(db.func.sum(Export.quantity)).scalar() or 0
        inventory = total_import - total_export
        report_data.append({
            'product': product,
            'total_import': total_import,
            'total_export': total_export,
            'inventory': inventory
        })

    return render_template('report.html', report_data=report_data, products=products, selected_product=selected_product, start_date=start_date, end_date=end_date)

if __name__ == '__main__':
    app.run(debug=True)
