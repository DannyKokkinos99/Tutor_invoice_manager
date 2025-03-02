# pylint: disable= C0116,C0114,C0115,W1203,C0411
import os
from dotenv import load_dotenv
from datetime import datetime
from flask import (
    render_template,
    redirect,
    url_for,
    request,
    send_file,
    Blueprint,
    jsonify,
)
from models import db, Student, Invoice
from forms import AddStudentForm, EditStudentForm, RemoveStudentForm, CreateInvoiceForm
from pdf import InvoicePDF
from gdrive import Gdrive
from emailer import Emailer
from utility.logger import logger
from services import (
    update_local_database,
    add_students,
    create_tax_csv,
    delete_tax_csv,
    get_pending_tax_year,
)


GOOGLE_DOC = "1pnp-XjBkuIb0LnspKW3d2uw2v6l7Byxxfuwgy5b0Oak"
PARENT_FOLDER_ID = "1--qhpO7fr5q4q7x0pRxdiETcFyBsNOGN"  # FOUND IN URL
TAX_RETURNS_FOLDER_ID = "1bpqM7ZChtiegKoJvV1MLpwIZ2PuKSLtv"
SERVICE_ACCOUNT_FILE = (
    "service_account.json"  # GIVE FOLDER PERMISSIONS TO SERVICE ACCOUNT
)
SCOPE = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.readonly",
]  # do not change this
LOCAL_PARENT_FOLDER = "Invoices"
TAX_PARENT_FOLDER = "Invoices"


drive_manager = Gdrive(SERVICE_ACCOUNT_FILE, SCOPE)
email_manager = Emailer(os.getenv("EMAIL"), os.getenv("APP_PASSWORD"))

load_dotenv()
app_routes = Blueprint("app_routes", __name__)


@app_routes.route("/")
def index():
    """index endpoint"""
    return render_template("index.html")


@app_routes.route("/get-student-details", methods=["GET"])
def get_student_details():
    student_id = int(request.args.get("student_id"))
    student = Student.query.get(student_id)
    form = EditStudentForm()
    form.set_choices()
    if student:
        return render_template("filled_form.html", student=student, form=form)
    return 404


@app_routes.route("/add-student", methods=["GET", "POST"])
def add_student():
    form = AddStudentForm()
    if form.validate_on_submit():
        # Create new student object
        new_student = Student(
            name=form.name.data,
            surname=form.surname.data,
            parent=form.parent.data,
            email=form.email.data,
            address=form.address.data,
            phone_number=form.phone_number.data,
            price_per_hour=form.price_per_hour.data,
        )
        # Add student to database
        db.session.add(new_student)
        db.session.commit()
        logger.critical("Added student to database")
        return redirect(
            url_for("app_routes.index")
        )  # Redirect to index or another page after submission
    return render_template("add_student.html", form=form)


@app_routes.route("/edit-student", methods=["GET", "POST"])
def edit_student():
    form = EditStudentForm()
    form.set_choices()  # Populate choices for student_id dropdown
    if request.method == "POST":
        student_id = form.student_id.data
        student = Student.query.get(student_id)
        if student:
            student.name = form.name.data
            student.surname = form.surname.data
            student.parent = form.parent.data
            student.email = form.email.data
            student.address = form.address.data
            student.phone_number = form.phone_number.data
            student.price_per_hour = form.price_per_hour.data
            db.session.commit()
            logger.critical("Edited student")
            return redirect(
                url_for("app_routes.index")
            )  # Redirect to index or another page after submission
    return render_template("edit_student.html", form=form)


@app_routes.route("/remove-student", methods=["GET", "POST"])
def remove_student():
    form = RemoveStudentForm()
    form.set_choices()  # Populate choices for student_id dropdown
    if request.method == "POST":
        student_id = form.student_id.data
        student = Student.query.get(student_id)
        if student:
            db.session.delete(student)
            db.session.commit()
            logger.critical("Student removed")
            return redirect(url_for("app_routes.index"))
    return render_template("remove_student.html", form=form)


