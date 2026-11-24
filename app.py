import csv
import os
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request,
    redirect, url_for, send_from_directory,
    flash, session, send_file, abort
)

from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from authlib.integrations.flask_client import OAuth
from flask_talisman import Talisman
from dotenv import load_dotenv

load_dotenv()

# =========================
# APP SETUP
# =========================

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")

# Talisman: security headers. Local (http) pe HTTPS force nahi karte,
# aur CSP me CDN (Bootstrap, FontAwesome, Google Fonts) allow karte hain
# warna icons / fonts / styles block ho jate hain.
FORCE_HTTPS = os.getenv("FORCE_HTTPS", "false").lower() == "true"

CSP = {
    'default-src': ["'self'"],
    'style-src': [
        "'self'", "'unsafe-inline'",
        "https://cdn.jsdelivr.net",
        "https://cdnjs.cloudflare.com",
        "https://fonts.googleapis.com",
    ],
    'script-src': [
        "'self'", "'unsafe-inline'",
        "https://cdn.jsdelivr.net",
        "https://cdnjs.cloudflare.com",
    ],
    'font-src': [
        "'self'", "data:",
        "https://fonts.gstatic.com",
        "https://cdnjs.cloudflare.com",
        "https://cdn.jsdelivr.net",
    ],
    'img-src': ["'self'", "data:", "https:"],
    'connect-src': ["'self'"],
    'object-src': ["'self'"],
    'frame-src': ["'self'"],
}

Talisman(
    app,
    force_https=FORCE_HTTPS,
    strict_transport_security=FORCE_HTTPS,
    session_cookie_secure=FORCE_HTTPS,
    content_security_policy=CSP
)

app.config['SESSION_COOKIE_SECURE'] = FORCE_HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

csrf = CSRFProtect(app)

limiter = Limiter(
    key_func=get_remote_address,
    app=app
)

