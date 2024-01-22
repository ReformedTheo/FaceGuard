import face_recognition
import cv2
import os
import pymysql
from datetime import datetime

class SimpleFaceRecognizer:
    def _init_(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()
        print("Face Recognition Server running...")

    def load_known_faces(self):
        for image_name in os.listdir('faces'):
            image_path = os.path.join('faces', image_name)
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)[0]

            self.known_face_encodings.append(encoding)
            self.known_face_names.append(image_name)

    def recognize_faces(self):
        video_capture = cv2.VideoCapture(0)

        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                name = "Unknown"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]

                top, right, bottom, left = [coordinate * 4 for coordinate in face_location]
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)

            cv2.imshow('Face Recognition', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Quit app")
                break
            elif key == ord('r'):
                self.send_face_data(name)

        video_capture.release()
        cv2.destroyAllWindows()

    def send_face_data(self, face_data):
        """
        Insert face data into the MySQL database.
            """
        try:
            con = pymysql.connect(host='database-1.cvm0aqq86tlh.sa-east-1.rds.amazonaws.com', user='admin',password='Chess.com2409',database='rfid_app', port=3306)
            # Creating a cursor object using the cursor() method
            with con.cursor() as cursor:
                    # SQL query to fetch the name of the face with ID 0
                    query = "UPDATE last_face SET name = %s WHERE id = 1"
                    # Executing the query
                    cursor.execute(query, (face_data))

                    # Fetching the result
                    result = cursor.fetchone()
                    print(f"teoricamente rodou a Query... {result[0]}")
                    return result[0]

        except pymysql.MySQLError as e:
            print("Error while connecting to MySQL", e)
            return None

        finally:
            # Closing the connection
            if con:
                con.close()

if __name__ == '_main_':
    recognizer = SimpleFaceRecognizer()
    recognizer.recognize_faces()