# pylint: disable= C0116,C0114,C0115
from pdf import InvoicePDF
from emailer import Emailer
"""Used for testing the emailing and pdf creating functions"""
class Student():
    """Class used for testing"""
    def __init__(self, name, surname, parent,
               email, address, phone_number, price_per_hour, invoice_count=1):

        self.name = name
        self.surname = surname
        self.parent = parent
        self.email = email
        self.address = address
        self.phone_number = phone_number
        self.price_per_hour = price_per_hour
        self.invoice_count = invoice_count

    def print_student(self):
        print(self.name)
        print(self.surname)
        print(self.email)
        print(self.address)
        print(self.phone_number)
        print(self.price_per_hour)
        print(self.invoice_count)

student1 = Student("Danny", "Magney", "Alice", "dannykokkinos@outlook.com",
                   "Church House, Marston St Lawrence, Banbury, Oxon OX17 2DA",
                   "+447949109673", 30, invoice_count=2)

### Testing PDF creator ###            
quantity_temp = 2
unit_price_temp = student1.price_per_hour
total_temp = quantity_temp * unit_price_temp

pdf = InvoicePDF()
pdf.add_page()
pdf.company_details()
pdf.customer_details(student1)
pdf.ln(10)
pdf.invoice_details(student1.invoice_count)
pdf.ln(10)
pdf.invoice_table(quantity_temp, unit_price_temp, total_temp)
pdf.ln(10)
pdf.total_amount(total_temp)
pdf.create_folders(student1.name)
pdf.output(f"Invoices/{student1.name}/Invoice-{student1.invoice_count}.pdf")

### Testing email Sender ###
SENDER_EMAIL = ""
SENDER_PASSWORD = ""

email = Emailer(SENDER_EMAIL,SENDER_PASSWORD)
email.send_email("email_template.txt", student1)
