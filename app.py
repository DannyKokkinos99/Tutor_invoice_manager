# pylint: disable= C0116,C0114,C0115
import secrets
from flask import Flask, render_template, redirect, url_for, request, send_file
from models import db, Student
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from forms import AddStudentForm, EditStudentForm, RemoveStudentForm, CreateInvoiceForm
from pdf import InvoicePDF
from emailer import Emailer


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
print(f"APP CREATED: {app}")

@app.route("/")
def index():
    """index endpoint"""
    return render_template("index.html")

@app.route('/get-student-details', methods=['GET'])
def get_student_details():
    student_id = int(request.args.get('student_id'))
    student = Student.query.get(student_id)
    form = EditStudentForm()
    form.set_choices()
    if student:
        return render_template("filled_form.html", student=student, form = form)
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
            return render_template("invoice_inspection.html", student_id=student_id)
    return render_template("invoice_form.html", form=form)

@app.route('/pdf')
def serve_pdf():
    print(request.method)
    print(f"REQUEST ARG: {request.args.get('student_id')}")
    student_id = int(request.args.get('student_id'))
    student = Student.query.get(student_id)
    return send_file(f'Invoices/{student.name}/Invoice-{student.invoice_count}.pdf',
                      mimetype='application/pdf')


@app.route('/invoice_send', methods=["POST"])
def invoice_send():
    sender_email = "dannykokkinos@outlook.com"
    sender_password = open("sender_password.txt", 'r', encoding= "UTF-8").read()
    # Send Invoice via email
    if request.method == "POST":
        student_id = int(request.args.get('student_id'))
        student = Student.query.get(student_id)
        email = Emailer(sender_email,sender_password)
        email.send_email("email_template.txt", student)
        # Increment the counter
        student.invoice_count = student.invoice_count + 1
        db.session.commit()
        return render_template('index.html')


if __name__ == "__main__":
    app.run(port=9000, debug=True)
