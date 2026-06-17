from unittest import case

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    send_file
)

from io import BytesIO

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from config import Config
from models import *
from datetime import datetime

from openpyxl import Workbook
# ==========================
# APP
# ==========================

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()
    create_admin()


# ==========================
# HOME
# ==========================

@app.route("/")
def home():

    if current_user.is_authenticated:
        return redirect(
            url_for("dashboard")
        )

    return redirect(
        url_for("login")
    )


# ==========================
# LOGIN
# ==========================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Username atau password salah",
            "danger"
        )

    return render_template(
        "login.html"
    )


# ==========================
# LOGOUT
# ==========================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("login")
    )


# ==========================
# DASHBOARD
# ==========================

@app.route("/dashboard")
@login_required
def dashboard():

    # ADMIN
    if current_user.role == "admin":

        total_kegiatan = Kegiatan.query.count()
        total_ppl = User.query.filter_by(role="ppl").count()
        total_pml = User.query.filter_by(role="pml").count()
        total_bs = BlokSensus.query.count()

        kegiatan_progress = []

        tahun_filter = request.args.get(
    "tahun",
    type=int
)

        query = Kegiatan.query

        if tahun_filter:
            query = query.filter(
                Kegiatan.tahun == tahun_filter
            )

        kegiatan_list = query.order_by(
            db.case(
                (
                    Kegiatan.status == "Berjalan",
                    0
                ),
                else_=1
            ),
            Kegiatan.tanggal_mulai
        ).all()

        tahun_list = db.session.query(
            Kegiatan.tahun
        ).distinct().order_by(
            Kegiatan.tahun.desc()
        ).all()

        tahun_list = [x[0] for x in tahun_list]

        for kegiatan in kegiatan_list:

            bs_list = BlokSensus.query.filter_by(
                kegiatan_id=kegiatan.id
            ).all()

            total_target = sum(
                bs.target for bs in bs_list
            )

            total_realisasi = sum(
                bs.realisasi for bs in bs_list
            )

            total_diperiksa = sum(
                getattr(bs, "diperiksa", 0)
                for bs in bs_list
            )

            progress_ppl = 0
            progress_pml = 0

            if total_target > 0:

                progress_ppl = round(
                    total_realisasi * 100 / total_target,
                    1
                )

                progress_pml = round(
                    total_diperiksa * 100 / total_target,
                    1
                )

            kegiatan_progress.append({
                "id": kegiatan.id,
                "nama": kegiatan.nama,
                "target": total_target,
                "realisasi": total_realisasi,
                "diperiksa": total_diperiksa,
                "progress_ppl": progress_ppl,
                "progress_pml": progress_pml,
                "status": kegiatan.status
            })
        # CARD DASHBOARD

        kegiatan_berjalan = len([
            k for k in kegiatan_list
            if k.status == "Berjalan"
        ])

        total_target = 0
        total_realisasi = 0
        total_diperiksa = 0

        for kegiatan in kegiatan_list:

            bs_list = BlokSensus.query.filter_by(
                kegiatan_id=kegiatan.id
            ).all()

            total_target += sum(
                bs.target for bs in bs_list
            )

            total_realisasi += sum(
                bs.realisasi for bs in bs_list
            )

            total_diperiksa += sum(
                getattr(bs, "diperiksa", 0)
                for bs in bs_list
            )
  
        return render_template(
            "dashboard_admin.html",

            kegiatan_berjalan=kegiatan_berjalan,

            total_target=total_target,

            total_realisasi=total_realisasi,

            total_diperiksa=total_diperiksa,

            kegiatan_progress=kegiatan_progress,

            kegiatan_list=kegiatan_list,

            tahun=datetime.now().year,

            tahun_filter=tahun_filter,

            tahun_list=tahun_list
        )

    # PPL
    elif current_user.role == "ppl":

        bs_list = (
            BlokSensus.query
            .join(Kegiatan)
            .filter(
                BlokSensus.ppl_id == current_user.id,
                Kegiatan.status != "Selesai"
            )
            .all()
        )

        return render_template(
            "dashboard_ppl.html",
            bs_list=bs_list
        )

    # PML
    elif current_user.role == "pml":

        bs_list = (
            BlokSensus.query
            .join(Kegiatan)
            .filter(
                Kegiatan.status != "Selesai"
            )
            .all()
        )

        return render_template(
            "dashboard_pml.html",
            bs_list=bs_list
        )


