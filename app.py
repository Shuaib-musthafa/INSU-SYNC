from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import random
import smtplib
import ssl
import joblib
import pandas as pd
import xgboost as xgb
import pickle
import numpy as np
import os
from rule import Rule
import google.generativeai as genai
import io
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
import re
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import tempfile

rule = Rule()

# =======================================
# Flask App Config
# =======================================

app = Flask(__name__)
app.secret_key = "supersecret"  # Change in production

UPLOAD_FOLDER = 'temp_store'
OUTPUT_FOLDER = 'output_storage'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Google GenAI client
# Replace with your actual API key
client = genai.configure(api_key="AIzaSyAXXdZ7kt35l4EZ4lGYnHOAzdZX80SRqZM")

# =======================================
# Database Connection
# =======================================

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="database-2.chaoacuce7aq.ap-south-1.rds.amazonaws.com",
            user="admin",
            password="MSF$z99970",
            database="InsuSync",
            auth_plugin='mysql_native_password'
        )
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        print("Error connecting to MySQL:", e)
        return None, None

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="database-2.chaoacuce7aq.ap-south-1.rds.amazonaws.com",
            user="admin",
            password="MSF$z99970",
            database="InsuSync"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# =======================================
# Email OTP Configuration
# =======================================

SMTP_EMAIL = "krishna2522kumar@gmail.com"
SMTP_PASS = "ofik gkil mwpk fpaf"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def get_html_email_template(otp, subject="Account Verification"):
    """Generate HTML email template with OTP"""
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject} - INSU-SYNC</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #e0f7fa 0%, #bbdefb 100%);
            color: #1a1a2e;
            line-height: 1.6;
            padding: 20px 0;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        .email-wrapper {{
            max-width: 600px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            box-shadow: 0 12px 36px rgba(26, 26, 46, 0.12);
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(20px);
        }}
        
        .header {{
            background: linear-gradient(135deg, #2596be, #1e7a9b);
            padding: 40px 40px 30px;
            text-align: center;
            color: white;
            position: relative;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
            pointer-events: none;
        }}
        
        .brand-name {{
            display: inline-block;
            margin-bottom: 15px;
            font-size: 20px;
            font-weight: 700;
            color: white;
            letter-spacing: 0.5px;
            position: relative;
            z-index: 1;
        }}
        
        .header h1 {{
            font-size: 28px;
            color: white;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
            position: relative;
            z-index: 1;
        }}
        
        .header p {{
            font-size: 16px;
            color: rgba(255, 255, 255, 0.9);
            margin: 0;
            font-weight: 500;
            position: relative;
            z-index: 1;
        }}
        
        .content {{
            padding: 40px;
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
        }}
        
        .greeting {{
            font-size: 18px;
            color: #1a1a2e;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        
        .message {{
            font-size: 16px;
            color: #686d76;
            margin-bottom: 30px;
            line-height: 1.7;
        }}
        
        .otp-section {{
            text-align: center;
            margin: 40px 0;
            padding: 30px;
            background: rgba(37, 150, 190, 0.08);
            border: 1px solid rgba(37, 150, 190, 0.2);
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }}
        
        .otp-label {{
            font-size: 14px;
            color: #2596be;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
            font-weight: 700;
        }}
        
        .otp-code {{
            font-size: 36px;
            font-weight: 800;
            color: #1e7a9b;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            letter-spacing: 8px;
            background: rgba(255, 255, 255, 0.9);
            padding: 20px 30px;
            border: 2px solid #2596be;
            border-radius: 12px;
            display: inline-block;
            margin: 10px 0;
            box-shadow: 0 6px 20px rgba(37, 150, 190, 0.15);
            backdrop-filter: blur(10px);
        }}
        
        .security-note {{
            background: rgba(37, 150, 190, 0.1);
            border: 1px solid rgba(37, 150, 190, 0.2);
            color: #2596be;
            padding: 20px;
            border-radius: 12px;
            font-size: 14px;
            margin: 25px 0;
            backdrop-filter: blur(10px);
        }}
        
        .security-note strong {{
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #1a1a2e;
        }}
        
        .divider {{
            height: 1px;
            background: linear-gradient(to right, transparent, #2596be, transparent);
            margin: 40px 0;
        }}
        
        .footer {{
            background: rgba(254, 247, 240, 0.8);
            padding: 30px 40px;
            text-align: center;
            border-top: 1px solid rgba(37, 150, 190, 0.2);
            backdrop-filter: blur(10px);
        }}
        
        .company-info {{
            margin-bottom: 20px;
        }}
        
        .company-name {{
            font-size: 18px;
            font-weight: 700;
            color: #2596be;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
        }}
        
        .company-address {{
            font-size: 14px;
            color: #686d76;
            line-height: 1.5;
        }}
        
        .support-info {{
            font-size: 14px;
            color: #686d76;
            margin: 20px 0 10px;
        }}
        
        .support-info a {{
            color: #2596be;
            text-decoration: none;
            font-weight: 600;
        }}
        
        .support-info a:hover {{
            text-decoration: underline;
            color: #1e7a9b;
        }}
        
        .disclaimer {{
            font-size: 12px;
            color: #9ca3af;
            margin-top: 20px;
            line-height: 1.4;
        }}
        
        @media only screen and (max-width: 600px) {{
            .email-wrapper {{
                margin: 10px;
                border-radius: 12px;
            }}
            
            .header,
            .content,
            .footer {{
                padding: 25px 20px;
            }}
            
            .otp-code {{
                font-size: 28px;
                letter-spacing: 6px;
                padding: 15px 20px;
            }}
            
            .header h1 {{
                font-size: 24px;
            }}
            
            .brand-name {{
                font-size: 18px;
            }}
        }}
        
        /* Motion preferences */
        @media (prefers-reduced-motion: reduce) {{
            * {{ 
                transition: none !important; 
                animation: none !important; 
            }}
        }}
    </style>
</head>
<body>
    <div class="email-wrapper">
        <div class="header">
            <div class="brand-name">INSU-SYNC</div>
            <h1>{subject}</h1>
            <p>Complete your registration with the code below</p>
        </div>
        
        <div class="content">
            <div class="greeting">Dear User,</div>
            
            <div class="message">
                Thank you for creating an account with INSU-SYNC. To ensure the security of your account 
                and complete the registration process, please verify your email address using the 
                one-time password provided below.
            </div>
            
            <div class="otp-section">
                <div class="otp-label">Verification Code</div>
                <div class="otp-code">{otp}</div>
                <div style="margin-top: 15px; font-size: 14px; color: #686d76;">
                    This code will expire in 15 minutes
                </div>
            </div>
            
            <div class="security-note">
                <strong>🔐 Security Notice:</strong>
                For your protection, never share this verification code with anyone. Our team will never 
                ask for this code via phone, email, or any other communication method.
            </div>
            
            <div class="divider"></div>
            
            <p style="font-size: 14px; color: #686d76; margin: 0;">
                If you did not request this verification code, please disregard this email. 
                No further action is required, and your account remains secure.
            </p>
        </div>
        
        <div class="footer">
            <div class="company-info">
                <div class="company-name">INSU-SYNC</div>
                <div class="company-address">
                    Insurance Analytics Platform<br>
                    Predictive Risk Management Solutions<br>
                    Mumbai, Maharashtra, India
                </div>
            </div>
            
            <div class="support-info">
                Need help? Contact our support team at 
                <a href="mailto:support@insu-sync.com">support@insu-sync.com</a>
                or visit our <a href="#">Help Center</a>
            </div>
            
            <div class="disclaimer">
                This is an automated message sent from a monitored email address. 
                Please do not reply directly to this email. All communications are 
                sent in accordance with our Privacy Policy and Terms of Service.
                © 2025 INSU-SYNC. All rights reserved.
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html_template

def send_otp_email(to_email, otp, subject="Your OTP Code"):
    try:
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_EMAIL
        msg['To'] = to_email
        
        # Create HTML content
        html_content = get_html_email_template(otp, subject)
        
        # Create plain text fallback
        text_content = f"""
{subject}

Dear User,

Thank you for creating an account with us. To ensure the security of your account 
and complete the registration process, please verify your email address using the 
one-time password provided below.

Your OTP is: {otp}

This code will expire in 15 minutes.

Security Notice:
For your protection, never share this verification code with anyone. Our team will never 
ask for this code via phone, email, or any other communication method.

If you did not request this verification code, please disregard this email. 
No further action is required, and your account remains secure.

Best regards,
Predictive Analytics Team
        """
        
        # Record the MIME types of both parts - text/plain and text/html
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        
        # Add HTML/plain-text parts to MIMEMultipart message
        msg.attach(part1)
        msg.attach(part2)
        
        # Create secure connection and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SMTP_EMAIL, SMTP_PASS)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    
# Function to get business fixes from Gemini
def business_fixes(feature_name):
    prompt = f"""
    The dataset feature is: {feature_name}.
    This feature has low importance in predicting healthcare star ratings.

    Give ONLY **real company-level strategies** that a healthcare organization
    (like a health plan, insurance company, or provider network) could implement
    to improve this metric in practice.

    Do not provide data preprocessing or feature engineering ideas.
    Only give **business improvement actions** in bullet points.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()


# Detect weakest features dynamically
def get_weakest_features(n=3):
    feature_importances = pd.DataFrame({
        'feature': encoded_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=True)

    return feature_importances.head(n)['feature'].tolist()

    
# =======================================
# Load ML Models (Pickle + JSON)
# =======================================

try:
    with open("xgb_model.pkl", "rb") as f:
        xgb_model = pickle.load(f)
    print("XGBoost model loaded successfully")
except FileNotFoundError:
    xgb_model = None
    print("Error: xgb_model.pkl not found. Future prediction disabled.")
except Exception as e:
    xgb_model = None
    print(f"Error loading XGBoost model: {str(e)}. Future prediction disabled.")

try:
    with open("random_forest_model.pkl", "rb") as f:
        random_forest_model = pickle.load(f)
    print("Random Forest model loaded successfully")
except FileNotFoundError:
    random_forest_model = None
    print("Error: random_forest_model.pkl not found. Weak page analysis disabled.")
except Exception as e:
    random_forest_model = None
    print(f"Error loading Random Forest model: {str(e)}. Weak page analysis disabled.")

try:
    with open("model1_feature_star_logic.pkl", "rb") as f:
        model1 = pickle.load(f)
    print("Model1 loaded successfully")
except FileNotFoundError:
    model1 = None
    print("Error: model1_feature_star_logic.pkl not found. Current state analysis disabled.")
except Exception as e:
    model1 = None
    print(f"Error loading Model1: {str(e)}. Current state analysis disabled.")

# Load model and columns
model = joblib.load("random_forest_model.pkl")
encoded_columns = joblib.load("encoded_columns.pkl")


# =======================================
# Database Table Creation (Run once)
# =======================================
def create_tables():
    """Create the necessary tables if they don't exist"""
    conn, cursor = get_connection()
    if not conn:
        print("Could not create tables - no database connection")
        return
    
    try:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create executives table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS executives (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create performance_measures table with all columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_measures (
                id INT AUTO_INCREMENT PRIMARY KEY,
                breast_cancer_screening FLOAT,
                colorectal_cancer_screening FLOAT,
                annual_flu_vaccine FLOAT,
                monitoring_physical_activity FLOAT,
                snp_care_management FLOAT,
                medication_review FLOAT,
                pain_assessment FLOAT,
                osteoporosis_management FLOAT,
                diabetes_eye_exam FLOAT,
                diabetes_blood_sugar FLOAT,
                controlling_blood_pressure FLOAT,
                reducing_risk_of_falling FLOAT,
                bladder_control FLOAT,
                medication_reconciliation FLOAT,
                plan_all_cause_readmissions FLOAT,
                statin_therapy FLOAT,
                transitions_of_care FLOAT,
                follow_up_ed_highrisk FLOAT,
                getting_needed_care FLOAT,
                getting_appointments_quickly FLOAT,
                customer_service FLOAT,
                rating_healthcare_quality FLOAT,
                rating_health_plan FLOAT,
                care_coordination FLOAT,
                complaints_health_plan FLOAT,
                members_leaving_plan FLOAT,
                health_plan_quality_improvement FLOAT,
                timely_decisions_appeals FLOAT,
                reviewing_appeals FLOAT,
                call_center_interpreter FLOAT,
                complaints_drug_plan FLOAT,
                members_leaving_drug_plan FLOAT,
                drug_plan_quality_improvement FLOAT,
                rating_drug_plan FLOAT,
                needed_prescription_drugs FLOAT,
                mpf_price_accuracy FLOAT,
                med_adherence_diabetes FLOAT,
                med_adherence_hypertension FLOAT,
                med_adherence_cholesterol FLOAT,
                mtm_cmr_completion FLOAT,
                historical_star_rating FLOAT,
                region VARCHAR(255),
                gender_encoded INT,
                organization_encoded INT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        cursor.close()
        conn.close()

# Create tables on startup
create_tables()

# =======================================
# Routes
# =======================================

@app.route('/')
def home():
    # Show the main landing page
    return render_template('main.html')

@app.route('/login')
def login_page():
    # Direct to the login/signup page
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("Please log in to access the dashboard.", "error")
        return redirect(url_for('login_page'))
    
    # Redirect based on role
    if session.get('role') == 'user':
        return render_template('userdash.html', username=session['username'])
    elif session.get('role') == 'executive':
        return render_template('dashboard.html', username=session['username'])
    else:
        flash("Invalid role. Please log in again.", "error")
        return redirect(url_for('login_page'))

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('signup-user')
    email = request.form.get('signup-email')
    password = request.form.get('signup-pass')
    confirm = request.form.get('signup-confirm')
    role = request.form.get('signup-role')

    if not username or not email or not password or not confirm or not role:
        flash("All fields are required!", "error")
        return redirect(url_for('login_page'))

    if password != confirm:
        flash("Passwords do not match!", "error")
        return redirect(url_for('login_page'))

    if role not in ['user', 'executive']:
        flash("Invalid role selected!", "error")
        return redirect(url_for('login_page'))

    conn, cursor = get_connection()
    if not conn:
        flash("Database connection error!", "error")
        return redirect(url_for('login_page'))

    try:
        # Check if username or email exists in the appropriate table
        if role == 'user':
            cursor.execute("SELECT username FROM users WHERE username=%s OR email=%s", (username, email))
        else:  # executive
            cursor.execute("SELECT username FROM executives WHERE username=%s OR email=%s", (username, email))
        
        existing_user = cursor.fetchone()
        if existing_user:
            flash(f"Username or email already exists for {role} role!", "error")
            return redirect(url_for('login_page') + '?mode=signup')

        hashed_password = generate_password_hash(password)
        otp = str(random.randint(100000, 999999))

        session['signup_otp'] = otp
        session['signup_user'] = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'role': role
        }

        if send_otp_email(email, otp, "Signup OTP Verification"):
            # Redirect to OTP verification page instead of showing flash message
            return redirect(url_for('login_page') + '?show_otp=true&otp_type=signup')
        else:
            flash("Error sending OTP email. Please try again.", "error")

    except Exception as e:
        flash(f"Database error: {str(e)}", "error")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('login_page'))

@app.route('/resend-otp')
def resend_otp():
    otp_type = request.args.get('type', 'signup')
    
    if otp_type == 'signup' and 'signup_user' in session:
        email = session['signup_user']['email']
        otp = str(random.randint(100000, 999999))
        session['signup_otp'] = otp
        
        if send_otp_email(email, otp, "Signup OTP Verification"):
            return jsonify({'success': True, 'message': 'OTP resent successfully'})
        else:
            return jsonify({'success': False, 'message': 'Error resending OTP'})
    
    elif otp_type == 'forgot' and 'forgot_email' in session:
        email = session['forgot_email']
        otp = str(random.randint(100000, 999999))
        session['forgot_otp'] = otp
        
        if send_otp_email(email, otp, "Password Reset OTP"):
            return jsonify({'success': True, 'message': 'OTP resent successfully'})
        else:
            return jsonify({'success': False, 'message': 'Error resending OTP'})
    
    return jsonify({'success': False, 'message': 'No pending verification found'})

@app.route('/verify-signup-otp', methods=['POST'])
def verify_signup_otp():
    entered_otp = request.form.get('otp')
    if entered_otp == session.get('signup_otp'):
        user = session.get('signup_user')
        if not user:
            flash("Session expired. Please try signup again.", "error")
            return redirect(url_for('login_page'))

        conn, cursor = get_connection()
        if not conn:
            flash("Database connection error!", "error")
            return redirect(url_for('login_page'))

        try:
            # Insert into appropriate table based on role
            if user['role'] == 'user':
                cursor.execute(
                    "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (user['username'], user['email'], user['password'])
                )
            else:  # executive
                cursor.execute(
                    "INSERT INTO executives (username, email, password) VALUES (%s, %s, %s)",
                    (user['username'], user['email'], user['password'])
                )
            
            conn.commit()
            flash(f"Signup successful as {user['role']}! You can now login.", "success")
            session.pop('signup_otp', None)
            session.pop('signup_user', None)

        except Exception as e:
            flash(f"Database error: {str(e)}", "error")
        finally:
            cursor.close()
            conn.close()
    else:
        flash("Invalid OTP, try again.", "error")

    return redirect(url_for('login_page'))

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.form.get('forgot-email')
    role = request.form.get('forgot-role')
    
    if not email or not role:
        flash("Email and role are required!", "error")
        return redirect(url_for('login_page'))

    if role not in ['user', 'executive']:
        flash("Invalid role selected!", "error")
        return redirect(url_for('login_page'))

    conn, cursor = get_connection()
    if not conn:
        flash("Database connection error!", "error")
        return redirect(url_for('login_page'))

    try:
        # Check in appropriate table based on role
        if role == 'user':
            cursor.execute("SELECT username FROM users WHERE email=%s", (email,))
        else:  # executive
            cursor.execute("SELECT username FROM executives WHERE email=%s", (email,))
        
        user = cursor.fetchone()
        if not user:
            flash(f"Email not found for {role} role!", "error")
            return redirect(url_for('login_page'))

        otp = str(random.randint(100000, 999999))
        session['forgot_otp'] = otp
        session['forgot_email'] = email
        session['forgot_role'] = role

        if send_otp_email(email, otp, "Password Reset OTP"):
            flash("OTP sent to your email!", "info")
        else:
            flash("Error sending OTP email. Please try again.", "error")

    except Exception as e:
        flash(f"Database error: {str(e)}", "error")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('login_page'))


@app.route('/verify-forgot-otp', methods=['POST'])
def verify_forgot_otp():
    entered_otp = request.form.get('otp')
    if entered_otp == session.get('forgot_otp'):
        flash("OTP verified! You can now reset your password.", "success")
        return redirect(url_for('login_page') + '?show_otp=true&otp_type=forgot')
    else:
        flash("Invalid OTP. Try again.", "error")
        return redirect(url_for('login_page') + '?show_otp=true&otp_type=forgot')

@app.route('/reset-password', methods=['POST'])
def reset_password():
    new_password = request.form.get('new-password')
    confirm_password = request.form.get('confirm-password')

    if not new_password or not confirm_password:
        flash("All fields are required!", "error")
        return redirect(url_for('login_page'))

    if new_password != confirm_password:
        flash("Passwords do not match!", "error")
        return redirect(url_for('login_page') + '?show_otp=true&otp_type=forgot')

    email = session.get('forgot_email')
    role = session.get('forgot_role')
    
    if not email or not role:
        flash("Session expired. Please try again.", "error")
        return redirect(url_for('login_page'))

    conn, cursor = get_connection()
    if not conn:
        flash("Database connection error!", "error")
        return redirect(url_for('login_page'))

    try:
        hashed_password = generate_password_hash(new_password)
        
        # Update password in appropriate table based on role
        if role == 'user':
            cursor.execute("UPDATE users SET password=%s WHERE email=%s", (hashed_password, email))
        else:  # executive
            cursor.execute("UPDATE executives SET password=%s WHERE email=%s", (hashed_password, email))
        
        conn.commit()
        flash("Password reset successful! You can now login with your new password.", "success")
        session.pop('forgot_otp', None)
        session.pop('forgot_email', None)
        session.pop('forgot_role', None)
        
    except Exception as e:
        flash(f"Database error: {str(e)}", "error")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('login_page'))


@app.route('/signin', methods=['POST'])
def signin():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')

    if not username or not password or not role:
        flash("Username, password, and role are required!", "error")
        return redirect(url_for('login_page'))

    if role not in ['user', 'executive']:
        flash("Invalid role selected!", "error")
        return redirect(url_for('login_page'))

    conn, cursor = get_connection()
    if not conn:
        flash("Database connection error!", "error")
        return redirect(url_for('login_page'))

    try:
        # Check in appropriate table based on role
        if role == 'user':
            cursor.execute("SELECT username, password FROM users WHERE username=%s", (username,))
        else:  # executive
            cursor.execute("SELECT username, password FROM executives WHERE username=%s", (username,))
        
        user = cursor.fetchone()
        if user and check_password_hash(user[1], password):
            session['username'] = user[0]
            session['role'] = role
            flash("Login successful!", "success")
            
            # Redirect to the appropriate dashboard based on role
            if role == 'executive':
                return redirect(url_for('dashboard'))
            else:  # user
                # Assuming 'userdash.html' is the user dashboard
                return redirect(url_for('dashboard'))
        else:
            flash(f"Invalid username or password for {role} role!", "error")
            return redirect(url_for('login_page'))
            
    except Exception as e:
        flash(f"Database error: {str(e)}", "error")
        return redirect(url_for('login_page'))
    finally:
        cursor.close()
        conn.close()

# Redirect all pages to dashboard.html to use the SPA approach

@app.route('/weak')
def weak():
    if 'username' not in session or session.get('role') != 'executive':
        flash("Access denied. Please log in as an executive.", "error")
        return redirect(url_for('login_page'))
    return render_template('weak.html', username=session['username'])

@app.route('/reports')
def reports():
    if 'username' not in session or session.get('role') != 'executive':
        flash("Access denied. Please log in as an executive.", "error")
        return redirect(url_for('login_page'))
    return render_template('reports.html', username=session['username'])

@app.route('/settings')
def settings():
    if 'username' not in session or session.get('role') != 'executive':
        flash("Access denied. Please log in as an executive.", "error")
        return redirect(url_for('login_page'))
    return render_template('settings.html', username=session['username'])

@app.route('/simulator')
def simulator():
    if 'username' not in session or session.get('role') != 'executive':
        flash("Access denied. Please log in as an executive.", "error")
        return redirect(url_for('login_page'))
    return render_template('simulator.html', username=session['username'])

# Remove or update the insights route if needed
@app.route('/insights')
def insights():
    if 'username' not in session or session.get('role') != 'executive':
        flash("Access denied. Please log in as an executive.", "error")
        return redirect(url_for('login_page'))
    # If you want to keep this as a fragment navigation
    return redirect(url_for('dashboard') + '#insights')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# ------------------ Future Prediction ------------------
@app.route('/api_summary_data')
def api_summary_data():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    
    try:
        # Fetch the most recent 10 records to show trend data
        cursor.execute("SELECT * FROM performance_measures ORDER BY historical_star_rating DESC LIMIT 10")
        trend_data_db = cursor.fetchall()
        
        trend_data = []
        for row in trend_data_db:
            trend_data.append({
                'month': f"Month {len(trend_data_db) - trend_data_db.index(row)}", # Dummy month for visualization
                'Preventive Care': row.get('breast_cancer_screening', 0),
                'Chronic Condition Management': row.get('snp_care_management', 0),
                'Patient Experience': row.get('getting_appointments_quickly', 0),
                'Plan Administration': row.get('complaints_health_plan', 0)
            })

        # Fetch the very last record for the main dashboard metrics
        cursor.execute("SELECT * FROM performance_measures ORDER BY historical_star_rating DESC LIMIT 1")
        latest_data = cursor.fetchone()

        if not latest_data:
            return jsonify({'message': 'No data available in the database'}), 200

        response_data = {
            'overview': {
                'overallRating': latest_data.get('historical_star_rating', 0),
                'preventiveCare': latest_data.get('breast_cancer_screening', 0),
                'patientExperience': latest_data.get('rating_healthcare_quality', 0),
                'chronicCondition': latest_data.get('diabetes_eye_exam', 0)
            },
            'topMeasures': [
                {'measure': 'Breast Cancer Screening', 'score': float(latest_data.get('breast_cancer_screening', 0))},
                {'measure': 'Pain Assessment', 'score': float(latest_data.get('pain_assessment', 0))},
                {'measure': 'Medication Review', 'score': float(latest_data.get('medication_review', 0))}
            ],
            'domainData': [
                {
                    'period': 'Current',
                    'Preventive Care': float(latest_data.get('breast_cancer_screening', 0)),
                    'Chronic Condition Management': float(latest_data.get('snp_care_management', 0)),
                    'Patient Experience': float(latest_data.get('getting_appointments_quickly', 0)),
                    'Plan Administration': float(latest_data.get('complaints_health_plan', 0))
                }
            ],
            'patientExperience': {
                'appointments': float(latest_data.get('getting_appointments_quickly', 0)),
                'customerService': float(latest_data.get('customer_service', 0)),
                'careQuality': float(latest_data.get('rating_healthcare_quality', 0))
            },
            'trendData': trend_data  # Add the trend data here
        }
        
        cursor.close()
        conn.close()
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    
@app.route('/export-current-analysis', methods=['POST'])
def export_current_analysis():
    try:
        # Get the analysis data from the request
        data = request.json
        
        if not data or 'analysisData' not in data:
            return jsonify({'error': 'No analysis data provided'}), 400
        
        analysis_data = data['analysisData']
        
        # Create a temporary file for the PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        
        # Create the PDF document
        doc = SimpleDocTemplate(temp_file.name, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2596be')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#1a1a2e')
        )
        
        normal_style = styles['Normal']
        
        # Add title
        story.append(Paragraph("CMS Current State Analysis Report", title_style))
        story.append(Spacer(1, 20))
        
        # Add generation timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        story.append(Paragraph(f"Generated on: {timestamp}", normal_style))
        story.append(Spacer(1, 20))
        
        # Add summary section
        story.append(Paragraph("Executive Summary", heading_style))
        
        if 'summary' in analysis_data:
            summary = analysis_data['summary']
            story.append(Paragraph(f"Average Star Rating: {summary.get('avgStar', 'N/A')} / 5.0", normal_style))
            story.append(Paragraph(f"Total Features Analyzed: {summary.get('totalFeatures', 'N/A')}", normal_style))
            story.append(Paragraph(f"Data Records Processed: {summary.get('rowsProcessed', 'N/A')}", normal_style))
        
        story.append(Spacer(1, 20))
        
        # Add detailed results table
        story.append(Paragraph("Detailed Analysis Results", heading_style))
        
        if 'detailedResults' in analysis_data and analysis_data['detailedResults']:
            # Prepare table data
            table_data = [['Feature', 'Predicted Star Rating', 'Average Percentage']]
            
            for item in analysis_data['detailedResults']:
                row = [
                    item.get('feature', 'N/A'),
                    f"{item.get('predicted_star', 'N/A')}/5.0",
                    f"{item.get('average_percentage', 'N/A')}%"
                ]
                table_data.append(row)
            
            # Create table
            table = Table(table_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2596be')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            story.append(table)
        else:
            story.append(Paragraph("No detailed results available.", normal_style))
        
        story.append(Spacer(1, 30))
        
        # Add recommendations section
        story.append(Paragraph("Key Insights & Recommendations", heading_style))
        
        recommendations = [
            "Review features with lower star ratings for improvement opportunities",
            "Focus on metrics that significantly impact overall CMS star ratings", 
            "Implement targeted quality improvement initiatives",
            "Monitor progress regularly and adjust strategies as needed"
        ]
        
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", normal_style))
            story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 20))
        
        # Add footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph("This report was generated by INSU-SYNC CMS Analysis Platform", footer_style))
        story.append(Paragraph("© 2025 INSU-SYNC. All rights reserved.", footer_style))
        
        # Build the PDF
        doc.build(story)
        
        # Read the PDF file
        with open(temp_file.name, 'rb') as f:
            pdf_data = f.read()
        
        # Clean up the temporary file
        os.unlink(temp_file.name)
        
        # Create response
        response = app.response_class(
            pdf_data,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="CMS_Analysis_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
            }
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate PDF: {str(e)}'}), 500


