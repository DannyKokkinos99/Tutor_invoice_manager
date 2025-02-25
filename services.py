# pylint: disable= C0116,C0114,C0115,W1203
import os
import csv
from collections import defaultdict
from pathlib import Path
from datetime import datetime
from sqlalchemy import and_
import pdfplumber
from extensions import db
from models import Student, Invoice
from utility.logger import logger


# logger = get_logger(__name__)


def get_pending_tax_year():
    current_year = int(datetime.now().year) - 1
    previous_year = current_year - 1
    return (
        f"tax_return_{previous_year}_{current_year}.csv",
        f"{previous_year}-04-05",
        f"{current_year}-04-05",
    )


def delete_tax_csv(output_csv):
    file_path = Path(output_csv)
    if file_path.exists():
        file_path.unlink()


def create_tax_csv(output_csv, filter_start_date, filter_end_date):
    # Dictionary to store the total amount for each month name
    monthly_totals = defaultdict(float)
    invoices = Invoice.query.filter(
        and_(Invoice.date > filter_start_date, Invoice.date < filter_end_date)
    ).all()
    # Process each invoice
    for invoice in invoices:
        # Extract the month name from the date
        month_name = datetime.strptime(invoice.date, "%Y-%m-%d").strftime("%B")
        monthly_totals[month_name] += invoice.total

    # Write the results to a CSV file
    with open(output_csv, mode="w", newline="", encoding="UTF-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Personal"])  # Write the header
        # Sort by month name alphabetically
        for month, total in sorted(monthly_totals.items()):
            writer.writerow([total])


def add_students(students):
    db.session.query(Student).delete()
    logger.info("Adding students to database")
    for student in students:
        new_student = Student(
            name=student["name"],
            surname=student["surname"],
            parent=student["parent"],
            email=student["email"],
            address=student["address"],
            phone_number=student["phone_number"],
            price_per_hour=student["price_per_hour"],
        )
        db.session.add(new_student)
        db.session.commit()
        logger.info(f"  {student["name"]} {student["surname"]} ✅")


def get_student_id(student_name):
    student = Student.query.filter_by(name=student_name).first()
    if student:
        return student.id


def read_field_from_pdf(file_path, keyword):
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                for line in lines:
                    if keyword in line:
                        return line
    return ""


def update_local_database(parent_folder, folder_names):
    db.session.query(Invoice).delete()
    db.session.commit()
    logger.info("Adding invoices to database")
    for folder_name in folder_names:
        logger.info(f"   Adding invoices for {folder_name}")
        count = 0
        folder_path = os.path.join(parent_folder, folder_name)
        for file_name in os.listdir(folder_path):
            count += 1
            file_path = os.path.join(folder_path, file_name)
            total_price = float(read_field_from_pdf(file_path, "£").split("£")[2])
            hours = float(
                read_field_from_pdf(file_path, "£").split("£")[0].split(" ")[2]
            )
            student_id = get_student_id(folder_name)
            # Gets the date from invoice add formats it correctly for the database
            date_wrong_format = (
                read_field_from_pdf(file_path, "Invoice Date:").split(":")[1].lstrip()
            )
            split_wrong_date_format = date_wrong_format.split("/")
            day = split_wrong_date_format[0]
            month = split_wrong_date_format[1]
            year = split_wrong_date_format[2]
            correct_date_format = f"{year}-{month}-{day}"
            logger.info(f"     Invoice-{count} ✅")
            # Add all invoices to local db
            new_invoice = Invoice(
                hours=hours,
                total=total_price,
                student_id=student_id,
                date=correct_date_format,
            )
            db.session.add(new_invoice)
            db.session.commit()
