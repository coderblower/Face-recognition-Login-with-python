from flask import Blueprint, request, jsonify
import pickle
import numpy as np
from PIL import Image
import io
import base64
import os
import face_recognition

# Path to store enrolled faces
image_folder = 'enrolled_faces'
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# Create a Blueprint for the routes
register_face = Blueprint('register_face', __name__)
login_face = Blueprint('login_face', __name__)

def process_face_frame(frame):
    """Process a single frame and return face encodings."""
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    return face_encodings

# Register face route
@register_face.route('/register_face', methods=['POST'])
def register_face_route():
    enrollment_id = request.form.get('enrollment_id')
    name = request.form.get('name')

    if not enrollment_id or not name:
        return jsonify({"message": "Enrollment ID and name are required"}), 400

    # Initialize a list to store encodings from multiple images
    all_face_encodings = []

    # Check if multiple images are sent in the 'frame' field as files
    if 'frame' in request.files:
        frames = request.files.getlist('frame')  # Use getlist to retrieve all files with the key 'frame'
        for frame_file in frames:
            frame = np.array(Image.open(frame_file))
            face_encodings = process_face_frame(frame)
            if face_encodings:  # If encodings are found, add to the list
                all_face_encodings.extend(face_encodings)
    
    # Check if multiple base64 images are sent in 'frame' field in form data
    elif 'frame' in request.form:
        frames_data = request.form.getlist('frame')  # Use getlist to retrieve all frames in form
        for frame_data in frames_data:
            frame_bytes = base64.b64decode(frame_data)
            frame = np.array(Image.open(io.BytesIO(frame_bytes)))
            face_encodings = process_face_frame(frame)
            if face_encodings:
                all_face_encodings.extend(face_encodings)
    
    else:
        return jsonify({"message": "Frame data not provided"}), 400

    # Check if we have collected any face encodings from the frames
    if all_face_encodings:
        # Store the combined encodings in a file for the enrollment ID
        with open(f'{image_folder}/{enrollment_id}_face_encoding.pkl', 'wb') as f:
            pickle.dump(all_face_encodings, f)
        return jsonify({"message": f"Face registered for {name} (ID: {enrollment_id})"}), 200
    else:
        return jsonify({"message": "No face detected in the provided images."}), 400



@login_face.route('/login_face', methods=['POST'])
def login_face_route():
    # Get the enrollment_id if specified (though it won't be used for finding match)
    enrollment_id = request.form.get('enrollment_id')  

    # Check if 'frame' data is provided in either file upload or base64
    if 'frame' in request.files:
        frame_file = request.files['frame']
        frame = np.array(Image.open(frame_file))
    elif 'frame' in request.form:
        frame_data = request.form.get('frame')
        frame_bytes = base64.b64decode(frame_data)
        frame = np.array(Image.open(io.BytesIO(frame_bytes)))
    else:
        return jsonify({"message": "Frame data not provided"}), 400

    # Process the frame to get face encodings
    face_encodings = process_face_frame(frame)
    if len(face_encodings) == 0:
        return jsonify({"message": "No face detected."}), 400

    # Set a tolerance for face matching
    tolerance = 0.4  # Adjust as needed for matching precision

    # Loop through each .pkl file in the folder
    for file_name in os.listdir(image_folder):
        if file_name.endswith('_face_encoding.pkl'):
            file_path = os.path.join(image_folder, file_name)
            
            try:
                # Load stored face encodings from file
                with open(file_path, 'rb') as f:
                    stored_face_encodings = pickle.load(f)

                # Calculate the face distance for the first encoding
                distances = face_recognition.face_distance(stored_face_encodings, face_encodings[0])
                min_distance = min(distances)

                # Check if any distance is within tolerance
                if min_distance <= tolerance:
                    # Extract enrollment_id from the file name (remove "_face_encoding.pkl" suffix)
                    matched_enrollment_id = file_name.replace('_face_encoding.pkl', '')
                    return jsonify({"message": "Login successful!", "enrollment_id": matched_enrollment_id}), 200

            except Exception as e:
                print(f"Error loading file {file_name}: {e}")
                continue

    # If no match is found, return "Face not recognized"
    return jsonify({"message": "Face not recognized."}), 401
