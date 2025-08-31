import cv2
import numpy as np
import face_recognition
import os
import pandas as pd
import datetime


path = 'students'

images = []
classNames = []


try:
    for img in os.listdir(path):

        if img.lower().endswith(('.png', '.jpg', '.jpeg')):
            image = cv2.imread(f'{path}/{img}')
            images.append(image)
            classNames.append(os.path.splitext(img)[0])
except FileNotFoundError:
    print(f"Error: The 'students' directory was not found. Please create it and add face images.")
    exit()

print(f"Loaded class names: {classNames}")

scale = 0.25
box_multiplier = 1 / scale

def find_encodings(images):

    encodeList = []
    for img in images:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img_rgb)[0]
        encodeList.append(encode)
    return encodeList

knownEncodes = find_encodings(images)
print('Encoding Complete')

cap = None
for i in range(4):  
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  
    if cap.isOpened():
        success, frame = cap.read()
        if success:
            print(f"Camera found at index {i}.")
            break
        else:
            print(f"Camera found at index {i} but failed to read frame. Trying next index.")
            cap.release()
            cap = None
    else:
        print(f"No camera found at index {i}. Trying next index.")
        cap = None

if cap is None:
    print("Failed to read from any camera. Exiting.")
    exit()
    
csv_file = 'attendance_log.csv'

if not os.path.exists(csv_file):

    data = {'Name': classNames, 'Timestamp': [''] * len(classNames), 'Authenticated': ['No'] * len(classNames)}
    df = pd.DataFrame(data)
    
else:
    
    df = pd.read_csv(csv_file)
    
    if 'Authenticated' not in df.columns:
        df['Authenticated'] = 'No'
    
    if 'Timestamp' not in df.columns:
        df['Timestamp'] = ''
    
    current_students = df['Name'].str.lower().tolist()
    for student in classNames:
        if student.lower() not in current_students:
            new_row = pd.DataFrame([{'Name': student, 'Timestamp': '', 'Authenticated': 'No'}])
            df = pd.concat([df, new_row], ignore_index=True)
    
df.to_csv(csv_file, index=False)

while True:
    success, img = cap.read()
    if not success:
        print("Failed to read from camera. Exiting.")
        break

    
    current_image_resized = cv2.resize(img, (0, 0), None, scale, scale)
    current_image_rgb = cv2.cvtColor(current_image_resized, cv2.COLOR_BGR2RGB)

    
    face_locations = face_recognition.face_locations(current_image_rgb, model='hog')
    face_encodes = face_recognition.face_encodings(current_image_rgb, face_locations)

    for encodeFace, faceLocation in zip(face_encodes, face_locations):
        matches = face_recognition.compare_faces(knownEncodes, encodeFace, tolerance=0.6)
        faceDis = face_recognition.face_distance(knownEncodes, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()


            if name.lower() in df['Name'].str.lower().values:
              
                if df.loc[df['Name'].str.lower() == name.lower(), 'Authenticated'].iloc[0] != 'Yes':
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                 
                    df.loc[df['Name'].str.lower() == name.lower(), 'Timestamp'] = timestamp
                    df.loc[df['Name'].str.lower() == name.lower(), 'Authenticated'] = 'Yes'
                    df.to_csv(csv_file, index=False)
                    print(f"Authentication recorded for {name} at {timestamp}")

            y1, x2, y2, x1 = faceLocation
            y1, x2, y2, x1 = int(y1 * box_multiplier), int(x2 * box_multiplier), int(y2 * box_multiplier), int(
                x1 * box_multiplier)

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 2)

    cv2.imshow('Webcam Authentication', img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
