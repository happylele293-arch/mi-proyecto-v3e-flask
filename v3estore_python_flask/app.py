from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "v3e-store-cambia-esta-clave")

# SQLite por defecto para que funcione al instante.
# Para MySQL cambia DATABASE_URL por algo como:
# mysql+pymysql://root:tu_clave@localhost/v3estore
db_path = os.path.join(os.path.dirname(__file__), "v3estore.db")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    documento = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    mensajes = db.relationship("MensajeContacto", backref="usuario_rel", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Producto(db.Model):
    __tablename__ = "productos"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    categoria = db.Column(db.String(50), nullable=False, default="general")
    precio = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(255), nullable=True)
    descripcion = db.Column(db.String(255), nullable=True)
    stock = db.Column(db.Integer, nullable=False, default=10)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

class MensajeContacto(db.Model):
    __tablename__ = "mensajes_contacto"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    asunto = db.Column(db.String(150), nullable=True)
    mensaje = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

def get_current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return Usuario.query.get(uid)

@app.context_processor
def inject_user():
    return {"usuario_actual": get_current_user()}

def login_required():
    if not get_current_user():
        flash("Debes iniciar sesión para continuar.", "error")
        return False
    return True

@app.route("/")
@app.route("/index.html")
def index():
    destacados = Producto.query.order_by(Producto.creado_en.desc()).limit(8).all()
    return render_template("index.html", destacados=destacados)

@app.route("/registro.html", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        documento = request.form.get("documento", "").strip()
        email = request.form.get("email", "").strip().lower()
        usuario = request.form.get("usuario", "").strip()
        fecha_nacimiento_raw = request.form.get("fecha_nacimiento", "").strip()
        password = request.form.get("password", "").strip()

        if not all([nombre, documento, email, usuario, fecha_nacimiento_raw, password]):
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for("registro"))

        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "error")
            return redirect(url_for("registro"))

        try:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento_raw, "%Y-%m-%d").date()
        except ValueError:
            flash("La fecha de nacimiento no es válida.", "error")
            return redirect(url_for("registro"))

        edad = date.today().year - fecha_nacimiento.year - ((date.today().month, date.today().day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        if edad < 13:
            flash("Debes tener al menos 13 años para registrarte.", "error")
            return redirect(url_for("registro"))

        if Usuario.query.filter((Usuario.email == email) | (Usuario.documento == documento) | (Usuario.usuario == usuario)).first():
            flash("Ya existe un usuario con ese correo, documento o nombre de usuario.", "error")
            return redirect(url_for("registro"))

        nuevo = Usuario(
            nombre=nombre,
            documento=documento,
            email=email,
            usuario=usuario,
            fecha_nacimiento=fecha_nacimiento
        )
        nuevo.set_password(password)
        db.session.add(nuevo)
        db.session.commit()

        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("login"))

    return render_template("registro.html")

@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identidad = request.form.get("usuario", "").strip()
        password = request.form.get("clave", "").strip()

        user = Usuario.query.filter((Usuario.email == identidad) | (Usuario.usuario == identidad)).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["user_name"] = user.nombre
            flash("Bienvenida a V3E STORE.", "success")
            return redirect(url_for("dashboard"))
        flash("Credenciales inválidas.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("index"))

@app.route("/dashboard.html")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))
    total_productos = Producto.query.count()
    total_usuarios = Usuario.query.count()
    total_mensajes = MensajeContacto.query.count()
    ultimos_productos = Producto.query.order_by(Producto.creado_en.desc()).limit(5).all()
    return render_template(
        "dashboard.html",
        total_productos=total_productos,
        total_usuarios=total_usuarios,
        total_mensajes=total_mensajes,
        ultimos_productos=ultimos_productos
    )

@app.route("/perfil.html", methods=["GET", "POST"])
def perfil():
    if not login_required():
        return redirect(url_for("login"))
    user = get_current_user()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        documento = request.form.get("documento", "").strip()
        if not all([nombre, email, documento]):
            flash("Nombre, correo y documento son obligatorios.", "error")
            return redirect(url_for("perfil"))

        existe = Usuario.query.filter(
            ((Usuario.email == email) | (Usuario.documento == documento)) & (Usuario.id != user.id)
        ).first()
        if existe:
            flash("Correo o documento ya están en uso.", "error")
            return redirect(url_for("perfil"))

        user.nombre = nombre
        user.email = email
        user.documento = documento
        db.session.commit()
        flash("Perfil actualizado correctamente.", "success")
        return redirect(url_for("perfil"))

    member_days = (date.today() - user.creado_en.date()).days + 1
    return render_template("perfil.html", member_days=member_days)