# ==========================
# USERS
# ==========================

@app.route("/users")
@login_required
def users():

    if current_user.role != "admin":
        return redirect(
            url_for("dashboard")
        )

    data = User.query.order_by(
        User.nama
    ).all()

    return render_template(
        "users_list.html",
        data=data
    )


# ==========================
# TAMBAH USER
# ==========================

@app.route(
    "/users/tambah",
    methods=["GET", "POST"]
)
@login_required
def tambah_user():

    if current_user.role != "admin":
        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        user = User(
            nama=request.form["nama"],
            username=request.form["username"],
            password=generate_password_hash(
                request.form["password"]
            ),
            role=request.form["role"]
        )

        db.session.add(user)
        db.session.commit()

        flash(
            "User berhasil dibuat",
            "success"
        )

        return redirect(
            url_for("users")
        )

    return render_template(
        "user_form.html",
        user=None
    )


# ==========================
# EDIT USER
# ==========================

@app.route(
    "/users/edit/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def edit_user(id):

    if current_user.role != "admin":
        return redirect(
            url_for("dashboard")
        )

    user = User.query.get_or_404(id)

    if request.method == "POST":

        user.nama = request.form["nama"]
        user.username = request.form["username"]
        user.role = request.form["role"]

        if request.form["password"]:

            user.password = (
                generate_password_hash(
                    request.form["password"]
                )
            )

        db.session.commit()

        flash(
            "User berhasil diubah",
            "success"
        )

        return redirect(
            url_for("users")
        )

    return render_template(
        "user_form.html",
        user=user
    )


# ==========================
# HAPUS USER
# ==========================

@app.route(
    "/users/hapus/<int:id>"
)
@login_required
def hapus_user(id):

    if current_user.role != "admin":
        return redirect(
            url_for("dashboard")
        )

    user = User.query.get_or_404(id)

    if user.username == "admin":

        flash(
            "Admin tidak boleh dihapus",
            "danger"
        )

        return redirect(
            url_for("users")
        )

    db.session.delete(user)
    db.session.commit()

    flash(
        "User berhasil dihapus",
        "success"
    )

    return redirect(
        url_for("users")
    )
    
# ==========================
# KEGIATAN
# ==========================

@app.route("/kegiatan")
@login_required
def kegiatan():

    data = Kegiatan.query.order_by(
        Kegiatan.tahun.desc()
    ).all()
    

    return render_template(
        "kegiatan_list.html",
        data=data
    )


@app.route(
    "/kegiatan/tambah",
    methods=["GET", "POST"]
)
@login_required
def tambah_kegiatan():

    if current_user.role != "admin":
        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        data = Kegiatan(
            nama=request.form["nama"],
            tahun=int(request.form["tahun"]),
            tanggal_mulai=datetime.strptime(
                request.form["tanggal_mulai"],
                "%Y-%m-%d"
            ).date(),
            tanggal_selesai=datetime.strptime(
                request.form["tanggal_selesai"],
                "%Y-%m-%d"
            ).date(),
            status=request.form["status"]
        )

        db.session.add(data)
        db.session.commit()

        flash(
            "Kegiatan berhasil ditambahkan",
            "success"
        )

        return redirect(
            url_for("kegiatan")
        )

    return render_template(
        "kegiatan_form.html",
        kegiatan=None
    )


@app.route(
    "/kegiatan/edit/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def edit_kegiatan(id):

    data = Kegiatan.query.get_or_404(id)

    if request.method == "POST":

        data.nama = request.form["nama"]
        data.tahun = int(
            request.form["tahun"]
        )
        data.tanggal_mulai = datetime.strptime(
        request.form["tanggal_mulai"],
        "%Y-%m-%d"
        ).date()

        data.tanggal_selesai = datetime.strptime(
            request.form["tanggal_selesai"],
            "%Y-%m-%d"
        ).date()
        data.status = request.form["status"]

        db.session.commit()

        flash(
            "Kegiatan berhasil diubah",
            "success"
        )

        return redirect(
            url_for("kegiatan")
        )

    return render_template(
        "kegiatan_form.html",
        kegiatan=data
    )


@app.route("/kegiatan/hapus/<int:id>")
@login_required
def hapus_kegiatan(id):

    kegiatan = Kegiatan.query.get_or_404(id)

    BlokSensus.query.filter_by(
        kegiatan_id=id
    ).delete()

    Penugasan.query.filter_by(
        kegiatan_id=id
    ).delete()

    db.session.delete(kegiatan)
    db.session.commit()

    flash(
        "Kegiatan berhasil dihapus",
        "success"
    )

    return redirect(
        url_for("kegiatan")
    )
# ==========================
# PENUGASAN
# ==========================

@app.route("/penugasan")
@login_required
def penugasan():

    data = Penugasan.query.all()

    return render_template(
        "penugasan_list.html",
        data=data
    )


@app.route(
    "/penugasan/tambah",
    methods=["GET", "POST"]
)
@login_required
def tambah_penugasan():

    kegiatan = Kegiatan.query.all()

    # ambil semua user dulu
    semua_user = User.query.all()

    print("\n===== USER =====")
    for u in semua_user:
        print(u.id, u.nama, repr(u.role))

    ppl_list = User.query.filter_by(
        role="ppl"
    ).all()

    pml_list = User.query.filter_by(
        role="pml"
    ).all()

    print("Jumlah PPL :", len(ppl_list))
    print("Jumlah PML :", len(pml_list))


    if request.method == "POST":

        kegiatan_id = int(
            request.form["kegiatan_id"]
        )

        pml_id = int(
            request.form["pml_id"]
        )

        ppl_ids = request.form.getlist(
            "ppl_ids[]"
        )

        for ppl_id in ppl_ids:

            if ppl_id:

                data = Penugasan(

                    kegiatan_id=kegiatan_id,

                    pml_id=pml_id,

                    ppl_id=int(ppl_id)

                )

                db.session.add(data)

        db.session.commit()

        flash(
            "Penugasan berhasil dibuat",
            "success"
        )

        return redirect(
            url_for("penugasan")
        )


    return render_template(

        "penugasan_form.html",

        kegiatan=kegiatan,

        ppl_list=ppl_list,

        pml_list=pml_list

    )


@app.route(
    "/penugasan/hapus/<int:id>"
)
@login_required
def hapus_penugasan(id):

    data = Penugasan.query.get_or_404(id)

    db.session.delete(data)
    db.session.commit()

    flash(
        "Penugasan berhasil dihapus",
        "success"
    )

    return redirect(
        url_for("penugasan")
    )

# ==========================
# BLOK SENSUS
# ==========================

@app.route("/bs")
@login_required
def bs():

    data = BlokSensus.query.order_by(
        BlokSensus.kode_bs
    ).all()

    return render_template(
        "bs_list.html",
        data=data
    )


@app.route(
    "/bs/tambah",
    methods=["GET", "POST"]
)
@login_required
def tambah_bs():

    kegiatan = Kegiatan.query.all()

    ppl_list = User.query.filter_by(
        role="ppl"
    ).all()

    if request.method == "POST":

        daftar_bs = request.form["kode_bs"]

        for baris in daftar_bs.splitlines():

            baris = baris.strip()

            if not baris:
                continue

            try:

                kode_bs, target = baris.split(":")

                kode_bs = kode_bs.strip()
                target = int(target.strip())

            except ValueError:

                flash(
                    f"Format salah: {baris}",
                    "danger"
                )

                return redirect(
                    url_for("tambah_bs")
                )

            bs = BlokSensus(
                kegiatan_id=int(
                    request.form["kegiatan_id"]
                ),
                ppl_id=int(
                    request.form["ppl_id"]
                ),
                kecamatan=request.form["kecamatan"],
                kode_bs=kode_bs,
                target=target,
                realisasi=0,
                diperiksa=0,
                status="Belum"
            )

            db.session.add(bs)

        db.session.commit()

    return render_template(
        "bs_form.html",
        kegiatan=kegiatan,
        ppl_list=ppl_list,
        data=None
    )


@app.route(
    "/bs/edit/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def edit_bs(id):

    data = BlokSensus.query.get_or_404(id)

    kegiatan = Kegiatan.query.all()

    ppl_list = User.query.filter_by(
        role="ppl"
    ).all()

    if request.method == "POST":

        data.kegiatan_id = int(
            request.form["kegiatan_id"]
        )

        data.ppl_id = int(
            request.form["ppl_id"]
        )
        data.kecamatan = request.form["kecamatan"]

        data.kode_bs = request.form["kode_bs"]

        data.target = int(
            request.form["target"]
        )

        db.session.commit()

        flash(
            "BS berhasil diubah",
            "success"
        )

        return redirect(
            url_for("bs")
        )

    return render_template(
        "bs_form.html",
        kegiatan=kegiatan,
        ppl_list=ppl_list,
        data=data
    )


@app.route(
    "/bs/hapus/<int:id>"
)
@login_required
def hapus_bs(id):

    data = BlokSensus.query.get_or_404(id)

    db.session.delete(data)
    db.session.commit()

    flash(
        "BS berhasil dihapus",
        "success"
    )

    return redirect(
        url_for("bs")
    )
@app.route(
    "/bs/update/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def update_bs(id):

    data = BlokSensus.query.get_or_404(id)

    if request.method == "POST":

        realisasi = int(
            request.form["realisasi"]
        )

        data.realisasi = realisasi

        if realisasi == 0:
            data.status = "Belum"
        elif realisasi < data.target:
            data.status = "Berjalan"
        else:
            data.status = "Selesai"

        db.session.commit()

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "update_bs.html",
        data=data
    )

@app.route(
    "/pml/periksa/<int:id>",
    methods=["GET", "POST"]
)
@login_required
def periksa_bs(id):

    data = BlokSensus.query.get_or_404(id)

    if request.method == "POST":

        data.diperiksa = int(
            request.form["diperiksa"]
        )


        db.session.commit()

        flash(
            "Pemeriksaan berhasil disimpan",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "periksa_bs.html",
        data=data
    )
@app.route("/kegiatan/detail/<int:id>")
@login_required
def detail_kegiatan(id):

    kegiatan = Kegiatan.query.get_or_404(id)

    bs_list = BlokSensus.query.filter_by(
        kegiatan_id=id
    ).all()

    penugasan = Penugasan.query.filter_by(
        kegiatan_id=id
    ).all()

    mapping_pml = {
        p.ppl_id: p.pml.nama
        for p in penugasan
    }

    progress_kecamatan = {}

    for bs in bs_list:

        kec = bs.kecamatan

        if kec not in progress_kecamatan:
            progress_kecamatan[kec] = {
                "target": 0,
                "realisasi": 0,
                "diperiksa": 0
            }

        progress_kecamatan[kec]["target"] += bs.target
        progress_kecamatan[kec]["realisasi"] += bs.realisasi
        progress_kecamatan[kec]["diperiksa"] += bs.diperiksa

    for item in progress_kecamatan.values():

        if item["target"] > 0:
            item["progress_ppl"] = round(
                item["realisasi"] * 100 / item["target"], 1
            )

            item["progress_pml"] = round(
                item["diperiksa"] * 100 / item["target"], 1
            )
        else:
            item["progress_ppl"] = 0
            item["progress_pml"] = 0

    return render_template(
        "kegiatan_detail.html",
        kegiatan=kegiatan,
        bs_list=bs_list,
        mapping_pml=mapping_pml,
        progress_kecamatan=progress_kecamatan
    )
        
@app.route(
    "/kegiatan/<int:kegiatan_id>/anomali/tambah",
    methods=["GET", "POST"]
)
def tambah_anomali(kegiatan_id):

    kegiatan = Kegiatan.query.get_or_404(
        kegiatan_id
    )

    if request.method == "POST":

        anomali = LinkAnomali(
            kegiatan_id=kegiatan.id,
            judul=request.form["judul"],
            link=request.form["link"],
            keterangan=request.form["keterangan"]
        )

        db.session.add(anomali)
        db.session.commit()

        return redirect(
            url_for(
                "detail_kegiatan",
                id=kegiatan.id
            )
        )

    return render_template(
        "anomali_form.html",
        kegiatan=kegiatan
    )

@app.route("/anomali/hapus/<int:id>")
def hapus_anomali(id):

    anomali = LinkAnomali.query.get_or_404(id)

    kegiatan_id = anomali.kegiatan_id

    db.session.delete(anomali)
    db.session.commit()

    return redirect(
        url_for(
            "detail_kegiatan",
            id=kegiatan_id
        )
    )

@app.route(
    "/kegiatan/<int:id>/drive",
    methods=["GET", "POST"]
)
def edit_drive(id):

    kegiatan = Kegiatan.query.get_or_404(id)

    if request.method == "POST":

        kegiatan.drive_link = request.form["drive_link"]

        db.session.commit()

        return redirect(
            url_for(
                "detail_kegiatan",
                id=id
            )
        )

    return render_template(
        "drive_form.html",
        kegiatan=kegiatan
    )
    
    
from ai.predictor import (
    cari_kbli,
    cari_kbji
)


# ==========================
# KBLI AI
# ==========================

@app.route("/kbli")
@login_required
def kbli():

    return render_template(
        "kbli.html"
    )


@app.route(
    "/kbli/prediksi",
    methods=["GET", "POST"]
)
@login_required
def prediksi_kbli():

    if request.method == "GET":

        return redirect(
            url_for("kbli")
        )

    uraian = request.form.get(
        "uraian",
        ""
    ).strip()

    if not uraian:

        flash(
            "Uraian tidak boleh kosong",
            "danger"
        )

        return redirect(
            url_for("kbli")
        )

    hasil_kbli = cari_kbli(
        uraian
    )

    hasil_kbji = cari_kbji(
        uraian
    )

    return render_template(
        "hasil_kbli.html",
        uraian=uraian,
        hasil_kbli=hasil_kbli,
        hasil_kbji=hasil_kbji
    )

@app.route(
    "/kegiatan/<int:kegiatan_id>/link-lainnya/tambah",
    methods=["GET", "POST"]
)
@login_required
def tambah_link_lainnya(kegiatan_id):

    kegiatan = Kegiatan.query.get_or_404(
        kegiatan_id
    )

    if request.method == "POST":

        data = LinkLainnya(
            kegiatan_id=kegiatan.id,
            judul=request.form["judul"],
            link=request.form["link"],
            keterangan=request.form["keterangan"]
        )

        db.session.add(data)
        db.session.commit()

        return redirect(
            url_for(
                "detail_kegiatan",
                id=kegiatan.id
            )
        )

    return render_template(
        "anomali_form.html",
        kegiatan=kegiatan
    )
@app.route(
    "/link-lainnya/hapus/<int:id>"
)
@login_required
def hapus_link_lainnya(id):

    data = LinkLainnya.query.get_or_404(id)

    kegiatan_id = data.kegiatan_id

    db.session.delete(data)
    db.session.commit()

    return redirect(
        url_for(
            "detail_kegiatan",
            id=kegiatan_id
        )
    )
    
@app.route("/forms")
@login_required
def forms():

    data = FormTemplate.query.all()

    return render_template(

        "form_list.html",

        data=data

    )
@app.route(

"/forms/tambah",

methods=["GET","POST"]

)

@login_required
def tambah_form():

    kegiatan = Kegiatan.query.all()



    if request.method=="POST":


        data = FormTemplate(

            nama=request.form["nama"],

            kegiatan_id=int(

                request.form["kegiatan_id"]

            ),

            role=request.form["role"]

        )


        db.session.add(data)

        db.session.commit()


        return redirect(

            url_for(

                "forms"

            )

        )



    return render_template(

        "form_form.html",

        kegiatan=kegiatan

    )
@app.route(

"/forms/<int:id>/field"

)

@login_required
def field(id):


    data = FormField.query.filter_by(

        form_id=id

    ).all()


    form = FormTemplate.query.get_or_404(

        id

    )


    return render_template(

        "field_list.html",

        data=data,

        form=form

    )
@app.route(

"/forms/<int:id>/field/tambah",

methods=["GET","POST"]

)

@login_required
def tambah_field(id):


    if request.method=="POST":



        data = FormField(


            form_id=id,


            pertanyaan=request.form[

                "pertanyaan"

            ],


            tipe=request.form[

                "tipe"

            ]

        )


        db.session.add(

            data

        )


        db.session.commit()



        return redirect(

            url_for(

                "field",

                id=id

            )

        )



    return render_template(

        "field_form.html"

    )
@app.route(

"/my-form"

)

@login_required
def my_form():



    data = FormTemplate.query.filter_by(

        role=current_user.role

    ).all()



    return render_template(

        "my_forms.html",

        data=data

    )

@app.route(

"/isi-form/<int:id>",

methods=["GET","POST"]

)

@login_required
def isi_form(id):



    form = FormTemplate.query.get_or_404(

        id

    )



    fields = FormField.query.filter_by(

        form_id=id

    ).all()



    if request.method=="POST":


        response = FormResponse(

            form_id=id,

            user_id=current_user.id

        )


        db.session.add(

            response

        )



        db.session.commit()



        for f in fields:


            ans = FormAnswer(


                response_id=response.id,


                field_id=f.id,


                jawaban=request.form.get(

                    str(f.id)

                )

            )


            db.session.add(

                ans

            )



        db.session.commit()



        return redirect(

            url_for(

                "dashboard"

            )

        )



    return render_template(

        "isi_form.html",

        form=form,

        fields=fields

    )
    
@app.route("/forms/<int:id>/hasil")
@login_required
def hasil_form(id):

    form = FormTemplate.query.get_or_404(id)

    users = User.query.filter_by(
        role=form.role
    ).order_by(
        User.nama
    ).all()


    responses = FormResponse.query.filter_by(
        form_id=id
    ).all()


    sudah = {
        r.user_id:r
        for r in responses
    }


    return render_template(

        "hasil_form.html",

        form=form,

        users=users,

        sudah=sudah

    )



@app.route(
"/forms/<int:id>/detail/<int:user_id>"
)

@login_required
def detail_respon(

id,

user_id

):


    form = FormTemplate.query.get_or_404(

        id

    )


    user = User.query.get_or_404(

        user_id

    )


    response = FormResponse.query.filter_by(

        form_id=id,

        user_id=user_id

    ).first()



    if not response:

        flash(

            "Belum ada jawaban",

            "warning"

        )

        return redirect(

            url_for(

                "hasil_form",

                id=id

            )

        )



    answers = FormAnswer.query.filter_by(

        response_id=response.id

    ).all()



    mapping = {}


    for a in answers:


        field = FormField.query.get(

            a.field_id

        )


        mapping[

            field.pertanyaan

        ] = a.jawaban



    return render_template(

        "detail_respon.html",

        form=form,

        user=user,

        mapping=mapping

    )
@app.route(
"/forms/field/edit/<int:id>",
methods=["GET","POST"]
)
@login_required
def edit_field(id):

    field = FormField.query.get_or_404(id)

    if request.method=="POST":

        field.pertanyaan = request.form[
            "pertanyaan"
        ]

        field.tipe = request.form[
            "tipe"
        ]

        db.session.commit()

        flash(

            "Pertanyaan berhasil diubah",

            "success"

        )

        return redirect(

            url_for(

                "field",

                id=field.form_id

            )

        )


    return render_template(

        "field_form.html",

        field=field

    )
@app.route(
"/forms/field/hapus/<int:id>"
)
@login_required
def hapus_field(id):


    field = FormField.query.get_or_404(id)

    form_id = field.form_id


    db.session.delete(

        field

    )


    db.session.commit()


    flash(

        "Pertanyaan dihapus",

        "success"

    )


    return redirect(

        url_for(

            "field",

            id=form_id

        )

    )

@app.route("/forms/<int:id>/excel")
@login_required
def export_excel(id):


    form = FormTemplate.query.get_or_404(id)


    fields = FormField.query.filter_by(

        form_id=id

    ).order_by(

        FormField.id

    ).all()



    wb = Workbook()

    ws = wb.active



    ws.title = form.nama



    header = ["Nama"]



    for f in fields:

        header.append(

            f.pertanyaan

        )



    ws.append(

        header

    )



    responses = FormResponse.query.filter_by(

        form_id=id

    ).all()




    for r in responses:



        user = User.query.get(

            r.user_id

        )



        row = [

            user.nama

            if user

            else

            "User Dihapus"

        ]




        for f in fields:



            ans = FormAnswer.query.filter_by(


                response_id=r.id,


                field_id=f.id


            ).first()




            if ans:


                row.append(

                    ans.jawaban

                )



            else:


                row.append("")



        ws.append(

            row

        )



    output = BytesIO()


    wb.save(

        output

    )


    output.seek(

        0

    )



    return send_file(


        output,


        download_name=f"{form.nama}.xlsx",


        as_attachment=True,


        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


    )


if __name__ == "__main__":
    app.run(debug=True)
