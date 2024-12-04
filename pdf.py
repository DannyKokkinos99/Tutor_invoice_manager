# pylint: disable= C0116,C0114,C0115
from datetime import datetime
import os
from fpdf import FPDF


R = 175
G = 238
B = 238


class InvoicePDF(FPDF):

    def header(self):
        self.set_font("Arial", "B", 24)
        self.cell(0, 10, "INVOICE", 0, 1, "C")

    def company_details(self):
        x_value = 10
        y_value = 30
        self.set_font("Arial", "B", 12)
        self.set_xy(x_value, y_value)
        self.cell(90, 35, "", 1)
        self.set_xy(x_value, y_value)
        self.set_fill_color(175, 238, 238)
        self.cell(90, 10, "", 1, fill=True)
        self.set_xy(x_value, y_value)
        self.cell(75, 10, "From", 0, 1)
        self.set_xy(x_value, y_value + 10)
        self.cell(75, 10, "Ntani Kokkinos")
        self.set_xy(x_value, y_value + 18)
        self.multi_cell(80, 5, "St. Thomas Street, The Milliners 308, BS1 6WT")
        self.set_xy(x_value, y_value + 26)
        self.cell(75, 10, "+447448646758")
        self.ln(20)

    def customer_details(self, student):
        x_value = 10
        y_value = 80
        self.set_font("Arial", "B", 12)
        self.set_xy(x_value, y_value)
        self.cell(90, 35, "", 1)
        self.set_xy(x_value, y_value)
        self.set_fill_color(175, 238, 238)
        self.cell(90, 10, "", 1, fill=True)
        self.set_xy(x_value, y_value)
        self.cell(75, 10, "Bill to", 0, 1)
        self.set_xy(x_value, y_value + 10)
        name = student.name.replace(student.name, student.parent)
        self.cell(75, 10, f"{name} {student.surname}")
        self.set_xy(x_value, y_value + 18)
        self.multi_cell(80, 5, student.address)
        self.set_xy(x_value, y_value + 26)
        self.cell(75, 10, f"{student.phone_number}")
        self.ln(20)

    def invoice_details(self, invoice_counter):
        today = datetime.today()
        formatted_date = today.strftime("%d/%m/%Y")
        x_value = 100
        y_value = 30
        self.set_font("Arial", "", 10)
        self.set_xy(x_value, y_value)
        self.cell(80, 10, f"Invoice Date: {formatted_date}", align="R")
        self.set_xy(x_value, y_value + 10)
        self.cell(80, 10, "Due: On Receipt", align="R")
        self.set_xy(x_value, y_value + 20)
        self.cell(80, 10, f"Invoice Number: {invoice_counter}", align="R")

    def invoice_table(self, quantity, unit_price, total):
        x_value = 10
        y_value = 135
        self.set_font("Arial", "B", 12)
        self.set_fill_color(175, 238, 238)
        self.set_xy(x_value, y_value)
        self.cell(80, 10, "Item", 1, fill=True, align="C")
        self.set_fill_color(175, 238, 238)
        self.cell(30, 10, "Quantity", 1, fill=True, align="C")
        self.set_fill_color(175, 238, 238)
        self.cell(40, 10, "Unit Price", 1, fill=True, align="C")
        self.set_fill_color(175, 238, 238)
        self.cell(40, 10, "Total", 1, fill=True, align="C")
        self.ln()
        self.set_font("Arial", "", 12)
        self.cell(80, 10, "Tuition Service", 1, align="C")
        self.cell(30, 10, str(quantity), 1, align="C")
        self.cell(40, 10, f"£{str(unit_price)}", 1, align="C")
        self.cell(40, 10, f"£{str(total)}", 1, align="C")
        self.ln()

    def total_amount(self, total):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, f"Total: £{total:.2f}", 0, 1, "R")
        self.set_xy(10, 180)
        self.cell(0, 10, "INVOICE IS PAID")

    def create_folders(self, folder_name):
        # add creating a new folder here
        main_folder = "Invoices"
        path = os.path.join(os.getcwd(), main_folder)
        if not os.path.exists(path):
            os.makedirs(path)

        path = os.path.join(os.getcwd(), f"{main_folder}/{folder_name}")
        if not os.path.exists(path):
            os.makedirs(path)
