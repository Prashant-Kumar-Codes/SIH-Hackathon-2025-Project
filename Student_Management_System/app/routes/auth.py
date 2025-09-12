from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mail
from flask_mail import Message
import random
import mysql.connector
from datetime import datetime, timedelta


auth = Blueprint("auth", __name__)

# MySQL connection (you can also move this to models/__init__.py)
conn = mysql.connector.connect( host="localhost", user="root", password="admin123", database="student_management_system_database")

cursor = conn.cursor(dictionary=True)

#landing route
@auth.route('/',methods=['GET'])
def landing_page():
    return render_template("auth/landing_page.html")

# signup route
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        #checking if the user exists in the database or not
        cursor.execute('select email from login_data where email=%s',(email,))
        x = cursor.fetchone()
        if x:
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for('auth.login'))
        else:
            otp = str(random.randint(100000, 999999))
            # Send OTP
            msg = Message('Your OTP Verification Code', sender='pkthisisfor1234@gmail.com', recipients=[email])
            msg.body = f'Your OTP is {otp}'
            mail.send(msg)
            now = datetime.utcnow()   # or datetime.now() if you want local time
            # Insert into MySQL
            cursor.execute("INSERT INTO login_data (username, email, password, otp, otp_created_at, is_verified) VALUES (%s,%s, %s, %s, %s, %s)",(username,email, password, otp, now, False))
            conn.commit()

            session['user_email'] = email
            return redirect(url_for('auth.verify'))

    return render_template('auth/signup.html')



# constants
OTP_EXPIRY = 60            # seconds
RESEND_INTERVAL = 60        # seconds between resends
STALE_ACCOUNT_SECONDS = 24*3600  # delete unverified accounts older than 24 hours

# helper: delete stale unverified accounts
def cleanup_stale_unverified():
    cutoff = datetime.now() - timedelta(seconds=STALE_ACCOUNT_SECONDS)
    try:
        cursor.execute(
            "DELETE FROM login_data WHERE is_verified=0 AND otp_created_at IS NOT NULL AND otp_created_at < %s",
            (cutoff,)
        )
        conn.commit()
    except Exception:
        # don't crash on cleanup errors; optional: log it
        pass

