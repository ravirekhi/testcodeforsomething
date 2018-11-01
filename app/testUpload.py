from flask import request,session,abort
from werkzeug.utils import secure_filename
from app import webapp
from app.utils import get_db
from app.transformations import transform_and_upload
from app.images import generateImageObject,insert_to_imagesdb,update_imagesdb,updateImageObject

@webapp.route('/test/FileUpload', methods=['GET', 'POST'])
def test_upload_image():
    userid = request.form['userID']
    psw = request.form['password']
    test_validate_user(userid,psw)
    file = request.files['uploadedfile']
    filename = secure_filename(file.filename)
    imgObj = generateImageObject(filename)
    id = insert_to_imagesdb(imgObj)
    imgObj = updateImageObject(imgObj, id, filename)
    update_imagesdb(imgObj, id)
    transform_and_upload(file.read(), imgObj)
    return "Success"


def test_validate_user(userid,psw):
    cnx = get_db()
    cursor = cnx.cursor()
    query = "SELECT id FROM users WHERE login=%s AND password=%s"
    cursor.execute(query, (userid, psw))
    row = cursor.fetchone()
    if row is None:
        error_msg = "Error: Username or Password is invalid!"
        abort(400)
    session['username'] = userid
    session['userid'] = row[0]
    return