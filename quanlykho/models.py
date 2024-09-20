# models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    unit_price = db.Column(db.Numeric(10,2), nullable=False)
    
    imports = db.relationship('Import', backref='product', lazy=True)
    exports = db.relationship('Export', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Import(db.Model):
    __tablename__ = 'imports'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    import_date = db.Column(db.DateTime, server_default=db.func.now())
    
    def __repr__(self):
        return f'<Import {self.product.name} - {self.quantity}>'

class Export(db.Model):
    __tablename__ = 'exports'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    export_date = db.Column(db.DateTime, server_default=db.func.now())
    
    def __repr__(self):
        return f'<Export {self.product.name} - {self.quantity}>'
