from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_mail import Message
from flask_mail import Message
import random
import mysql.connector
from datetime import datetime, timedelta


auth = Blueprint("auth", __name__)

# MySQL connection (you can also move this to models/__init__.py)
conn = mysql.connector.connect( host="sql12.freesqldatabase.com", user="sql12800646", password="cK7VmCEWry", database="sql12800646")

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
        role = request.form['role']

        #checking if the user exists in the database or not
        cursor.execute('select email from login_data where email=%s',(email,))
        x = cursor.fetchone()
        try:
            cursor.execute('select is_verified from login_data where email=%s',(email,))
            y = cursor.fetchone()
        except:
            pass

        if x:
            if y['is_verified'] == 0:
                cursor.execute("delete from login_data where email=%s",(x['email'],))
                flash('There was some problem in backend. Please try again.')
            else:
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
            cursor.execute("INSERT INTO login_data (username, email, password, role, otp, otp_created_at, is_verified) VALUES (%s,%s, %s, %s, %s, %s, %s)",(username,email, password, role, otp, now, 0))
            conn.commit()

            session['user_email'] = email
            return redirect(url_for('auth.verify'))

    return render_template('auth/signup.html')



# LOGIN ROUTE
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # check if user exists
        cursor.execute("SELECT * FROM login_data WHERE email=%s AND password=%s AND role=%s", (email, password, role))
        user = cursor.fetchone()
        
        print(user)
        if user:
            if user['is_verified'] == 1:
                session['user_email'] = user['email']  # store login session
                flash("Login successful!", "success")
                
                # Correct redirection logic
                if user['role'] == 'alumni' or user['role'] == 'student':
                    return redirect(url_for('auth.alumni_student_dashboard'))
                elif user['role'] == 'administrator':
                    return redirect(url_for('auth.administrator_dashboard'))
                else:
                    flash('Something wrong. Try Again.', 'warning')
                    return redirect(url_for('auth.signup'))
            else:
                cursor.execute("delete from login_data where email=%s", (user['email'],))
                flash("Please signin and verify your account.", "warning")
                return redirect(url_for('auth.signup'))
        else:
            flash("Invalid email, role or password.", "danger")
            # Return the template so the user can try again
            return render_template('auth/login.html')

    # This handles the initial GET request to display the login form
    return render_template('auth/login.html')




# constants
OTP_EXPIRY = 60            # seconds
RESEND_INTERVAL = 60        # seconds between resends
STALE_ACCOUNT_SECONDS = 24*3600  # delete unverified accounts older than 24 hours


#---------------Deleting the unverified accounts----------------
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



#logout route
@auth.route('/logout')
def logout():
    session.pop('user_email', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('auth.login'))


#dashboard route
@auth.route('/alumni_student_dashboard')
def alumni_student_dashboard():
    if 'user_email' not in session:   # prevent direct access
        flash("Please login first!", "warning")
        return redirect(url_for('auth.login'))
    return render_template('auth/alumni_student_dashboard.html', email=session['user_email'])


@auth.route('/alumni_student_profile', methods=['POST', 'GET'])
def alumni_student_profile():
    user_email = session.get('user_email')
    
    # Fetch existing data for the user
    cursor.execute('SELECT * FROM student_data WHERE email = %s', (user_email,))
    existing_data = cursor.fetchone()

    if request.method == 'POST':
        # Get form data
        form_data = {
            'name': request.form.get('name'),
            'photo': request.form.get('photo'),  # Note: This is for a text field, for file uploads you need request.files
            'coll_univ': request.form.get('college'),
            'branch': request.form.get('branch'),
            'passing_year': request.form.get('passingyear'),
            'university_roll_no': request.form.get('rollno'),
            'email_id': request.form.get('email_id'),
            'cgpa': request.form.get('cgpa'),
            'status': request.form.get('status'),
            'curr_role': request.form.get('curr_role'),
            'current_company': request.form.get('company')
        }
        
        # Prepare the data to be inserted/updated
        data_to_save = {}
        for key, value in form_data.items():
            # If the user has provided a new value, use it.
            # Otherwise, use the existing value from the database.
            # If no existing data and no new value, it will be None.
            data_to_save[key] = value if value else (existing_data[key] if existing_data and key in existing_data else None)

        if existing_data:
            # Update the existing record
            query = """
            UPDATE student_data
            SET name = %s, photo = %s, coll_univ = %s, branch = %s, passing_year = %s, university_roll_no = %s,
                email_id = %s, cgpa = %s, status = %s, curr_role = %s, current_company = %s
            WHERE email = %s
            """
            cursor.execute(query, (
                data_to_save['name'], data_to_save['photo'], data_to_save['coll_univ'], data_to_save['branch'], 
                data_to_save['passing_year'], data_to_save['university_roll_no'], data_to_save['email_id'], 
                data_to_save['cgpa'], data_to_save['status'], data_to_save['curr_role'], data_to_save['current_company'],
                user_email
            ))
        else:
            # Insert a new record
            query = """
            INSERT INTO student_data(
                name, photo, coll_univ, branch, passing_year, university_roll_no, email_id, cgpa, status, curr_role, current_company
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                data_to_save['name'], data_to_save['photo'], data_to_save['coll_univ'], data_to_save['branch'], 
                data_to_save['passing_year'], data_to_save['university_roll_no'], data_to_save['email_id'], 
                data_to_save['cgpa'], data_to_save['status'], data_to_save['curr_role'], data_to_save['current_company']
            ))

        # You should commit the transaction after a change.
        # This will depend on your database connection library (e.g., `conn.commit()`).
        # Assuming `conn` is your database connection object.
        # conn.commit() 
    
    # Pass existing data to the template for pre-filling the form fields
    return render_template('auth/alumni_student_profile.html', student_data=existing_data)

@auth.route('/events')
def events():
    return render_template('auth/events.html')