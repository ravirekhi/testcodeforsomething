from flask import render_template, request,session
from werkzeug.utils import secure_filename
from app import webapp
from app.utils import login_required,get_db,s3_config
from app.transformations import transform_and_upload
from flask.json import jsonify


@webapp.route('/welcome', methods=['GET'])
@login_required
def welcome():
    return render_template("welcome.html", title="Welcome "+session['username'])


@webapp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_image():
    error_msg=""
    if request.method == 'GET':
        return render_template("upload.html", title="Upload image")
    file = request.files['file']
    filename = secure_filename(file.filename)
    imgObj = generateImageObject(filename)
    id = insert_to_imagesdb(imgObj)
    imgObj = updateImageObject(imgObj,id,filename)
    update_imagesdb(imgObj, id)
    transform_and_upload(file.read(),imgObj)
    return render_template('welcome.html',title="Welcome "+session['username'],error_msg=error_msg)

@webapp.route('/images', methods=['GET','POST'])
@login_required
def image_list():
    cnx = get_db()
    cursor = cnx.cursor()
    query = "SELECT * FROM images WHERE userId = %s"
    images = []
    cursor.execute(query, (session['userid'],))
    for row in cursor:
        images.append(row)
    return render_template('images_list.html', title="Image List",images=images,s3_url=s3_config['url'])

@webapp.route('/transforms/<id>', methods=['GET'])
@login_required
def transformation_list(id):
    return render_template('transformation_list.html', title="Transformation List",id=id,url=s3_config['url'])


@webapp.route('/getImage', methods=['GET','POST'])
@login_required
def getImage():
    data = []
    query="SELECT key1 from images where userId=%s"
    cnx = get_db()
    cursor = cnx.cursor()
    cursor.execute(query, (session['userid'],))
    rows= cursor.fetchall()
    return jsonify({'rows': rows})


@webapp.route('/getTransforms/<id>', methods=['GET','POST'])
@login_required
def getTransforms(id):
     data = []
     query="SELECT * from images where userId=%s and id=%s"
     cnx = get_db()
     cursor = cnx.cursor()
     cursor.execute(query, (session['userid'],id))
     rows= cursor.fetchall()
     return jsonify({'rows': rows})



def insert_to_imagesdb(imgObj):
    query="INSERT into images (userId,key1,key2,key3,key4) VALUES (%s,%s,%s,%s,%s)"
    cnx = get_db()
    cursor = cnx.cursor()
    cursor.execute(query, (imgObj['userid'], imgObj['key1'],imgObj['key2'],imgObj['key3'],imgObj['key4']))
    cnx.commit()
    query = "SELECT id from images where userId=%s and key1=%s and key2=%s and key3=%s and key4=%s"
    cursor.execute(query, (imgObj['userid'], imgObj['key1'], imgObj['key2'], imgObj['key3'], imgObj['key4']))
    row = cursor.fetchone()
    return row[0]

def generateImageObject(filename):
    imgObj = {}
    imgObj['userid']=session['userid'];
    imgObj['key1'] = "%s/%s" % (session['username'],filename);
    imgObj['key2'] = "%s/FLIPPED_%s" % (session['username'],filename);
    imgObj['key3'] = "%s/BLURRED_%s" % (session['username'],filename);
    imgObj['key4'] = "%s/RESIZED_%s" % (session['username'],filename);
    return imgObj


def updateImageObject(imgObj,id,filename):
    imgObj['key1'] = "%s/%s/%s" % (session['username'],id,filename);
    imgObj['key2'] = "%s/%s/FLIPPED_%s" % (session['username'],id,filename);
    imgObj['key3'] = "%s/%s/BLURRED_%s" % (session['username'],id,filename);
    imgObj['key4'] = "%s/%s/RESIZED_%s" % (session['username'],id,filename);
    return imgObj

def update_imagesdb(imgObj,id):
    query="UPDATE images set key1=%s,key2=%s,key3=%s,key4=%s where id=%s"
    cnx = get_db()
    cursor = cnx.cursor()
    cursor.execute(query, (imgObj['key1'],imgObj['key2'],imgObj['key3'],imgObj['key4'],id))
    cnx.commit()
    return
