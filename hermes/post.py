from flask import Blueprint, request, redirect, url_for, flash
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
        
        with con:
            cur = con.cursor()
            sql = "INSERT INTO post (name, phone, data, create_post) VALUES (%s, %s, %s, %s)"
            cur.execute(sql,(name,phone,data,datetime.now()))
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
        
        