@app.route("/productos.html")
def productos():
    productos = Producto.query.order_by(Producto.creado_en.desc()).all()
    return render_template("productos.html", productos=productos, vista="todos")

@app.route("/maquillaje.html")
def maquillaje():
    productos = Producto.query.filter_by(categoria="maquillaje").order_by(Producto.creado_en.desc()).all()
    return render_template("categoria.html", productos=productos, titulo="Maquillaje")

@app.route("/ropa.html")
def ropa():
    productos = Producto.query.filter_by(categoria="ropa").order_by(Producto.creado_en.desc()).all()
    return render_template("categoria.html", productos=productos, titulo="Ropa")

@app.route("/skincare.html")
def skincare():
    productos = Producto.query.filter_by(categoria="skincare").order_by(Producto.creado_en.desc()).all()
    return render_template("categoria.html", productos=productos, titulo="Skincare")

@app.route("/contacto.html", methods=["GET", "POST"])
def contacto():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()
        asunto = request.form.get("asunto", "").strip()
        mensaje = request.form.get("mensaje", "").strip()

        if not all([nombre, email, mensaje]):
            flash("Nombre, correo y mensaje son obligatorios.", "error")
            return redirect(url_for("contacto"))

        msg = MensajeContacto(
            nombre=nombre,
            email=email,
            asunto=asunto,
            mensaje=mensaje,
            usuario_id=get_current_user().id if get_current_user() else None
        )
        db.session.add(msg)
        db.session.commit()
        flash("Tu mensaje fue enviado correctamente.", "success")
        return redirect(url_for("contacto"))

    return render_template("contacto.html")

@app.route("/instagrampagina.html")
def instagrampagina():
    return render_template("instagrampagina.html")

# CRUD PRODUCTOS
@app.route("/admin/productos/nuevo", methods=["POST"])
def producto_nuevo():
    if not login_required():
        return redirect(url_for("login"))

    nombre = request.form.get("nombre", "").strip()
    categoria = request.form.get("categoria", "").strip().lower()
    precio = request.form.get("precio", "").strip()
    imagen = request.form.get("imagen", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    stock = request.form.get("stock", "").strip()

    if not nombre or not categoria or not precio:
        flash("Nombre, categoría y precio son obligatorios.", "error")
        return redirect(url_for("productos"))

    try:
        precio = float(precio)
        stock = int(stock or 0)
    except ValueError:
        flash("Precio o stock inválidos.", "error")
        return redirect(url_for("productos"))

    nuevo = Producto(
        nombre=nombre,
        categoria=categoria,
        precio=precio,
        imagen=imagen or None,
        descripcion=descripcion or None,
        stock=stock if stock >= 0 else 0
    )
    db.session.add(nuevo)
    db.session.commit()
    flash("Producto creado correctamente.", "success")
    return redirect(url_for("productos"))

@app.route("/admin/productos/<int:producto_id>/editar", methods=["GET", "POST"])
def producto_editar(producto_id):
    if not login_required():
        return redirect(url_for("login"))

    producto = Producto.query.get_or_404(producto_id)

    if request.method == "POST":
        producto.nombre = request.form.get("nombre", "").strip()
        producto.categoria = request.form.get("categoria", "").strip().lower()
        producto.imagen = request.form.get("imagen", "").strip() or None
        producto.descripcion = request.form.get("descripcion", "").strip() or None
        try:
            producto.precio = float(request.form.get("precio", "0"))
            producto.stock = int(request.form.get("stock", "0"))
        except ValueError:
            flash("Precio o stock inválidos.", "error")
            return redirect(url_for("producto_editar", producto_id=producto.id))

        if not producto.nombre or not producto.categoria:
            flash("Nombre y categoría son obligatorios.", "error")
            return redirect(url_for("producto_editar", producto_id=producto.id))

        db.session.commit()
        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for("productos"))

    return render_template("editar_producto.html", producto=producto)

