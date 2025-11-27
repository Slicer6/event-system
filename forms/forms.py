# forms/forms.py - UPDATED WITH EVENT FORMS
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange
from your_forms_module import EventSearchForm
from datetime import datetime

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number')
    whatsapp = StringField('WhatsApp Number')
    role = SelectField('Role', choices=[
        ('attendee', 'Event Attendee'),
        ('organizer', 'Event Organizer')
    ], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Event Description', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('wedding', 'Wedding'),
        ('corporate', 'Corporate Event'),
        ('music', 'Music Festival'),
        ('community', 'Community Program'),
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    tags = StringField('Tags', validators=[Length(max=500)])
    date = StringField('Event Date (YYYY-MM-DD)', validators=[DataRequired()])
    time = StringField('Event Time (HH:MM)', validators=[DataRequired()])
    venue = StringField('Venue', validators=[DataRequired(), Length(max=200)])
    capacity = IntegerField('Capacity (0 for unlimited)', validators=[NumberRange(min=0)])
    contact_phone = StringField('Contact Phone')
    contact_whatsapp = StringField('Contact WhatsApp')
    contact_email = StringField('Contact Email')
    submit = SubmitField('Create Event')
    
class EventSearchForm(FlaskForm):
     search_query = StringField('Search Events', validators=[Optional()])
    submit = SubmitField('Search')
        ('', 'All Categories'),
        ('wedding', 'Wedding'),
        ('corporate', 'Corporate Event'),
        ('music', 'Music Festival'),
        ('community', 'Community Program'),
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('other', 'Other')
    ])
    date_from = StringField('From Date')
    date_to = StringField('To Date')
    venue = StringField('Venue')
    sort_by = SelectField('Sort By', choices=[
        ('date_asc', 'Date (Earliest First)'),
        ('date_desc', 'Date (Latest First)'),
        ('title_asc', 'Title (A-Z)'),
        ('title_desc', 'Title (Z-A)'),
        ('created_desc', 'Newest First')
    ], default='date_asc')
    submit = SubmitField('Search')
    
class EventEditForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Event Description', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('wedding', 'Wedding'),
        ('corporate', 'Corporate Event'),
        ('music', 'Music Festival'),
        ('community', 'Community Program'),
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    tags = StringField('Tags', validators=[Length(max=500)])  
    date = StringField('Event Date (YYYY-MM-DD)', validators=[DataRequired()])
    time = StringField('Event Time (HH:MM)', validators=[DataRequired()])
    venue = StringField('Venue', validators=[DataRequired(), Length(max=200)])
    capacity = IntegerField('Capacity (0 for unlimited)', validators=[NumberRange(min=0)])
    contact_phone = StringField('Contact Phone')
    contact_whatsapp = StringField('Contact WhatsApp')
    contact_email = StringField('Contact Email')
    submit = SubmitField('Update Event')    