# =========================
# MAIL
# =========================

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
# Gmail App Password spaces ke saath dikhta hai (abcd efgh ...), spaces hata do
app.config['MAIL_PASSWORD'] = (os.getenv('MAIL_PASSWORD') or '').replace(' ', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail = Mail(app)

# =========================
# IMAGE FOLDER
# =========================

IMAGES_DIR = os.path.join(
    os.path.dirname(__file__),
    'images'
)

# =========================
# RESUME FILE
# =========================

def find_resume():
    """
    Resume PDF dhundta hai. Pehle known naam, phir project folder / static
    folder ki koi bhi .pdf (naam alag ho ya (1) lag gaya ho tab bhi chalega).
    """
    base = os.path.dirname(os.path.abspath(__file__))
    folders = [base, os.path.join(base, 'static')]
    known = ['Neha_Bharule.pdf', 'Neha_B- Expert AIML Engineer.pdf']

    for folder in folders:
        for name in known:
            path = os.path.join(folder, name)
            if os.path.isfile(path):
                return path

    for folder in folders:
        if not os.path.isdir(folder):
            continue
        pdfs = sorted(
            f for f in os.listdir(folder) if f.lower().endswith('.pdf')
        )
        if pdfs:
            return os.path.join(folder, pdfs[0])

    print("Resume search folder:", base)
    print("Files there:", os.listdir(base))
    abort(404, description=(
        "Resume PDF nahi mili. PDF ko is folder me rakho: " + base
    ))

# =========================
# PROJECT DATA
# =========================

project_data = [
    {
        'id': 1,
        'title': 'Railway Navigation System',
        'desc': 'Real-time navigation system',
        'image': 'railway.jpg',
        'github': 'https://github.com/nehabharude07/Railway-Navigation-System',
        'demo': 'https://railway-navigation.vercel.app'
    },
    {
        'id': 2,
        'title': 'Crowd Management System',
        'desc': 'YOLOv8 based system',
        'image': 'crowd.jpg',
        'github': 'https://github.com/nehabharude07/Crowd-Management-System',
        'demo': 'https://crowd-management.vercel.app'
    },
    {
        'id': 3,
        'title': 'AQI Prediction',
        'desc': 'ML based AQI prediction',
        'image': 'aqi.jpg',
        'github': 'https://github.com/nehabharude07/AQI_Prediction_System',
        'demo': 'https://aqi-prediction.vercel.app'
    }
]

# =========================
# LOGIN REQUIRED
# =========================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if 'user' not in session:
            session['next'] = request.path
            return redirect(
                url_for('login_google')
            )

        return f(*args, **kwargs)

    return decorated_function

# =========================
# ROUTES
# =========================

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def aboutme():
    return render_template(
        ['aboutme.html', 'about.html', 'about_me.html']
    )


@app.route('/projects')
def projects_page():
    return render_template(
        'projects.html',
        projects=project_data
    )


@app.route('/resume')
@login_required
def resume():
    # Resume PDF ko browser me inline dikhata hai
    return send_file(
        find_resume(),
        mimetype='application/pdf',
        as_attachment=False
    )


@app.route('/info')
def info():
    return render_template('info.html')


@app.route('/login')
def login():
    # If already signed in, no need to show the login page again
    if 'user' in session:
        return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/contact', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def contact():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        os.makedirs(
            'data',
            exist_ok=True
        )

        with open(
            'data/contacts.csv',
            'a',
            newline='',
            encoding='utf-8'
        ) as f:

            writer = csv.writer(f)

            writer.writerow([
                name,
                email,
                message,
                datetime.now()
            ])

        mail_ok = False

        try:

            if (
                not app.config['MAIL_USERNAME']
                or not app.config['MAIL_PASSWORD']
                or 'your-' in app.config['MAIL_USERNAME']
                or 'your-' in app.config['MAIL_PASSWORD']
            ):
                raise RuntimeError(
                    "MAIL_USERNAME / MAIL_PASSWORD .env me set nahi hai"
                )

            msg = Message(
                subject=f"Portfolio Contact: {name}",
                sender=("Portfolio Contact", app.config['MAIL_USERNAME']),
                recipients=[app.config['MAIL_USERNAME']],
                reply_to=email
            )

            msg.body = f"""
Name: {name}

Email: {email}

Message:
{message}
"""

            mail.send(msg)
            mail_ok = True

        except Exception as e:
            # Terminal me poora error dikhega
            app.logger.exception("MAIL ERROR: %s", e)

        if mail_ok:
            flash(
                "Message sent successfully!",
                "success"
            )
        else:
            flash(
                "Message Can't Sent"
            )

        return redirect(
            url_for('contact')
        )

    return render_template(
        'contact.html'
    )


@app.route('/download-resume')
@login_required
def download_resume():

    return send_file(
        find_resume(),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='Neha_Bharule_Resume.pdf'
    )


@app.route('/media/<filename>')
def media(filename):

    return send_from_directory(
        IMAGES_DIR,
        filename
    )

# =========================
# GOOGLE OAUTH
# =========================

oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.getenv(
        "GOOGLE_CLIENT_ID"
    ),
    client_secret=os.getenv(
        "GOOGLE_CLIENT_SECRET"
    ),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@app.route('/login/google')
def login_google():

    redirect_uri = url_for(
        'authorize_google',
        _external=True
    )

    return google.authorize_redirect(
        redirect_uri
    )


@app.route('/authorize/google')
def authorize_google():

    token = google.authorize_access_token()

    user_info = token.get(
        'userinfo'
    )

    session['user'] = {
        'name': user_info.get(
            'name'
        ),
        'email': user_info.get(
            'email'
        ),
        'picture': user_info.get(
            'picture'
        )
    }

    flash(
        "Login successful",
        "success"
    )

    next_url = session.pop('next', None)

    # sirf internal path pe redirect (open-redirect se bachne ke liye)
    if next_url and next_url.startswith('/') and not next_url.startswith('//'):
        return redirect(next_url)

    return redirect(
        url_for('home')
    )


@app.route('/logout')
def logout():

    session.clear()

    flash(
        "Logged out successfully",
        "success"
    )

    return redirect(
        url_for('home')
    )

# =========================
# RUN
# =========================

if __name__ == '__main__':
    app.run(
        debug=True,
        port=5555
    )