from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mail
from flask_mail import Message
import random
import mysql.connector
from datetime import datetime

auth = Blueprint("auth", __name__)

# MySQL connection (you can also move this to models/__init__.py)
conn = mysql.connector.connect( host="localhost", user="root", password="admin123", database="student_management_system_database")

cursor = conn.cursor(dictionary=True)


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


@auth.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        email = session.get('user_email')

        if not email:
            flash("Session expired. Please signup again.", "danger")
            return redirect(url_for('auth.signup'))

        # Get user
        cursor.execute("SELECT * FROM login_data WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user:
            otp_created_at = user['otp_created_at']
            # check expiry (60 sec)
            if (datetime.now() - otp_created_at).seconds > 60:
                flash("OTP expired. Please request a new one.", "warning")
                return redirect(url_for('auth.resend_otp'))

            if user['otp'] == entered_otp:
                cursor.execute("UPDATE login_data SET is_verified = %s, otp = NULL WHERE email = %s", (True, email))
                conn.commit()
                flash("Account verified successfully! Please login.", "success")
                return redirect(url_for('auth.login'))
            else:
                flash("Invalid OTP. Please try again.", "danger")
        else:
            flash("No user found. Please signup again.", "danger")
            return redirect(url_for('auth.signup'))

    # pass remaining time to template for countdown
    email = session.get('user_email')
    remaining = 0
    if email:
        cursor.execute("SELECT otp_created_at FROM login_data WHERE email=%s", (email,))
        data = cursor.fetchone()
        if data:
            elapsed = (datetime.now() - data['otp_created_at']).seconds
            remaining = max(0, 60 - elapsed)

    return render_template('auth/verify.html', remaining=remaining)





# RESEND_OTP ROUTE
@auth.route('/resend_otp', methods=['POST'])
def resend_otp():
    email = session.get('user_email')
    if not email:
        flash("Session expired. Please signup again.", "danger")
        return redirect(url_for('auth.signup'))

    # Check time since last OTP
    cursor.execute("SELECT otp_created_at FROM login_data WHERE email=%s", (email,))
    data = cursor.fetchone()
    if data and (datetime.now() - data['otp_created_at']).seconds < 60:
        flash("You can request a new OTP after 1 minute.", "warning")
        return redirect(url_for('auth.verify'))

    # Generate new OTP
    otp = str(random.randint(100000, 999999))
    otp_created_at = datetime.now()
    cursor.execute("UPDATE login_data SET otp=%s, otp_created_at=%s WHERE email=%s", (otp, otp_created_at, email))
    conn.commit()

    # Send mail
    msg = Message('Your New OTP Code', sender='pkthisisfor1234@gmail.com', recipients=[email])
    msg.body = f'Your new OTP is {otp}'
    mail.send(msg)

    flash("OTP resent successfully!", "success")
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
                flash("Please verify your account first.", "warning")
                return redirect(url_for('auth.verify'))
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
