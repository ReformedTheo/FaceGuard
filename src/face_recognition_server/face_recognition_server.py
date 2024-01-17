import face_recognition
import os
import sys
import cv2
import numpy as np
import math
import socket
import threading
import json

def face_confidence(face_distance, face_match_threshold=0.6):
    range = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (range * 2.0)

    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + '%'
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + '%'

class FaceRecognitionServer:
    def __init__(self):
        self.encode_faces()
        self.start_server()

    def encode_faces(self):
        self.known_face_encodings = []
        self.known_face_names = []
        for image in os.listdir('faces'):
            face_image = face_recognition.load_image_file(f'faces/{image}')
            face_encoding = face_recognition.face_encodings(face_image)[0]
            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(image.split('.')[0])

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', 9091))
        server_socket.listen(5)
        print("Face Recognition Server running...")

        while True:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        face_data = self.run_recognition_once()
        client_socket.sendall(json.dumps(face_data).encode())
        client_socket.close()

    def run_recognition_once(self):
        video_capture = cv2.VideoCapture(0)
        ret, frame = video_capture.read()
        if not ret:
            sys.exit('Could not read from camera.')

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_data = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = 'Unknown'
            confidence = 'Unknown'

            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
                confidence = face_confidence(face_distances[best_match_index])

            face_data.append({'name': name, 'confidence': confidence})

        video_capture.release()
        return face_data

if __name__ == '__main__':
    fr_server = FaceRecognitionServer()
