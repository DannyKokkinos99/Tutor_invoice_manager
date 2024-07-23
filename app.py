# pylint: disable= C0116,C0114,C0115
import secrets
import os
from flask import Flask, render_template, redirect, url_for, request, send_file, jsonify
from models import db, Student, Invoice
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from forms import AddStudentForm, EditStudentForm, RemoveStudentForm, CreateInvoiceForm
from pdf import InvoicePDF
from gdrive import Gdrive
from emailer import Emailer
from utility.logger import get_logger
from dotenv import load_dotenv


PARENT_FOLDER_ID = "1--qhpO7fr5q4q7x0pRxdiETcFyBsNOGN"  # FOUND IN URL
SERVICE_ACCOUNT_FILE = (
    "service_account.json"  # GIVE FOLDER PERMISSIONS TO SERVICE ACCOUNT
)
SCOPE = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.readonly",
]  # do not change this

drive_manager = Gdrive(SERVICE_ACCOUNT_FILE, SCOPE)
email_manager = Emailer(os.getenv("EMAIL"), os.getenv("APP_PASSWORD"))
logger = get_logger(__name__)
load_dotenv()  # Loads env variables


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = secrets.token_hex(16)
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
    db.init_app(app)
    # Create all database tables
    with app.app_context():
        db.create_all()
    return app


app = create_app()


@app.route("/")
def index():
    """index endpoint"""
    return render_template("index.html")


@app.route("/get-student-details", methods=["GET"])
def get_student_details():
    student_id = int(request.args.get("student_id"))
    student = Student.query.get(student_id)
    form = EditStudentForm()
    form.set_choices()
    if student:
        return render_template("filled_form.html", student=student, form=form)
    return 404


@app.route("/add-student", methods=["GET", "POST"])
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
            url_for("index")
        )  # Redirect to index or another page after submission
    return render_template("add_student.html", form=form)


@app.route("/edit-student", methods=["GET", "POST"])
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
                url_for("index")
            )  # Redirect to index or another page after submission
    return render_template("edit_student.html", form=form)


@app.route("/remove-student", methods=["GET", "POST"])
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
            return redirect(url_for("index"))
    return render_template("remove_student.html", form=form)


@app.route("/create-invoice-form", methods=["GET", "POST"])
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


@app.route("/pdf")
def serve_pdf():
    student_id = int(request.args.get("student_id"))
    student = Student.query.get(student_id)
    return send_file(
        f"Invoices/{student.name}/Invoice-{student.invoice_count}.pdf",
        mimetype="application/pdf",
    )


@app.route("/invoice_send", methods=["POST"])
def invoice_send():
    student_id = int(request.args.get("student_id"))
    hours = float(request.args.get("hours"))
    total = float(request.args.get("total"))
    student = Student.query.get(student_id)
    # Send email
    email_manager.send_email("email_template.txt", student)
    # Create new invoice database entry
    new_invoice = Invoice(hours=hours, total=total, student_id=student_id)
    db.session.add(new_invoice)
    db.session.commit()
    logger.critical("Invoice entry created")
    # Save Invoice to google drive
    folder_id = drive_manager.ensure_folder_exists(PARENT_FOLDER_ID, student.name)
    file_path = f"Invoices/{student.name}/Invoice-{student.invoice_count}.pdf"
    file_name = f"Invoice-{student.invoice_count}.pdf"
    drive_manager.upload_file(folder_id, file_path, file_name)
    logger.critical("File uploaded to google drive")
    return render_template("index.html")


@app.route("/api/get_total_students", methods=["GET"])
def get_total_students():
    students = Student.query.all()
    return str(len(students) - 1)


@app.route("/api/get_total_hours", methods=["GET"])
def get_total_hours():
    invoices = Invoice.query.all()
    hours_list = [invoice.hours for invoice in invoices]
    hours = sum(hours_list)
    return str(hours)


@app.route("/api/get_total_paid", methods=["GET"])
def get_total_paid():
    invoices = Invoice.query.all()
    total_list = [invoice.total for invoice in invoices]
    total = round(sum(total_list))
    return f"£{str(total)}"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
