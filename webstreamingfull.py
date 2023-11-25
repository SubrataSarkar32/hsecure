from flask import Flask, render_template, Response, stream_with_context, url_for
import cv2
import datetime
import numpy as np
# from flask_bcrypt import Bcrypt
# from flask_mail import Mail
# from dotenv import load_dotenv
from pathlib import Path
from pushbullet import Pushbullet
import os

# db url from env
# dotenv_path = Path('/home/subrata32/.env')
# load_dotenv(dotenv_path=dotenv_path)

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt", "MobileNetSSD_deploy.caffemodel")

app = Flask(__name__)

# This values need to be stored in environment and called
# Using dummy values for now
# Configuration of a Gmail account for sending mails

app.config['MAIL_SERVER'] = 'smtpout.secureserver.net'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

if not os.getenv("PB_API_KEY"):
    raise RuntimeError("PB_API_KEY is not set")

# if not os.getenv("MAIL_USERNAME"):
#     raise RuntimeError("MAIL_USERNAME is not set")

# app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")

# if not os.getenv("MAIL_PASSWORD"):
#     raise RuntimeError("MAIL_PASSWORD is not set")

# app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
# app.config['ADMINS'] = [os.getenv("MAIL_USERNAME")]

# confirm_token_salt = 'random-confirm-mail-1'

# reset_token_salt = 'random-reset-2'
# mail = Mail(app)

pb = Pushbullet(os.getenv("PB_API_KEY"))

camera = cv2.VideoCapture(0)  # I can't use a local webcam video or a local source video, I must receive it by http in some api(flask) route
timer = 0
runner = 0

def gen_frames():  # generate frame by frame from camera
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            global timer
            global runner
            # describe the type of  
            # font you want to display
            font = cv2.FONT_HERSHEY_SIMPLEX
  
            # Get date and time and  
            # save it inside a variable 
            dt = datetime.datetime.now()
            # grab the frame dimensions and convert it to a blob
            (h, w) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                0.007843, (300, 300), 127.5)
            # pass the blob through the network and obtain the detections and
            # predictions
            net.setInput(blob)
            detections = net.forward()
            person = False

            # loop over the detections
            for i in np.arange(0, detections.shape[2]):
                # extract the confidence (i.e., probability) associated with
                # the prediction
                confidence = detections[0, 0, i, 2]
                # filter out weak detections by ensuring the `confidence` is
                # greater than the minimum confidence
                if confidence > 0.7:
                    # extract the index of the class label from the
                    # `detections`, then compute the (x, y)-coordinates of
                    # the bounding box for the object
                    idx = int(detections[0, 0, i, 1])
                    if CLASSES[idx] == "person":
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype("int")
                        # draw the prediction on the frame
                        label = "{}: {:.2f}%".format(CLASSES[idx],
                            confidence * 100)
                        frame = cv2.rectangle(frame, (startX, startY), (endX, endY),
                            COLORS[idx], 2)
                        y = startY - 15 if startY - 15 > 15 else startY + 15
                        frame = cv2.putText(frame, label, (startX, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
                        person = True
  
            # put the dt variable over the 
            # video frame 
            endtime = datetime.datetime.now()
            time_to_process = endtime - dt
            frame = cv2.putText(frame, str(time_to_process),
                                (100, 300),
                                font, 0.5,
                                (0, 255, 0),
                                2)
            frame = cv2.putText(frame, str(dt).split(".")[0],
                                (10, 100),
                                font, 0.5,
                                (255, 0, 0),
                                2)
            ret, buffer = cv2.imencode('.jpg', frame)
            if person:
                if timer <10:
                    timer += 1
                elif timer == 10:
                    cv2.imwrite(os.path.join("/srv/dev-disk-by-uuid-A0FC80EAFC80BC52/pi4shared/cctv", dt.strftime("%Y_%m_%d-%H_%M_%S")+".jpg"), frame)
                    push = pb.push_note("hsecure", "Person detected at home")
                    with open(os.path.join("/srv/dev-disk-by-uuid-A0FC80EAFC80BC52/pi4shared/cctv", dt.strftime("%Y_%m_%d-%H_%M_%S")+".jpg"), "rb") as pic:
                        file_data = pb.upload_file(pic, dt.strftime("%Y_%m_%d-%H_%M_%S")+".jpg")
                    push = pb.push_file(**file_data)
                    timer += 1
                elif timer > 10 and timer < 100:
                    timer += 1
                else:
                    timer = 0
            else:
                if timer >= 10:
                   timer = 0
                else:
                   timer = 0
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(stream_with_context(gen_frames()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index2.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
