# app.py - UPDATED IMPORTS
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from wtforms import StringField, SubmitField, SelectField, DateField, TextAreaField, IntegerField, PasswordField, TelField, EmailField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Optional, Email, Length, NumberRange, EqualTo
from flask_mail import Mail, Message
import os

class EventSearchForm(FlaskForm):
    query = StringField('Search Events', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('social', 'Social Event')
    ], validators=[Optional()])
    date_from = DateField('From Date', validators=[Optional()])
    date_to = DateField('To Date', validators=[Optional()])
    venue = StringField('Venue', validators=[Optional()])
    sort_by = SelectField('Sort By', choices=[
        ('date_asc', 'Date (Earliest First)'),
        ('date_desc', 'Date (Latest First)'),
        ('title_asc', 'Title (A-Z)'),
        ('title_desc', 'Title (Z-A)')
    ], default='date_asc')
    submit = SubmitField('Search')

# Also define the other forms you need:
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=80)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = TelField('Phone Number', validators=[Optional()])
    whatsapp = TelField('WhatsApp Number', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])  # ADD THIS LINE
    role = SelectField('Role', choices=[
        ('attendee', 'Attendee'),
        ('organizer', 'Organizer')
    ], default='attendee')
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('conference', 'Conference'), ('workshop', 'Workshop'), 
        ('seminar', 'Seminar'), ('social', 'Social Event')
    ])
    tags = StringField('Tags', validators=[Optional()])
    date = StringField('Date', validators=[DataRequired()])
    time = StringField('Time', validators=[DataRequired()])
    venue = StringField('Venue', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[Optional()], default=0)
    contact_phone = TelField('Contact Phone', validators=[Optional()])
    contact_whatsapp = TelField('Contact WhatsApp', validators=[Optional()])
    contact_email = EmailField('Contact Email', validators=[Optional(), Email()])
    submit = SubmitField('Create Event')

# Create Flask application instance
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///events.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@eventmaster.com')

mail = Mail(app)

# Initialize login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='attendee')
    phone = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

