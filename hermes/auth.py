from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

con = pymysql.connect("localhost","root","root","hermes",8889)

auth = Blueprint("auth",__name__)


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('views.home'))

@auth.route("/login")
def login():
    return render_template('login.html',name="LOGIN")

@auth.route("/signup")
def signup():
    return render_template('signup.html',name="SIGNUP")

@auth.route('/addmember', methods=['POST'])
def addmember():
    
    if request.method == 'POST':
        
        fname = request.form['fname']
        lname = request.form['lname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password_1']
        con_password = request.form['password_2']
        
        if len(fname)<2:
            flash("ชื่อต้องมีความยาวมากกว่า 2 ตัวอักษร โปรดใส่อีกครั้ง")
            
        elif len(lname)<2:
            flash("นามสกุลต้องมีความยาวมากกว่า 2 ตัวอักษร โปรดใส่อีกครั้ง")

        elif len(username)<2:
            flash("ชื่อผู้ใช้ต้องมีความยาวมากกว่า 2 ตัวอักษร โปรดใส่อีกครั้ง")

        elif len(email)<7:
            flash("Email ต้องมีความยาวมากกว่า 2 ตัวอักษร โปรดใส่อีกครั้ง")
        
        elif password != con_password:
            flash("รหัสผ่านไม่ตรงกัน ลองใหม่อีกครั้ง")
            
        else:
            # generate hash password
            password = generate_password_hash(password)
            with con:
                cur = con.cursor()
                sql = "INSERT INTO user (fname, lname, username, email, password) VALUES (%s, %s, %s, %s, %s)"
                cur.execute(sql,(fname,lname,username,email,password))
                con.commit()
                return redirect(url_for('auth.login'))

    return redirect(url_for('auth.signup'))


@auth.route('/checklogin', methods=['POST'])
def checklogin():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with con:
            cur = con.cursor()
            sql = "SELECT * FROM user WHERE username=%s"
            cur.execute(sql,username)
            rows = cur.fetchall()
            print(rows)
            
            if len(rows)>0:
                if check_password_hash(rows[0][5],password):
                    session['username'] = username
                    session['fname'] = rows[0][1]
                    session.permanent = True
                    return redirect(url_for('post.showpost'))
                else:
                    flash("รหัสผ่านไม่ถูกต้อง โปรดใส่ชื่อผู้ใช้และรหัสผ่านอีกครั้ง")
            
            else:
                flash("คุณไม่มีชื่อในระบบ โปรดลงทะเบียนก่อนเข้าใช้")
            return redirect(url_for('auth.login'))