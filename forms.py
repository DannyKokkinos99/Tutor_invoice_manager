# pylint: disable= C0116,C0114,C0115
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, FloatField
from wtforms.validators import InputRequired, Length, DataRequired, Email
from models import Student


class AddStudentForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(max=100)])
    surname = StringField("Surname", validators=[InputRequired(), Length(max=100)])
    parent = StringField("Parent", validators=[InputRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    address = StringField("Address", validators=[InputRequired(), Length(max=200)])
    phone_number = StringField(
        "Phone Number", validators=[InputRequired(), Length(max=20)]
    )
    price_per_hour = IntegerField("Price per Hour", validators=[InputRequired()])


class EditStudentForm(FlaskForm):
    student_id = SelectField("Select Student", coerce=int)
    name = StringField("Name", validators=[InputRequired(), Length(max=100)])
    surname = StringField("Surname", validators=[InputRequired(), Length(max=100)])
    parent = StringField("Parent", validators=[InputRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    address = StringField("Address", validators=[InputRequired(), Length(max=200)])
    phone_number = StringField(
        "Phone Number", validators=[InputRequired(), Length(max=20)]
    )
    price_per_hour = IntegerField("Price per Hour", validators=[InputRequired()])

    def set_choices(self):
        self.student_id.choices = [
            (student.id, f"{student.name} {student.surname}")
            for student in Student.query.all()
        ]


class RemoveStudentForm(FlaskForm):
    student_id = SelectField("Select Student", coerce=int)

    def set_choices(self):
        self.student_id.choices = [
            (student.id, f"{student.name} {student.surname}")
            for student in Student.query.all()
        ]


class CreateInvoiceForm(FlaskForm):
    student_id = SelectField("Select Student", coerce=int)
    hours_tutored = FloatField("Hours taught", validators=[InputRequired()])

    def set_choices(self):
        self.student_id.choices = [
            (student.id, f"{student.name} {student.surname}")
            for student in Student.query.all()
        ]