@app.route('/predict', methods=['POST'])
def predict():
    if xgb_model is None:
        return jsonify({'error': 'Future prediction model not loaded.'}), 500
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file, encoding='latin1')
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file, engine="openpyxl")
        else:
            return jsonify({'error': 'Unsupported file type'}), 400
        predictions = xgb_model.predict(df)
        predicted_value = round(float(predictions[0]), 2)
        return jsonify({
            'data': predicted_value,
            'message': 'Future prediction successful',
            'columns_received': list(df.columns),
            'data_shape': df.shape
        })
    except Exception as e:
        return jsonify({'error': f'An error occurred during future prediction: {str(e)}'}), 500
# ------------------ Current State Analysis ------------------

@app.route('/analyze-current', methods=['POST'])
def analyze_current_state():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({'error': f'An error occurred while saving the file: {str(e)}'}), 500
    try:
        result_df = rule.load(file_path)
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'rule_output.csv')
        result_df.to_csv(output_path, index=False)
        results = result_df.to_dict('records')
        return jsonify({
            'data': results,
            'message': 'Current state analysis successful',
            'columns_received': list(result_df.columns),
            'data_shape': result_df.shape
        })
    except FileNotFoundError:
        return jsonify({'error': 'Dataset not found.'}), 404
    except Exception as e:
        return jsonify({'error': f'An error occurred during current state analysis: {str(e)}'}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# ------------------ Weak Page Analysis (uses Random Forest) ------------------

@app.route("/weak_analysis", methods=["POST"])
def weak_analysis():
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        
        # Check if file has a valid name
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read the file based on extension
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return jsonify({"error": "Unsupported file format. Please upload CSV or Excel files."}), 400
        
        # Prepare the data for prediction (assuming it matches the model's expected format)
        # You may need to adjust this based on your model's requirements
        input_encoded = pd.get_dummies(df, drop_first=True)
        input_encoded = input_encoded.reindex(columns=encoded_columns, fill_value=0)
        
        # Make predictions
        predictions = model.predict(input_encoded)
        avg_prediction = predictions.mean()
        
        # Get weakest features automatically
        weak_features = get_weakest_features(n=3)
        
        # Generate business fixes using Gemini
        strategies = {f: business_fixes(f) for f in weak_features}
        
        # Format strategies for display
        formatted_strategies = "\n\n".join([f"Feature: {f}\nStrategies:\n{s}" for f, s in strategies.items()])
        
        # Prepare response
        response_data = {
            "future_prediction": round(avg_prediction, 2),
            "current_state": {
                "shape": df.shape,
                "data": df.head().to_dict()  # Sample of data
            },
            "strategies": formatted_strategies,
            "weak_features": weak_features
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
        
# ------------------ Healthcare Data API Endpoint ------------------

@app.route('/api/healthcare-data', methods=['GET'])
def get_healthcare_data():
    try:
        conn, cursor = get_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get all data ordered by ID (oldest to newest)
        cursor.execute("SELECT * FROM performance_measures ORDER BY id ASC")
        rows = cursor.fetchall()
        
        if not rows:
            return jsonify({'error': 'No data found'}), 404
        
        # Process the latest row for most metrics
        latest_data = rows[-1]  # Last row is the newest
        
        # Define measure columns for fallback calculation
        measure_columns = [
            'breast_cancer_screening', 'colorectal_cancer_screening', 'annual_flu_vaccine',
            'monitoring_physical_activity', 'snp_care_management', 'medication_review',
            'pain_assessment', 'osteoporosis_management', 'diabetes_eye_exam', 'diabetes_blood_sugar',
            'controlling_blood_pressure', 'reducing_risk_of_falling', 'bladder_control',
            'medication_reconciliation', 'plan_all_cause_readmissions', 'statin_therapy',
            'transitions_of_care', 'follow_up_ed_highrisk'
        ]
        
        # Prepare trend data - order from oldest to newest
        trend_data = []
        # Use all rows in chronological order (oldest first)
        chronological_rows = rows  # Already ordered by ID ASC

        for row in chronological_rows:
            # Check if there's a date column, otherwise use record ID
            if 'timestamp' in row and row['timestamp'] is not None:
                # If it's a string, try to parse it
                if isinstance(row['timestamp'], str):
                    try:
                        date_obj = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                else:
                    date_obj = row['timestamp']
                period = date_obj.strftime('%b %d, %Y')  # Format as "Jan 01, 2023"
            else:
                period = f"Record {row['id']}"
            
            # Use historical_star_rating if available, otherwise calculate
            if 'historical_star_rating' in row and row['historical_star_rating'] is not None:
                rating = float(row['historical_star_rating'])
            else:
                total = sum(float(row[measure]) for measure in measure_columns if measure in row and row[measure] is not None)
                count = sum(1 for measure in measure_columns if measure in row and row[measure] is not None)
                rating = (total / count) * 5 if count > 0 else 0
            
            trend_data.append({
                'period': period,
                'rating': rating
            })
        
        # Prepare a simple response with key metrics
        response_data = {
            'overallRating': float(latest_data.get('historical_star_rating', 0)),
            'topMeasures': [
                {'measure': 'Breast Cancer Screening', 'score': float(latest_data.get('breast_cancer_screening', 0))},
                {'measure': 'Colorectal Cancer Screening', 'score': float(latest_data.get('colorectal_cancer_screening', 0))},
                {'measure': 'Annual Flu Vaccine', 'score': float(latest_data.get('annual_flu_vaccine', 0))}
            ],
            'bottomMeasures': [
                {'measure': 'Pain Assessment', 'score': float(latest_data.get('pain_assessment', 0))},
                {'measure': 'Medication Review', 'score': float(latest_data.get('medication_review', 0))}
            ],
            'domainData': [
                {
                    'period': 'Current',
                    'Preventive Care': float(latest_data.get('breast_cancer_screening', 0)),
                    'Chronic Condition Management': float(latest_data.get('snp_care_management', 0)),
                    'Patient Experience': float(latest_data.get('getting_appointments_quickly', 0)),
                    'Plan Administration': float(latest_data.get('complaints_health_plan', 0))
                }
            ],
            'patientExperience': {
                'appointments': float(latest_data.get('getting_appointments_quickly', 0)),
                'customerService': float(latest_data.get('customer_service', 0)),
                'careQuality': float(latest_data.get('rating_healthcare_quality', 0))
            },
            'trendData': trend_data  # Add the trend data here
        }
        
        cursor.close()
        conn.close()
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    
class HealthPlanRecommender:
    def __init__(self, data_path=None, df=None):
        if df is not None:
            self.df = df
        elif data_path:
            self.df = pd.read_csv(data_path)
        else:
            raise ValueError("Either data_path or df must be provided")
        
        # Clean column names
        self.df.columns = self.df.columns.str.strip()
        
        # Condition to column mapping
        self.condition_mapping = {
            'diabetes': ['Diabetes Care – Eye Exam', 'Diabetes Care – Blood Sugar Controlled', 
                        'Medication Adherence for Diabetes Medications'],
            'heart': ['Statin Therapy for Patients with Cardiovascular Disease', 'Controlling Blood Pressure'],
            'cancer': ['Breast Cancer Screening', 'Colorectal Cancer Screening'],
            'elderly': ['Care for Older Adults – Medication Review', 'Care for Older Adults – Pain Assessment',
                       'Osteoporosis Management in Women who had a Fracture', 'Reducing the Risk of Falling'],
            'general': ['Annual Flu Vaccine', 'Monitoring Physical Activity', 'Getting Needed Care'],
            'medication': ['Medication Adherence for Hypertension (RAS antagonists)', 
                          'Medication Adherence for Cholesterol (Statins)', 'MTM Program Completion Rate for CMR'],
            'chronic': ['Follow-up after Emergency Department Visit for People with Multiple High-Risk Chronic Conditions',
                       'Transitions of Care']
        }
    
    def preprocess_data(self):
        """Preprocess the data for analysis"""
        # Convert relevant columns to numeric, handling errors
        numeric_columns = [
            'Breast Cancer Screening', 'Colorectal Cancer Screening', 'Annual Flu Vaccine',
            'Diabetes Care – Eye Exam', 'Diabetes Care – Blood Sugar Controlled',
            'Statin Therapy for Patients with Cardiovascular Disease', 'Controlling Blood Pressure',
            'Historical_Star_Rating'
        ]
        
        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Fill NaN values with column mean
        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col].fillna(self.df[col].mean())
    
    def find_condition_columns(self, condition_input):
        """Find relevant columns based on condition input"""
        condition_input = condition_input.lower()
        
        for condition, columns in self.condition_mapping.items():
            if condition in condition_input:
                # Return only columns that exist in the dataframe
                available_columns = [col for col in columns if col in self.df.columns]
                return available_columns, condition
        
        # If no direct match, try fuzzy matching
        for condition in self.condition_mapping.keys():
            if condition in condition_input:
                available_columns = [col for col in self.condition_mapping[condition] 
                                   if col in self.df.columns]
                return available_columns, condition
        
        return None, None
    
    def recommend_plans(self, condition_input, top_n=3):
        """Recommend plans based on condition"""
        condition_columns, matched_condition = self.find_condition_columns(condition_input)
        
        if not condition_columns:
            return f"Sorry, I couldn't find specific measures for '{condition_input}'. " \
                   f"Try conditions like: diabetes, heart, cancer, elderly, general, medication, or chronic."
        
        # Calculate average score for the condition
        self.df['Condition_Score'] = self.df[condition_columns].mean(axis=1)
        
        # Sort by condition score and star rating
        recommendations = self.df.nlargest(top_n, ['Condition_Score', 'Historical_Star_Rating'])
        
        # Prepare response
        response = f"Based on your condition '{matched_condition}', here are the top {top_n} recommended plans:\n\n"
        
        for i, (idx, row) in enumerate(recommendations.iterrows(), 1):
            response += f"{i}. {row['Organization Marketing Name']} (Plan ID: {row['CONTRACT_ID']})\n"
            response += f"   Star Rating: {row['Historical_Star_Rating']}/5\n"
            response += f"   Condition Score: {row['Condition_Score']:.3f}/1.0\n"
            
            # Add specific metric scores
            for col in condition_columns:
                if col in row:
                    response += f"   {col}: {row[col]:.3f}\n"
            
            response += "\n"
        
        response += "Note: Higher scores indicate better performance in these quality measures."
        return response
    
    def get_plan_details(self, plan_id):
        """Get detailed information about a specific plan"""
        plan_data = self.df[self.df['CONTRACT_ID'] == plan_id]
        
        if plan_data.empty:
            return f"Plan with ID {plan_id} not found."
        
        row = plan_data.iloc[0]
        response = f"Plan Details for {row['Organization Marketing Name']} (ID: {plan_id}):\n\n"
        response += f"Star Rating: {row['Historical_Star_Rating']}/5\n"
        response += f"Member ID: {row['Member_ID']}\n"
        response += f"Region: {row['Region_Zip_Code']}\n"
        response += f"Gender: {row['Gender']}\n"
        response += f"Age: {row['age']}\n\n"
        
        response += "Key Quality Measures:\n"
        measures = [
            'Breast Cancer Screening', 'Colorectal Cancer Screening', 'Annual Flu Vaccine',
            'Diabetes Care – Eye Exam', 'Diabetes Care – Blood Sugar Controlled',
            'Statin Therapy for Patients with Cardiovascular Disease', 'Controlling Blood Pressure'
        ]
        
        for measure in measures:
            if measure in row:
                response += f"  {measure}: {row[measure]:.3f}\n"
        
        return response

# Initialize the recommender
try:
    df = pd.read_csv(r"Star_data.csv", encoding='latin1')
    recommender = HealthPlanRecommender(df=df)
    recommender.preprocess_data()
except Exception as e:
    print(f"Error loading data: {e}")
    # Create a dummy recommender for demonstration
    recommender = None

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json['message']
    
    if not recommender:
        return jsonify({'response': "Error: Data not loaded properly. Please check your data file."})
    
    if user_input.lower() in ['exit', 'quit', 'bye']:
        return jsonify({'response': "Thank you for using the Health Plan Recommendation Chatbot. Goodbye!"})
    
    elif user_input.lower() in ['help', '?']:
        help_text = "Available commands:\n- Describe your health condition (e.g., 'diabetes', 'heart condition')\n- 'exit' - Quit the chatbot\n- 'help' - Show this help message\n\nSupported conditions: diabetes, heart, cancer, elderly, general, medication, chronic"
        return jsonify({'response': help_text})
    
    elif 'plan' in user_input.lower() and 'detail' in user_input.lower():
        # Extract plan ID using regex
        plan_match = re.search(r'[A-Z]\d{4}', user_input.upper())
        if plan_match:
            plan_id = plan_match.group()
            response = recommender.get_plan_details(plan_id)
        else:
            response = "Please specify a plan ID (e.g., 'show details for plan H5084')"
        return jsonify({'response': response})
    
    else:
        # Get recommendations based on condition
        response = recommender.recommend_plans(user_input)
        return jsonify({'response': response})


# =======================================
# Run Flask App
# =======================================

if __name__ == "__main__":
    app.run(debug=True)