def parse_db_datetime(val):
    """Return a datetime from DB value (handles str or datetime)."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    # if string like "2025-09-10 20:40:55" or with microseconds
    try:
        return datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
    except Exception:
        try:
            return datetime.strptime(val.split('.')[0], "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None



# VERIFY route
@auth.route('/verify', methods=['GET', 'POST'])
def verify():
    email = session.get('user_email')
    if not email:
        flash("Session expired. Please sign up again.", "danger")
        ## Adding delete data:
        cleanup_stale_unverified()
        return redirect(url_for('auth.signup'))

    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        if not entered_otp:
            flash("Please enter the OTP.", "danger")
            ## Adding delete data:
            cleanup_stale_unverified()
            return redirect(url_for('auth.verify'))

        cursor.execute("SELECT * FROM login_data WHERE email=%s", (email,))
        user = cursor.fetchone()

        if not user or not user.get('otp') or not user.get('otp_created_at'):
            flash("Invalid OTP or session. Please request a new one.", "danger")
            return redirect(url_for('auth.resend_otp'))

        try:
            # Consistent UTC time for comparison
            otp_created_at = user['otp_created_at']
            if isinstance(otp_created_at, str):
                otp_created_at = datetime.strptime(otp_created_at, "%Y-%m-%d %H:%M:%S")

            expiry_time = otp_created_at + timedelta(seconds=60)

            if datetime.utcnow() > expiry_time:
                flash("OTP expired. Please request a new one.", "warning")
                return redirect(url_for('auth.verify'))

            if user['otp'] == entered_otp:
                cursor.execute(
                    "UPDATE login_data SET is_verified = %s, otp = NULL, otp_created_at = NULL WHERE email = %s",
                    (1, email)
                )
                conn.commit()
                flash("Account verified successfully! You can now log in.", "success")
                return redirect(url_for('auth.login'))
            else:
                flash("Invalid OTP. Please try again.", "danger")
                return redirect(url_for('auth.verify'))

        except Exception as e:
            flash("An error occurred. Please try again.", "danger")
            # Log the error for debugging: print(f"Error in verify: {e}")
            return redirect(url_for('auth.verify'))

    # GET request logic for the verify page
    remaining = 0
    try:
        cursor.execute("SELECT otp_created_at FROM login_data WHERE email=%s", (email,))
        data = cursor.fetchone()
        if data and data['otp_created_at']:
            otp_created_at = data['otp_created_at']
            if isinstance(otp_created_at, str):
                otp_created_at = datetime.strptime(otp_created_at, "%Y-%m-%d %H:%M:%S")

            expiry_time = otp_created_at + timedelta(seconds=60)
            remaining = max(0, int((expiry_time - datetime.utcnow()).total_seconds()))
    except Exception:
        remaining = 0
        ## Adding delete data:
        cleanup_stale_unverified()
        
    return render_template('auth/verify.html', remaining=remaining)

#----------------------------------------------------------------------------------------------------------------------

# RESEND_OTP ROUTE
@auth.route('/resend_otp', methods=['POST'])
def resend_otp():
    email = session.get('user_email')
    if not email:
        flash("Session expired. Please sign up again.", "danger")
        return redirect(url_for('auth.signup'))

    cursor.execute("SELECT otp_created_at FROM login_data WHERE email=%s", (email,))
    data = cursor.fetchone()
    
    # Check if a new OTP can be sent
    if data and data['otp_created_at']:
        otp_created_at = data['otp_created_at']
        if isinstance(otp_created_at, str):
            otp_created_at = datetime.strptime(otp_created_at, "%Y-%m-%d %H:%M:%S")
        
        # Check if the cool-down period has passed
        resend_time = otp_created_at + timedelta(seconds=60) # Use 60s for consistency
        if datetime.utcnow() < resend_time:
            flash("Please wait until the current OTP expires before requesting a new one.", "warning")
            return redirect(url_for('auth.verify'))

    # Generate and save new OTP
    otp = str(random.randint(100000, 999999))
    otp_created_at = datetime.utcnow()
    try:
        cursor.execute("UPDATE login_data SET otp=%s, otp_created_at=%s WHERE email=%s",
                       (otp, otp_created_at, email))
        conn.commit()

        msg = Message('Your New OTP Code', sender='pkthisisfor1234@gmail.com', recipients=[email])
        msg.body = f'Your new OTP is {otp}'
        mail.send(msg)

        flash("New OTP sent successfully!", "success")
    except Exception as e:
        flash("Failed to send new OTP. Please try again.", "danger")
        # Log the error for debugging: print(f"Error in resend_otp: {e}")
        
    return redirect(url_for('auth.verify'))






# LOGIN ROUTE
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # check if user exists
        cursor.execute("SELECT * FROM login_data WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()

        if user:
            if user['is_verified']:
                session['user_email'] = user['email']  # store login session
                flash("Login successful!", "success")
                return redirect(url_for('auth.dashboard'))
            else:
                tem = user['email']
                cursor.execute("DELETE FROM login_data WHERE email=%s",(tem,))
                flash("Please SignIn and verify your account first.", "warning")
                return redirect(url_for('auth.signup'))
        else:
            flash("Invalid email or password.", "danger")

    return render_template('auth/login.html')

#logout route
@auth.route('/logout')
def logout():
    session.pop('user_email', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('auth.login'))


#dashboard route
@auth.route('/dashboard')
def dashboard():
    if 'user_email' not in session:   # prevent direct access
        flash("Please login first!", "warning")
        return redirect(url_for('auth.login'))
    return render_template('auth/dashboard.html', email=session['user_email'])
