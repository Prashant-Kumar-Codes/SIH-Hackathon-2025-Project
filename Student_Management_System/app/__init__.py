from flask import Flask
from flask_mail import Mail

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.secret_key = "myappsecretkey"

# MySQL connection
    app.config['MYSQL_HOST'] = "localhost"
    app.config['MYSQL_USER'] = "root"
    app.config['MYSQL_PASSWORD'] = "admin123"
    app.config['MYSQL_DATABASE'] = "Student_Management_System_Database"

# Mail_Setup: Brevo SMTP config
    app.config['MAIL_SERVER'] = 'smtp-relay.brevo.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = '969fcc001@smtp-brevo.com'
    app.config['MAIL_PASSWORD'] = '6za2MbPwpVrB04ch'
    app.config['MAIL_DEFAULT_SENDER'] = 'pkthisisfor1234@gmail.com'
    mail.init_app(app)

# Import routes
    from app.routes.auth import auth
    app.register_blueprint(auth)

    return app
