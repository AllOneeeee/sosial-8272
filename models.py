from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

db = SQLAlchemy()


# ==========================
# USER
# ==========================

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    nama = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    role = db.Column(db.String(20))

    no_hp = db.Column(db.String(20))
    desa = db.Column(db.String(100))
    kecamatan = db.Column(db.String(100))

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
    
class FormTemplate(db.Model):
    __tablename__ = "form_template"

    id = db.Column(db.Integer, primary_key=True)

    nama = db.Column(db.String(200))

    kegiatan_id = db.Column(
        db.Integer,
        db.ForeignKey('kegiatan.id')
    )

    role = db.Column(db.String(10))

    deadline = db.Column(db.Date)

    aktif = db.Column(
        db.Boolean,
        default=True
    )



class FormField(db.Model):

    __tablename__ = "form_field"

    id = db.Column(db.Integer,
                   primary_key=True)

    form_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'form_template.id'
        )
    )

    pertanyaan = db.Column(
        db.String(300)
    )

    tipe = db.Column(
        db.String(30)
    )

    wajib = db.Column(
        db.Boolean,
        default=True
    )



class FormResponse(db.Model):

    __tablename__="form_response"

    id=db.Column(
        db.Integer,
        primary_key=True
    )

    form_id=db.Column(
        db.Integer
    )

    user_id=db.Column(
        db.Integer
    )



class FormAnswer(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    response_id = db.Column(
        db.Integer,
        db.ForeignKey('form_response.id')
    )

    field_id = db.Column(
        db.Integer,
        db.ForeignKey('form_field.id')
    )

    jawaban = db.Column(
        db.Text
    )


    response = db.relationship(
        'FormResponse'
    )


    field = db.relationship(
        'FormField'
    )
class DashboardKategori(db.Model):
    __tablename__ = "dashboard_kategori"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nama = db.Column(
        db.String(100),
        nullable=False
    )

    indikator = db.relationship(
        "DashboardIndikator",
        backref="kategori_rel",
        lazy=True,
        cascade="all, delete-orphan"
    )


class DashboardIndikator(db.Model):
    __tablename__ = "dashboard_indikator"

    id = db.Column(db.Integer, primary_key=True)

    kategori_id = db.Column(
        db.Integer,
        db.ForeignKey("dashboard_kategori.id")
    )

    nama = db.Column(db.String(200))

    satuan = db.Column(db.String(50))

    header_baris = db.Column(
        db.String(100),
        default="Kecamatan"
    )

    kategori = db.relationship(
        "DashboardKategori"
    )


class DashboardData(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    indikator_id = db.Column(

        db.Integer,

        db.ForeignKey(

            'dashboard_indikator.id'

        )

    )


    wilayah = db.Column(

        db.String(100)

    )


    tahun = db.Column(

        db.Integer

    )


    nilai = db.Column(

        db.Float

    )
def create_dashboard():



    daftar=[


"PDRB",

"IPM",

"Kemiskinan",

"Inflasi",

"TPT",

"Gini Ratio",

"Pariwisata",

"Pertanian"

]


    for x in daftar:



        ada = DashboardKategori.query.filter_by(

            nama=x

        ).first()



        if not ada:



            db.session.add(

                DashboardKategori(

                    nama=x

                )

            )



    db.session.commit()

class DashboardBaris(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    indikator_id = db.Column(
        db.Integer,
        db.ForeignKey('dashboard_indikator.id')
    )

    nama = db.Column(db.String(100))


class DashboardKolom(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    indikator_id = db.Column(
        db.Integer,
        db.ForeignKey('dashboard_indikator.id')
    )

    nama = db.Column(db.String(50))