from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import pymysql


con = pymysql.connect("localhost","root","root","hermes",8889)

post = Blueprint("post",__name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
# Get current path
path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'hermes/static/uploads/')

def allowed_file(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@post.route('/addpost', methods=['POST','GET'])
def addpost():
    
    if request.method == 'POST':
        
        name = request.form['name']
        phone = request.form['phone']
        data = request.form['data']
        title = request.form['title']
        
        with con:
            cur = con.cursor()
            sql = "INSERT INTO post (name, phone, title, data, create_post) VALUES (%s, %s, %s,%s, %s)"
            cur.execute(sql,(name,phone,title,data,datetime.now()))
            con.commit()
            
            x = cur.execute("SELECT LAST_INSERT_ID() FROM post")
            
            files = request.files.getlist('files[]')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(UPLOAD_FOLDER + filename)
                    cur.execute("INSERT INTO photo (pathfilename, post_id) VALUES (%s, %s)",[filename, x])
                    con.commit()
            
            
        flash('ข้อมูลการแจ้งเรื่องราว/ร้องทุกข์ของท่านได้ถูกส่งไปให้เจ้าหน้าที่ที่เกี่ยวข้องเรียบร้อยแล้ว')
  
        return redirect(url_for('views.home'))
        
@post.route('/showpost', methods=['POST','GET'])
def showpost():
    
    if "username" not in session:
        return redirect(url_for('auth.login'))

    with con:
        cur = con.cursor()
        sql = "SELECT * FROM post ORDER BY create_post DESC"
        cur.execute(sql)
        rows = cur.fetchall()
        print(rows)
        return render_template('dash.html', rows=rows)

@post.route('/postdetail/<string:post_id>', methods=['POST','GET'])
def postdetail(post_id):
    
    if "username" not in session:
        return redirect(url_for('auth.login'))
    
    with con:
        cur = con.cursor()
        sql = "SELECT * FROM post WHERE id = %s"
        cur.execute(sql, post_id)
        details = cur.fetchall()
        print(details)
        sql = "SELECT * FROM photo WHERE post_id = %s"
        cur.execute(sql, post_id)
        photos = cur.fetchall()
        print(photos)

        
        return render_template('postcontent.html', details=details, photos=photos)

@post.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)