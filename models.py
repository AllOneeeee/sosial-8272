from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

db = SQLAlchemy()


# ==========================
# USER
# ==========================

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    nama = db.Column(
        db.String(100),
        nullable=False
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )


# ==========================
# KEGIATAN
# ==========================

class Kegiatan(db.Model):
    __tablename__ = "kegiatan"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nama = db.Column(
        db.String(200),
        nullable=False
    )

    tahun = db.Column(
        db.Integer,
        nullable=False
    )

    tanggal_mulai = db.Column(
        db.Date
    )

    tanggal_selesai = db.Column(
        db.Date
    )

    status = db.Column(
        db.String(50),
        default="Persiapan"
    )

    drive_link = db.Column(
        db.Text
    )

    blok_sensus = db.relationship(
        "BlokSensus",
        backref="kegiatan",
        lazy=True,
        cascade="all, delete-orphan"
    )

    link_anomali = db.relationship(
        "LinkAnomali",
        backref="kegiatan",
        lazy=True,
        cascade="all, delete-orphan"
    )
    link_lainnya = db.relationship(
    "LinkLainnya",
    backref="kegiatan",
    lazy=True,
    cascade="all, delete-orphan"
    )


# ==========================
# LINK ANOMALI
# ==========================

class LinkAnomali(db.Model):
    __tablename__ = "link_anomali"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    kegiatan_id = db.Column(
        db.Integer,
        db.ForeignKey("kegiatan.id"),
        nullable=False
    )

    judul = db.Column(
        db.String(200)
    )

    link = db.Column(
        db.Text
    )

    keterangan = db.Column(
        db.Text
    )


# ==========================
# PENUGASAN
# ==========================

class Penugasan(db.Model):
    __tablename__ = "penugasan"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    kegiatan_id = db.Column(
        db.Integer,
        db.ForeignKey("kegiatan.id"),
        nullable=False
    )

    ppl_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    pml_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    kegiatan = db.relationship(
        "Kegiatan",
        backref="penugasan"
    )

    ppl = db.relationship(
        "User",
        foreign_keys=[ppl_id]
    )

    pml = db.relationship(
        "User",
        foreign_keys=[pml_id]
    )


# ==========================
# BLOK SENSUS
# ==========================

class BlokSensus(db.Model):
    __tablename__ = "blok_sensus"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    kegiatan_id = db.Column(
        db.Integer,
        db.ForeignKey("kegiatan.id"),
        nullable=False
    )

    ppl_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    kecamatan = db.Column(
        db.String(50),
        nullable=False
    )

    kode_bs = db.Column(
        db.String(50),
        nullable=False
    )

    target = db.Column(
        db.Integer,
        default=16
    )

    realisasi = db.Column(
        db.Integer,
        default=0
    )

    diperiksa = db.Column(
        db.Integer,
        default=0
    )

    catatan_pml = db.Column(
        db.Text
    )

    status = db.Column(
        db.String(20),
        default="Belum"
    )

    ppl = db.relationship(
        "User",
        foreign_keys=[ppl_id]
    )




# ==========================
# ADMIN AWAL
# ==========================

def create_admin():

    admin = User.query.filter_by(
        username="admin"
    ).first()

    if not admin:

        admin = User(
            nama="Administrator",
            username="admin",
            password=generate_password_hash(
                "admin123"
            ),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

class LinkLainnya(db.Model):
    __tablename__ = "link_lainnya"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    kegiatan_id = db.Column(
        db.Integer,
        db.ForeignKey("kegiatan.id"),
        nullable=False
    )

    judul = db.Column(
        db.String(200)
    )

    link = db.Column(
        db.Text
    )

    keterangan = db.Column(
        db.Text
    )