@app_routes.route("/create-invoice-form", methods=["GET", "POST"])
def create_invoice_form():
    form = CreateInvoiceForm()
    form.set_choices()  # Populate choices for student_id dropdown
    if request.method == "POST" and form.validate_on_submit():
        student_id = form.student_id.data
        quantity = form.hours_tutored.data
        student = Student.query.get(student_id)
        if student:
            # Find invoice count from drive
            folder_id = drive_manager.ensure_folder_exists(
                PARENT_FOLDER_ID, student.name
            )
            file_count = drive_manager.file_count(folder_id) + 1
            student.invoice_count = file_count
            db.session.commit()
            unit_price = student.price_per_hour
            total = quantity * unit_price
            # Create Invoice
            pdf = InvoicePDF()
            pdf.add_page()
            pdf.company_details()
            pdf.customer_details(student)
            pdf.ln(10)
            pdf.invoice_details(student.invoice_count)
            pdf.ln(10)
            pdf.invoice_table(quantity, unit_price, total)
            pdf.ln(10)
            pdf.total_amount(total)
            pdf.create_folders(student.name)
            pdf.output(f"Invoices/{student.name}/Invoice-{student.invoice_count}.pdf")
            return render_template(
                "invoice_inspection.html",
                student_id=student_id,
                hours=quantity,
                total=total,
            )
    return render_template("invoice_form.html", form=form)


@app_routes.route("/update_database", methods=["GET"])
def update_database():
    if request.method == "GET":
        add_students(drive_manager.get_students_from_gdoc(GOOGLE_DOC))
        folder_names = drive_manager.update_database(PARENT_FOLDER_ID, "Invoices")
        update_local_database(LOCAL_PARENT_FOLDER, folder_names)
        return redirect(url_for("app_routes.index"))


@app_routes.route("/prepare_tax_return", methods=["GET"])
def prepare_tax_return():
    if request.method == "GET":
        tax_year, start_date, end_date = get_pending_tax_year()
        csv_file_path = os.path.join(TAX_PARENT_FOLDER, tax_year)
        create_tax_csv(csv_file_path, start_date, end_date)
        drive_manager.upload_file(
            TAX_RETURNS_FOLDER_ID, csv_file_path, tax_year, mimetype="text/csv"
        )
        delete_tax_csv(csv_file_path)
        return redirect(url_for("app_routes.index"))


@app_routes.route("/pdf")
def serve_pdf():
    student_id = int(request.args.get("student_id"))
    student = Student.query.get(student_id)
    return send_file(
        f"Invoices/{student.name}/Invoice-{student.invoice_count}.pdf",
        mimetype="application/pdf",
    )


@app_routes.route("/invoice_send", methods=["POST"])
def invoice_send():
    student_id = int(request.args.get("student_id"))
    hours = float(request.args.get("hours"))
    total = float(request.args.get("total"))
    student = Student.query.get(student_id)
    # Send email
    try:
        email_manager.send_email("email_template.txt", student)
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
    # Create new invoice database entry
    date = datetime.now().strftime("%Y-%m-%d")
    new_invoice = Invoice(hours=hours, total=total, student_id=student_id, date=date)
    db.session.add(new_invoice)
    db.session.commit()
    logger.info("Invoice created ✅")
    # Save Invoice to google drive
    folder_id = drive_manager.ensure_folder_exists(PARENT_FOLDER_ID, student.name)
    file_path = f"Invoices/{student.name}/Invoice-{student.invoice_count}.pdf"
    file_name = f"Invoice-{student.invoice_count}.pdf"
    drive_manager.upload_file(folder_id, file_path, file_name)
    return render_template("index.html")


@app_routes.route("/api/get_total_students", methods=["GET"])
def get_total_students():
    students = Student.query.all()
    return str(len(students) - 1)


@app_routes.route("/api/get_total_hours", methods=["GET"])
def get_total_hours():
    invoices = Invoice.query.all()
    hours_list = [invoice.hours for invoice in invoices]
    hours = sum(hours_list)
    return str(hours)


@app_routes.route("/api/get_total_paid", methods=["GET"])
def get_total_paid():
    invoices = Invoice.query.all()
    total_list = [invoice.total for invoice in invoices]
    total = round(sum(total_list))
    return f"£{str(total)}"
