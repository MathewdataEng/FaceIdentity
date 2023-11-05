import numpy as np
import pickle
import cv2
from keras.models import load_model
from PIL import Image
from mtcnn_cv2 import MTCNN
import datetime

# Load all models
mtcnn = MTCNN()
pkl_filename = './model/faces_emotion.pkl'
with open(pkl_filename, 'rb') as file:
    emotion_model = pickle.load(file)
pkl_filename = './model/outputemotion_enc.pkl'
with open(pkl_filename, 'rb') as file:
    output_enc_emotion = pickle.load(file)

pkl_filename = './model/faces_svm.pkl'
with open(pkl_filename, 'rb') as file:
    id_model = pickle.load(file)
pkl_filename = './model/output_enc.pkl'
with open(pkl_filename, 'rb') as file:
    output_enc_id = pickle.load(file)
facenet_model = load_model('./model/facenet_keras.h5')
facenet_model.load_weights('./model/encoder.h5')
# facenet_model._make_predict_function()
def get_embedding(face_pixels):
    # scale pixel values
    face_pixels = face_pixels.astype('float32')
    # standardize pixel values across channels (global)
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std
    # transform face into one sample
    samples = np.expand_dims(face_pixels, axis=0)
    # make prediction to get embedding
    yhat = facenet_model.predict(samples)
    return yhat[0]

def faceRecognitionPipeline(filename,path=True):
    dest_size = (160, 160)
    if path:
        # step-01: read image
        img = cv2.imread(filename) # BGR
    else:
        img = filename # array
    pixels = img.copy()
    # step-03: crop the face MTCNN
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    detections = mtcnn.detect_faces(img)
    img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    predictions = []
    for det in detections :
        x, y, w, h = det['box']
        x1, y1 = abs(x), abs(y)
        x2, y2 = x1 + w, y1 + h
        roi = pixels[y1:y2, x1:x2]
        image = Image.fromarray(roi)
        roi_rgb =  cv2.cvtColor(roi,cv2.COLOR_BGR2RGB) 
        h_roi, w_roi, dim = roi_rgb.shape
        # Convert the image to a bytes object
        roi_rgb = roi_rgb.tobytes()
        image = image.resize(dest_size)
        # Get Face embedding
        face_emb =  get_embedding( np.array(image))
        face_emb = np.expand_dims(face_emb, axis=0)
        
        # Predict ID via  SVM
        y_hat_id = id_model.predict(face_emb)
        prob_score = id_model.predict_proba(face_emb)
        prob_score_max_id = prob_score.max()
        predict_names = output_enc_id.inverse_transform(y_hat_id)
        #Predict emotion via SVM
        y_hat_emotion = emotion_model.predict(face_emb)
        prob_score_emotion = emotion_model.predict_proba(face_emb)
        prob_score_max_emotion = prob_score_emotion.max()
        predict_emotion = output_enc_emotion.inverse_transform(y_hat_emotion)
        # step-11: generate report
        text1 = "%s : %d"%(predict_names[0],prob_score_max_id*100)+"%"
        text2 = "%s : %d "%(predict_emotion[0],prob_score_max_emotion*100) + '%'
        # defining color based on results
        if prob_score_max_id*100 > 70:
            cv2.putText(img,text1,(x-10,y-35),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),5)
        else:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),5)
            cv2.putText(img,'Unknown',(x-10,y-35),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
            predict_names[0] = 'Unknown'
        if prob_score_max_emotion*100 > 60:
            cv2.putText(img,text2,(x-10,y-5),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,10),2)
        else:
            cv2.putText(img,'Unknown',(x-10,y-5),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
        image_report = img.copy()
        h_image, w_image, dim = image_report.shape
        image_report = image_report.tobytes()
        timestamp = datetime.datetime.now()
        output = {
            'timestamp':timestamp,
            'image':image_report,
            'h_image':h_image,
            'w_image':w_image,
            'roi':roi_rgb,
            'h_roi':h_roi,
            'w_roi':w_roi,
            'prediction_name':predict_names[0],
            'score_id':prob_score_max_id,
            'prediction_emotion':predict_emotion[0],
            'score_emotion':prob_score_max_emotion
        }

        predictions.append(output)

    return img, predictions    