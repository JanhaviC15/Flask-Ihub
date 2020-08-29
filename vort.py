import datetime
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate(r"-----Add Credentials------")

firebase_admin.initialize_app(cred)

db = firestore.client()

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class Attendance(FlaskForm):
    Date = SubmitField('Date')
    CheckIn = SubmitField('CheckIn')
    CheckOut = SubmitField('CheckOut')


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = '-----Add Secret Key-----'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
Debug = False

posts = [
    {
        'author': "Today's Headline",
        'title': 'Employee Management System',
        'content': 'Check Out new projects to work on...',
        'date': '20/2/15'
    },
    {
            'author': "Today's Update",
            'title': 'Profile updation required',
            'content': 'All employee are requested to update their profile as per .....',
            'date': '20/2/15'
        },
    {
            'author': "Today's Meeting",
            'title': 'No meeting scheduled today',
            'content': 'Check for future meetings and update your schedule...',
            'date': '20/2/15'
        },
]

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html",posts=posts)

@app.route("/about")
def about():
   return render_template("about.html",title='About')

@app.route("/Dashboard")
def Dashboard():
   return render_template("Dashboard.html",title='Dashboard')

@app.route("/register", methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!','success')
        return redirect(url_for('home'))
    return render_template("register.html",title='Register',form=form)

@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash(f'You have been login successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'Login unsuccessfully', 'danger')
    return render_template("login.html",title='Login',form=form)


@app.route("/attendance",  methods=['GET','POST'])
def attendance():
    form = Attendance()
    return render_template("attendance.html", title='Attendance', form=form)

@app.route("/attendance_status",  methods=['GET','POST'])
def attendance_status():
    doc_ref = db.collection(u'Employee').document("emp1").collection("Attendance")
    l = []
    doc = doc_ref.get()
    if doc:
        for i in doc:
            l.append(i.to_dict())
    df = pd.DataFrame(l)
    return render_template('att_status.html', column_names=df.columns, row_data=list(df.values.tolist()), zip=zip, title="Attandance Status")

@app.route('/experiment', methods=['GET','POST'])
def new():
    if request.method == "POST":
        ip = request.form['EmpId']
        doc_ref = db.collection(u'Admin').document(ip).collection("Attendance")
        l = []
        doc = doc_ref.get()
        if doc:
            for i in doc:
                l.append(i.to_dict())
        normal = pd.DataFrame(l)
        df = normal
        print(df)
        return render_template('att_status_admin.html', column_names=df.columns.values, row_data=list(df.values.tolist()),zip=zip, title="Attandance Status")
    return render_template("experiment.html")

@app.route("/CheckInRoute",  methods=['GET','POST'])
def CheckInRoute():
    return render_template('CheckIn.html')

@app.route("/CheckOutRoute",  methods=['GET','POST'])
def CheckOutRoute():
    return render_template('CheckOut.html')

@app.route("/CheckIn",  methods=['GET','POST'])
def CheckIn():
    if request.method == "POST":
        CheckIn = request.form['CheckIn']
        CheckIn1 = str(CheckIn)
        now = datetime.datetime.now().date()
        Date = str(now)
        in_ref = db.collection(u'Employee').document("emp1").collection("Attendance").document(Date)
        in_ref.set({
            'Date': Date,
            'Check In': CheckIn1,
        })
        flash(f'Checked In successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('CheckIn.html',title = 'Attendance')

@app.route("/CheckOut",  methods=['GET','POST'])
def CheckOut():
    now = datetime.datetime.now().date()
    Date = str(now)
    if request.method == "POST":
        CheckOut = request.form['CheckOut']
        CheckOut1 = str(CheckOut)
        out_ref = db.collection(u'Employee').document("emp1").collection("Attendance").document(Date)
        out_ref.set({
            'Check Out': CheckOut1,
        } ,merge=True)
        flash(f'Checked Out successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('CheckOut.html',title = 'Attendance')

if __name__ == "__main__":
    app.run(debug=True)