@app.route("/admin/productos/<int:producto_id>/eliminar", methods=["POST"])
def producto_eliminar(producto_id):
    if not login_required():
        return redirect(url_for("login"))
    producto = Producto.query.get_or_404(producto_id)
    db.session.delete(producto)
    db.session.commit()
    flash("Producto eliminado correctamente.", "info")
    return redirect(url_for("productos"))

SEED_PRODUCTS = [{'nombre': 'Base Líquida Glow', 'precio': 220.0, 'imagen': 'img/base_liquida.jpg', 'categoria': 'maquillaje', 'descripcion': 'Producto de la categoría maquillaje'}, {'nombre': 'Polvo Compacto Mate', 'precio': 180.0, 'imagen': 'img/polvo_compacto.jpg', 'categoria': 'maquillaje', 'descripcion': 'Producto de la categoría maquillaje'}, {'nombre': 'Rubor Rosado', 'precio': 95.0, 'imagen': 'img/rubor_rosado.jpg', 'categoria': 'maquillaje', 'descripcion': 'Producto de la categoría maquillaje'}, {'nombre': 'Paleta Sombras Nude', 'precio': 320.0, 'imagen': 'img/paleta_nude.jpg', 'categoria': 'maquillaje', 'descripcion': 'Producto de la categoría maquillaje'}, {'nombre': 'Delineador Líquido', 'precio': 70.0, 'imagen': 'img/delineador_liquido.jpg', 'categoria': 'maquillaje', 'descripcion': 'Producto de la categoría maquillaje'}, {'nombre': 'Máscara de Pestañas', 'precio': 110.0, 'imagen': 'img/mascara_pestanas.jpg', 'categoria': 'maquillaje', 'descripcion': 'Producto de la categoría maquillaje'}, {'nombre': 'Labial Rojo Intenso', 'precio': 85.0, 'imagen': 'img/labial_rojo.jpg', 'categoria': 'maquillaje', 'descripcion': 'Producto de la categoría maquillaje'}, {'nombre': 'Labial Nude', 'precio': 85.0, 'imagen': 'img/labial_nude.jpg', 'categoria': 'maquillaje', 'descripcion': 'Producto de la categoría maquillaje'}, {'nombre': 'Corrector Líquido', 'precio': 120.0, 'imagen': 'img/corrector_liquido.jpg', 'categoria': 'maquillaje', 'descripcion': 'Producto de la categoría maquillaje'}, {'nombre': 'Iluminador Líquido', 'precio': 140.0, 'imagen': 'img/iluminador_liquido.jpg', 'categoria': 'maquillaje', 'descripcion': 'Producto de la categoría maquillaje'}, {'nombre': 'Bronzer Compacto', 'precio': 130.0, 'imagen': 'img/bronzer_compacto.jpg', 'categoria': 'maquillaje', 'descripcion': 'Producto de la categoría maquillaje'}, {'nombre': 'Gel de Cejas', 'precio': 75.0, 'imagen': 'img/gel_cejas.jpg', 'categoria': 'maquillaje', 'descripcion': 'Producto de la categoría maquillaje'}, {'nombre': 'Paleta Sombras Color', 'precio': 340.0, 'imagen': 'img/paleta_color.jpg', 'categoria': 'maquillaje', 'descripcion': 'Producto de la categoría maquillaje'}, {'nombre': 'Delineador en Lápiz', 'precio': 60.0, 'imagen': 'img/delineador_lapiz.jpg', 'categoria': 'maquillaje', 'descripcion': 'Producto de la categoría maquillaje'}, {'nombre': 'Gloss Transparente', 'precio': 65.0, 'imagen': 'img/gloss_transparente.jpg', 'categoria': 'maquillaje', 'descripcion': 'Producto de la categoría maquillaje'}, {'nombre': 'Base Líquida Glow', 'precio': 220.0, 'imagen': 'img/base_liquida.jpg', 'categoria': 'ropa', 'descripcion': 'Producto de la categoría ropa'}, {'nombre': 'Polvo Compacto Mate', 'precio': 180.0, 'imagen': 'img/polvo_compacto.jpg', 'categoria': 'ropa', 'descripcion': 'Producto de la categoría ropa'}, {'nombre': 'Rubor Rosado', 'precio': 95.0, 'imagen': 'img/rubor_rosado.jpg', 'categoria': 'ropa', 'descripcion': 'Producto de la categoría ropa'}, {'nombre': 'Paleta Sombras Nude', 'precio': 320.0, 'imagen': 'img/paleta_nude.jpg', 'categoria': 'ropa', 'descripcion': 'Producto de la categoría ropa'}, {'nombre': 'Delineador Líquido', 'precio': 70.0, 'imagen': 'img/delineador_liquido.jpg', 'categoria': 'ropa', 'descripcion': 'Producto de la categoría ropa'}, {'nombre': 'Máscara de Pestañas', 'precio': 110.0, 'imagen': 'img/mascara_pestanas.jpg', 'categoria': 'ropa', 'descripcion': 'Producto de la categoría ropa'}, {'nombre': 'Labial Rojo Intenso', 'precio': 85.0, 'imagen': 'img/labial_rojo.jpg', 'categoria': 'ropa', 'descripcion': 'Producto de la categoría ropa'}, {'nombre': 'Labial Nude', 'precio': 85.0, 'imagen': 'img/labial_nude.jpg', 'categoria': 'ropa', 'descripcion': 'Producto de la categoría ropa'}, {'nombre': 'Corrector Líquido', 'precio': 120.0, 'imagen': 'img/corrector_liquido.jpg', 'categoria': 'ropa', 'descripcion': 'Producto de la categoría ropa'}, {'nombre': 'Iluminador Líquido', 'precio': 140.0, 'imagen': 'img/iluminador_liquido.jpg', 'categoria': 'ropa', 'descripcion': 'Producto de la categoría ropa'}, {'nombre': 'Bronzer Compacto', 'precio': 130.0, 'imagen': 'img/bronzer_compacto.jpg', 'categoria': 'ropa', 'descripcion': 'Producto de la categoría ropa'}, {'nombre': 'Gel de Cejas', 'precio': 75.0, 'imagen': 'img/gel_cejas.jpg', 'categoria': 'ropa', 'descripcion': 'Producto de la categoría ropa'}, {'nombre': 'Paleta Sombras Color', 'precio': 340.0, 'imagen': 'img/paleta_color.jpg', 'categoria': 'ropa', 'descripcion': 'Producto de la categoría ropa'}, {'nombre': 'Delineador en Lápiz', 'precio': 60.0, 'imagen': 'img/delineador_lapiz.jpg', 'categoria': 'ropa', 'descripcion': 'Producto de la categoría ropa'}, {'nombre': 'Gloss Transparente', 'precio': 65.0, 'imagen': 'img/gloss_transparente.jpg', 'categoria': 'ropa', 'descripcion': 'Producto de la categoría ropa'}, {'nombre': 'Limpiador Facial', 'precio': 150.0, 'imagen': 'img/limpiador_facial.jpg', 'categoria': 'skincare', 'descripcion': 'Producto de la categoría skincare'}, {'nombre': 'Tónico Hidratante', 'precio': 130.0, 'imagen': 'img/tonico_hidratante.jpg', 'categoria': 'skincare', 'descripcion': 'Producto de la categoría skincare'}, {'nombre': 'Serum Vitamina C', 'precio': 210.0, 'imagen': 'img/serum_vitamina_c.jpg', 'categoria': 'skincare', 'descripcion': 'Producto de la categoría skincare'}, {'nombre': 'Crema Hidratante', 'precio': 170.0, 'imagen': 'img/crema_hidratante.jpg', 'categoria': 'skincare', 'descripcion': 'Producto de la categoría skincare'}, {'nombre': 'Protector Solar', 'precio': 160.0, 'imagen': 'img/protector_solar.jpg', 'categoria': 'skincare', 'descripcion': 'Producto de la categoría skincare'}, {'nombre': 'Mascarilla Facial', 'precio': 90.0, 'imagen': 'img/mascarilla_facial.jpg', 'categoria': 'skincare', 'descripcion': 'Producto de la categoría skincare'}]

def seed_data():
    if Producto.query.count() == 0:
        for p in SEED_PRODUCTS:
            db.session.add(Producto(**p))
        db.session.commit()

with app.app_context():
    db.create_all()
    seed_data()

if __name__ == "__main__":
    app.run(debug=True)
