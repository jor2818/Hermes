from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import pymysql
from flask_paginate import Pagination, get_page_parameter, get_page_args
from exif import Image
import reverse_geocoder as rg
import webbrowser



con = pymysql.connect("localhost","root","root","hermes",8889)

post = Blueprint("post",__name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
# Get current path
path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'hermes/static/uploads/')

global post_id

def allowed_file(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def format_dms_coordinates(coordinates):
    return f"{coordinates[0]}° {coordinates[1]}\' {coordinates[2]}\""

def dms_coordinates_to_dd_coordinates(coordinates, coordinates_ref):
    decimal_degrees = coordinates[0] + \
                      coordinates[1] / 60 + \
                      coordinates[2] / 3600
    
    if coordinates_ref == "S" or coordinates_ref == "W":
        decimal_degrees = -decimal_degrees
    
    return decimal_degrees

def draw_map_for_location(latitude, latitude_ref, longitude, longitude_ref):
    
    
    decimal_latitude = dms_coordinates_to_dd_coordinates(latitude, latitude_ref)
    decimal_longitude = dms_coordinates_to_dd_coordinates(longitude, longitude_ref)
    url = f"https://www.google.com/maps?q={decimal_latitude},{decimal_longitude}"
    webbrowser.open_new_tab(url)


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

        
        # pagination section      
        page = request.args.get(get_page_parameter(), type=int, default=1)
        start = (page-1)*5
        end = start + 5
        row = rows[start:end]
        pagination = Pagination(page=page, total=len(rows), per_page=5, record_name='rows')
               
        return render_template('dash.html', rows=row, pagination=pagination,)

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
        
        return render_template('postcontent.html', details=details, photos=photos, post_id=post_id)

@post.route('/display/<filename>', methods=['POST','GET'])
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@post.route('/map/<post_id>/<filename>', methods=['POST','GET'])
def showmap(filename, post_id):
    
    filename = UPLOAD_FOLDER + filename
    with open(filename, "rb") as pic_file:
        image = Image(pic_file)
    
    # Check that have the gps_latitude
    if image.has_exif:
        try:
            draw_map_for_location(image.gps_latitude, 
                                image.gps_latitude_ref, 
                                image.gps_longitude,
                                image.gps_longitude_ref)
            
        except (AttributeError, KeyError):
            
            flash('รูปภาพไม่มีข้อมูลตำแหน่งบนแผนที่ โปรดเลือกรูปอื่น')
            return redirect(url_for('post.postdetail', post_id = post_id ))
    else:
        flash('รูปภาพไม่มีข้อมูลสำคัญสำหรับการแสดงตำแหน่งบนแผนที่ โปรดเลือกรูปอื่น')
    
    return redirect(url_for('post.postdetail', post_id = post_id ))