# In app.py - UPDATE THE EVENT MODEL (replace the existing one)
# Enhanced Event model with tags
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(500))  # Comma-separated tags
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    venue = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, default=0)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contact_phone = db.Column(db.String(20))
    contact_whatsapp = db.Column(db.String(20))
    contact_email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    organizer = db.relationship('User', backref='organized_events')
    
    def get_tags_list(self):
        """Convert comma-separated tags to list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def set_tags(self, tags_list):
        """Convert list of tags to comma-separated string"""
        self.tags = ','.join([tag.strip() for tag in tags_list])
    
    def __repr__(self):
        return f'<Event {self.title}>'

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    attendee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='confirmed')
    
    # Relationships
    event = db.relationship('Event', backref='event_registrations')
    attendee = db.relationship('User', backref='user_registrations')
    
    def __repr__(self):
        return f'<Registration {self.attendee_id} for {self.event_id}>'

# This function is required by Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create all database tables
with app.app_context():
    db.create_all()

# Email utility functions
def send_email(to, subject, template):
    try:
        msg = Message(
            subject=subject,
            recipients=[to],
            html=template,
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_registration_confirmation(user, event):
    subject = f"Registration Confirmed: {event.title}"
    template = f"""
    <h2>Registration Confirmed!</h2>
    <p>Hello {user.username},</p>
    <p>You have successfully registered for the event:</p>
    
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 5px; margin: 1rem 0;">
        <h3>{event.title}</h3>
        <p><strong>Date:</strong> {event.date}</p>
        <p><strong>Time:</strong> {event.time}</p>
        <p><strong>Venue:</strong> {event.venue}</p>
        <p><strong>Organizer:</strong> {event.organizer.username}</p>
    </div>
    
    <p>We look forward to seeing you at the event!</p>
    
    <hr>
    <p><small>If you have any questions, please contact the organizer:</small></p>
    <p><small>Email: {event.contact_email or event.organizer.email}</small></p>
    <p><small>Phone: {event.contact_phone or event.organizer.phone}</small></p>
    """
    
    return send_email(user.email, subject, template)

def send_event_created_notification(organizer, event):
    subject = f"Event Created: {event.title}"
    template = f"""
    <h2>Event Created Successfully!</h2>
    <p>Hello {organizer.username},</p>
    <p>Your event has been created and is now live on our platform:</p>
    
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 5px; margin: 1rem 0;">
        <h3>{event.title}</h3>
        <p><strong>Date:</strong> {event.date}</p>
        <p><strong>Time:</strong> {event.time}</p>
        <p><strong>Venue:</strong> {event.venue}</p>
        <p><strong>Category:</strong> {event.category.title()}</p>
    </div>
    
    <p>You can manage your event from your dashboard.</p>
    """
    
    return send_email(organizer.email, subject, template)

# Routes
@app.route('/')
def home():
    events_count = Event.query.count()
    users_count = User.query.count()
    organizers_count = User.query.filter_by(role='organizer').count()
    recent_events = Event.query.order_by(Event.created_at.desc()).limit(3).all()
    
    return render_template('index.html', 
                         events=recent_events,
                         events_count=events_count,
                         users_count=users_count,
                         organizers_count=organizers_count)

@app.route('/about')
def about():
    return render_template('about.html')
    
    # Enhanced search route in app.py
@app.route('/events/search')
def search_events():
    form = EventSearchForm()
    
    # Get search parameters
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    venue = request.args.get('venue', '')
    sort_by = request.args.get('sort_by', 'date_asc')
    
    # Build query
    events_query = Event.query
    
    # Text search
    if query:
        events_query = events_query.filter(
            db.or_(
                Event.title.ilike(f'%{query}%'),
                Event.description.ilike(f'%{query}%'),
                Event.venue.ilike(f'%{query}%')
            )
        )
    
    # Category filter
    if category:
        events_query = events_query.filter(Event.category == category)
    
    # Venue filter
    if venue:
        events_query = events_query.filter(Event.venue.ilike(f'%{venue}%'))
    
    # Date range filter
    if date_from:
        events_query = events_query.filter(Event.date >= date_from)
    if date_to:
        events_query = events_query.filter(Event.date <= date_to)
    
    # Sorting
    if sort_by == 'date_asc':
        events_query = events_query.order_by(Event.date.asc())
    elif sort_by == 'date_desc':
        events_query = events_query.order_by(Event.date.desc())
    elif sort_by == 'title_asc':
        events_query = events_query.order_by(Event.title.asc())
    elif sort_by == 'title_desc':
        events_query = events_query.order_by(Event.title.desc())
    elif sort_by == 'created_desc':
        events_query = events_query.order_by(Event.created_at.desc())
    
    events = events_query.all()
    
    return render_template('events.html', 
                         events=events, 
                         form=form,
                         search_params=search_params)

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            phone=form.phone.data,
            whatsapp=form.whatsapp.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        
        # Add to database
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('login.html', form=form)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

# Protected route example
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# Event routes
@app.route('/events')
def events():
    form = EventSearchForm()
    events_list = Event.query.order_by(Event.date.asc()).all()
    
    # Pass empty search_params for the main events page
    return render_template('events.html', 
                         events=events_list, 
                         form=form, 
                         search_params={})

@app.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if current_user.role != 'organizer':
        flash('Only organizers can create events.', 'error')
        return redirect(url_for('events'))
    
    form = EventForm()
    
    if form.validate_on_submit():
        try:
            # Create the event object
            event = Event(
                title=form.title.data,
                description=form.description.data,
                category=form.category.data,
                date=form.date.data,
                time=form.time.data,
                venue=form.venue.data,
                capacity=form.capacity.data or 0,
                organizer_id=current_user.id,
                contact_phone=form.contact_phone.data or current_user.phone,
                contact_whatsapp=form.contact_whatsapp.data or current_user.whatsapp,
                contact_email=form.contact_email.data or current_user.email
            )
            
            # Handle tags
            if form.tags.data:
                tags_list = [tag.strip() for tag in form.tags.data.split(',')]
                event.set_tags(tags_list)
            
            # Save to database
            db.session.add(event)
            db.session.commit()
            
            # Send email notification
            try:
                send_event_created_notification(current_user, event)
            except Exception as email_error:
                print(f"Email failed but event created: {email_error}")
            
            flash('Event created successfully!', 'success')
            return redirect(url_for('event_detail', event_id=event.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating event: {str(e)}', 'error')
            return render_template('create_event.html', form=form)
    
    return render_template('create_event.html', form=form)

@app.route('/events/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if current user is registered
    is_registered = False
    if current_user.is_authenticated:
        registration = Registration.query.filter_by(
            event_id=event_id, 
            attendee_id=current_user.id
        ).first()
        is_registered = registration is not None
    
    # Count current registrations
    current_registrations = Registration.query.filter_by(event_id=event_id).count()
    
    return render_template('event_detail.html', 
                         event=event, 
                         is_registered=is_registered,
                         current_registrations=current_registrations)
                         
@app.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if user owns the event
    if event.organizer_id != current_user.id:
        flash('You can only edit your own events.', 'error')
        return redirect(url_for('event_detail', event_id=event_id))
    
    form = EventEditForm()
    
    if form.validate_on_submit():
        try:
            event.title = form.title.data
            event.description = form.description.data
            event.category = form.category.data
            event.date = form.date.data
            event.time = form.time.data
            event.venue = form.venue.data
            event.capacity = form.capacity.data or 0
            
            # Handle tags
            if form.tags.data:
                tags_list = [tag.strip() for tag in form.tags.data.split(',')]
                event.set_tags(tags_list)
            else:
                event.tags = None
            
            event.contact_phone = form.contact_phone.data
            event.contact_whatsapp = form.contact_whatsapp.data
            event.contact_email = form.contact_email.data
            
            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('event_detail', event_id=event.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating event: {str(e)}', 'error')
    
    # Pre-populate form with existing data
    elif request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.category.data = event.category
        form.date.data = event.date
        form.time.data = event.time
        form.venue.data = event.venue
        form.capacity.data = event.capacity
        form.contact_phone.data = event.contact_phone
        form.contact_whatsapp.data = event.contact_whatsapp
        form.contact_email.data = event.contact_email
        form.tags.data = event.tags
    
    return render_template('edit_event.html', form=form, event=event)
    
@app.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if event.organizer_id != current_user.id:
        flash('You can only delete your own events.', 'error')
        return redirect(url_for('event_detail', event_id=event_id))
    
    # Delete associated registrations first
    Registration.query.filter_by(event_id=event_id).delete()
    db.session.delete(event)
    db.session.commit()
    
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('events'))

@app.route('/events/<int:event_id>/register')
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if current_user.id == event.organizer_id:
        flash('You are the organizer of this event - no need to register!', 'warning')
        return redirect(url_for('event_detail', event_id=event_id))
        
    existing_registration = Registration.query.filter_by(
        event_id=event_id, 
        attendee_id=current_user.id
    ).first()
    
    if existing_registration:
        flash('You are already registered for this event.', 'info')
        return redirect(url_for('event_detail', event_id=event_id))
    
    current_registrations = Registration.query.filter_by(event_id=event_id).count()
    if event.capacity > 0 and current_registrations >= event.capacity:
        flash('Sorry, this event is full!', 'error')
        return redirect(url_for('event_detail', event_id=event_id))
    
    registration = Registration(event_id=event_id, attendee_id=current_user.id)
    db.session.add(registration)
    db.session.commit()
    
    # Send registration confirmation email
    send_registration_confirmation(current_user, event)
    
    flash('Successfully registered for the event! Check your email for confirmation.', 'success')
    return redirect(url_for('event_detail', event_id=event_id))

# Route to view event attendees
@app.route('/events/<int:event_id>/attendees')
@login_required
def event_attendees(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if user owns the event
    if event.organizer_id != current_user.id:
        flash('You can only view attendees for your own events.', 'error')
        return redirect(url_for('event_detail', event_id=event_id))
    
    # Get all registrations for this event
    registrations = Registration.query.filter_by(event_id=event_id).all()
    
    return render_template('event_attendees.html', 
                         event=event, 
                         registrations=registrations)

# Route to remove an attendee
@app.route('/events/<int:event_id>/remove_attendee/<int:attendee_id>', methods=['POST'])
@login_required
def remove_attendee(event_id, attendee_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if user owns the event
    if event.organizer_id != current_user.id:
        flash('You can only manage attendees for your own events.', 'error')
        return redirect(url_for('event_detail', event_id=event_id))
    
    # Find and remove the registration
    registration = Registration.query.filter_by(
        event_id=event_id, 
        attendee_id=attendee_id
    ).first()
    
    if registration:
        db.session.delete(registration)
        db.session.commit()
        flash('Attendee removed successfully.', 'success')
    else:
        flash('Attendee not found.', 'error')
    
    return redirect(url_for('event_attendees', event_id=event_id))
    
# Route for event analytics
@app.route('/events/<int:event_id>/analytics')
@login_required
def event_analytics(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if user owns the event
    if event.organizer_id != current_user.id:
        flash('You can only view analytics for your own events.', 'error')
        return redirect(url_for('event_detail', event_id=event_id))
    
    # Calculate analytics
    total_registrations = Registration.query.filter_by(event_id=event_id).count()
    
    # Registration trend (last 7 days)
    from datetime import datetime, timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    recent_registrations = Registration.query.filter(
        Registration.event_id == event_id,
        Registration.registered_at >= seven_days_ago
    ).count()
    
    # Capacity utilization
    capacity_utilization = 0
    if event.capacity > 0:
        capacity_utilization = (total_registrations / event.capacity) * 100
    
    # Get attendee list for details
    registrations = Registration.query.filter_by(event_id=event_id).all()
    
    return render_template('event_analytics.html',
                         event=event,
                         total_registrations=total_registrations,
                         recent_registrations=recent_registrations,
                         capacity_utilization=capacity_utilization,
                         registrations=registrations)    

@app.route('/my-events')
@login_required
def my_events():
    if current_user.role == 'organizer':
        # Show events created by organizer
        events = Event.query.filter_by(organizer_id=current_user.id).all()
        return render_template('my_events.html', events=events, user_role='organizer')
    else:
        # Show events attended by user
        registrations = Registration.query.filter_by(attendee_id=current_user.id).all()
        events = [reg.event for reg in registrations]
        return render_template('my_events.html', events=events, user_role='attendee')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)