from flask import Flask, request, jsonify
import face_recognition
import os
import pickle
import numpy as np
import io
from PIL import Image
import base64

app = Flask(__name__)

# Path to store enrolled faces
image_folder = 'enrolled_faces'
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

def process_face_frame(frame):
    """Process a single frame and return face encodings."""
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    return face_encodings

def verify_liveness(frame):
    """
    A simple liveness check to verify if the image contains a real person.
    This is a placeholder. For real-world use, implement advanced liveness detection techniques.
    """
    return len(face_recognition.face_locations(frame)) > 0  # Check if faces are detected

@app.route('/register_face', methods=['POST'])
def register_face():
    enrollment_id = request.form.get('enrollment_id')
    name = request.form.get('name')

    if 'frame' in request.files:
        frame_file = request.files['frame']
        frame = np.array(Image.open(frame_file))
    elif 'frame' in request.form:
        frame_data = request.form.get('frame')
        frame_bytes = base64.b64decode(frame_data)
        frame = np.array(Image.open(io.BytesIO(frame_bytes)))
    else:
        return jsonify({"message": "Frame data not provided"}), 400

    face_encodings = process_face_frame(frame)

    if face_encodings:
        with open(f'{image_folder}/{enrollment_id}_face_encoding.pkl', 'wb') as f:
            pickle.dump(face_encodings, f)
        return jsonify({"message": f"Face registered for {name} (ID: {enrollment_id})"}), 200
    else:
        return jsonify({"message": "No face detected in the image."}), 400

@app.route('/login_face', methods=['POST'])
def login_face():
    if 'frame' in request.files:
        frame_file = request.files['frame']
        frame = np.array(Image.open(frame_file))
    elif 'frame' in request.form:
        frame_data = request.form.get('frame')
        frame_bytes = base64.b64decode(frame_data)
        frame = np.array(Image.open(io.BytesIO(frame_bytes)))
    else:
        return jsonify({"message": "Frame data not provided"}), 400

    face_encodings = process_face_frame(frame)
    
    if len(face_encodings) == 0:
        return jsonify({"message": "No face detected."}), 400

    tolerance = 0.4  # Lower tolerance for more precise matching




    try:
        with open(file_path, 'rb') as f:
            stored_face_encodings = pickle.load(f)
            
            
            # Check each stored encoding to find the closest match based on distance
            distances = face_recognition.face_distance(stored_face_encodings, face_encodings[0])
            min_distance = min(distances)

            # Check if the minimum distance is within our tolerance
            if min_distance <= tolerance:
                return jsonify({"message": "Login successful!"}), 200

        return jsonify({"message": "Face not recognized."}), 401
    
    
    except FileNotFoundError:
        return jsonify({"message": "No stored face encodings found."}), 404



  

if __name__ == '__main__':
    app.run(debug=True)
