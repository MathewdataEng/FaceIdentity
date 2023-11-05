from flask import Response, redirect, url_for,render_template, request, session
import cv2
import pandas as pd
import datetime
from mtcnn_cv2 import MTCNN
from app.face_recognition import faceRecognitionPipeline
import pymysql
import numpy as np
# Establish a connection to the MySQL server
try:
    connection = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='minhtri01',
        database='finalthesis'
    )
except Exception as e:
    print(f"Could not connect to database: {e}")
    exit()

detector = MTCNN()

def home():
    return render_template("home.html")
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        # Query the database for the user with the given username and password
        try:
            cursor = connection.cursor()
            query = "SELECT * FROM account WHERE User=%s AND Password=%s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            if result:
                # User is authenticated, so store their username in the session
                session["username"] = username
                return redirect(url_for("home"))
            else:
                # Invalid username or password
                return "Login failed. Invalid username or password."
        except Exception as e:
            print(f"Error: {e}")
            exit()
    else:
        return render_template("login.html")

def logout():
    session.clear()
    return redirect(url_for("home"))

def index():
    cursor = connection.cursor()
    query = "SELECT * FROM rtsp_links"
    cursor.execute(query)
    results = cursor.fetchall()
    # convert the results to a pandas DataFrame
    df = pd.DataFrame(results, columns=['Link', 'Timestamp', 'User'])
    return render_template('index.html', rtsp_links=df.to_dict('records'))

def add_link():
    link = request.form['link']
    print(link)
    # Check if the link already exists
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM rtsp_links WHERE Link=%s"
        cursor.execute(query, (link,))
        results = cursor.fetchall()
        if len(results) > 0:
            return redirect('/index')
        else:
            # Insert the new link into the database
            timestamp = datetime.datetime.now()
            user = session
            query = "INSERT INTO rtsp_links (Link, Timestamp, User) VALUES (%s, %s, %s)"
            cursor.execute(query, (link, timestamp, user))
            connection.commit()
            print('Success: The link has been added to the database.')
    except Exception as e:
        print(f"Error: {e}")
        exit()

    return redirect('/index')


def delete_link():
    link = request.form['link']
    # Delete the row with the specified link value
    try:
        cursor = connection.cursor()
        query = "DELETE FROM rtsp_links WHERE Link = %s"
        cursor.execute(query, (link,))
        connection.commit()
        print(f"Success: {cursor.rowcount} row(s) deleted.")
    except Exception as e:
        print(f"Error: {e}")
        exit()

    return redirect('/index')

def modify_link():
    # df = pd.read_csv('static/rtsp_links.csv')
    old_link = request.form['old_link']
    new_link = request.form['new_link']
    timestamp = datetime.datetime.now()
    user = session
    try:
        cursor = connection.cursor()
        query = "UPDATE rtsp_links SET Link=%s, Timestamp=%s, User=%s WHERE Link=%s"
        cursor.execute(query, (new_link, timestamp, user, old_link))
        connection.commit()
        print(f"Success: {cursor.rowcount} row(s) updated.")
    except Exception as e:
        print(f"Error: {e}")
        exit()
    return redirect('/index')


def gen_frames(rtsp_link):

    cap = cv2.VideoCapture(rtsp_link)
    print(rtsp_link)
    if not cap.isOpened():
        raise RuntimeError('Error opening video stream or file')

    while True:

        ret, frame = cap.read()
        if not ret:
            break
        else:

            frame, predictions = faceRecognitionPipeline(frame,path=False)
            for i , obj in enumerate(predictions):
                if obj['score_emotion'] > 0.65:
                    with connection.cursor() as cursor:
                        sql = "INSERT INTO report_new (timestamp, image,h_image,w_image,roi,h_roi,w_roi, prediction_name, score_id, prediction_emotion, score_emotion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s)"
                        val = (obj['timestamp'], obj['image'],obj['h_image'],obj['w_image'],obj['roi'],obj['h_roi'],obj['w_roi'], obj['prediction_name'], obj['score_id'], obj['prediction_emotion'], obj['score_emotion'])
                        cursor.execute(sql, val)
                    connection.commit()

            ret, buffer = cv2.imencode('.jpg', frame)

            # Yield the resulting frame in byte format
            frame_bytes = buffer.tobytes()
            yield b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n--frame\r\n'
    # Release the video capture object
    cap.release()
    cv2.destroyAllWindows()



def video_feed():
    # Get the selected RTSP link from the query parameter
    rtsp_link = request.args.get('rtsp_link')
    if rtsp_link.isdigit():
        rtsp_link = int(rtsp_link)
    # Return the response with the video stream
    return Response(gen_frames(rtsp_link),
                   mimetype="multipart/x-mixed-replace; boundary=frame" )

def display():
    cursor = connection.cursor()
    query = "SELECT * FROM rtsp_links"
    cursor.execute(query)
    results = cursor.fetchall()
    # convert the results to a pandas DataFrame
    rtsp_links_df = pd.DataFrame(results, columns=['Link', 'Timestamp', 'User'])
    rtsp_links = list(rtsp_links_df['Link'])
    return render_template('video.html', rtsp_links=rtsp_links)

def report():
    if request.method == 'POST':
        datetime = request.form['date']
        cursor = connection.cursor()
        query = "SELECT id,timestamp,prediction_name,score_id,prediction_emotion,score_emotion FROM report_new WHERE DATE(timestamp) = %s"
        cursor.execute(query, datetime)
        data = cursor.fetchall()
        return render_template('report.html', data=data)
    return render_template('report.html')

def displayimage():
    id_num = request.args.get('id_number')
    if id_num:
        report = []
        cursor = connection.cursor()
        query = "SELECT * FROM report_new WHERE id = %s"
        cursor.execute(query, id_num)
        data = cursor.fetchone()
        if data:
            timestamp = data[1]
            image = data[2]
            h_image = data[3]
            w_image = data[4]           
            roi = data[5]
            h_roi = data[6]
            w_roi = data[7]
            name = data[8]
            score_id = round(float(data[9]) * 100,2)
            emotion = data[10]
            score_emotion = round(float(data[11]) *100,2)
            image = np.frombuffer(image, np.uint8) .reshape((h_image,w_image,3))
            cv2.imwrite(f'.\static\predict\image.jpg',image)
            roi = np.frombuffer(roi, np.uint8) .reshape((h_roi,w_roi,3))
            roi = cv2.cvtColor(roi,cv2.COLOR_RGB2BGR)
            roi_path =  f'.\static\predict\idimage.jpg'
            cv2.imwrite(roi_path,roi)
            report.append([ timestamp,roi_path,name,score_id,emotion,score_emotion])
        else:
            return "No data found for ID number {}".format(id_num)
        return render_template('displayimage.html',fileupload=True,report = report)
    return render_template('displayimage.html',fileupload=False)
