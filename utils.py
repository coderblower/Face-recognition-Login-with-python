import face_recognition
import numpy as np
from PIL import Image
import io
import base64

def process_face_frame(frame):
    """Process a single frame and return face encodings."""
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    return face_encodings

def decode_frame(frame_data):
    """Decode base64 frame data into an image."""
    frame_bytes = base64.b64decode(frame_data)
    return np.array(Image.open(io.BytesIO(frame_bytes)))

def handle_uploaded_image(frame_file=None, frame_data=None):
    """Handle both file and base64 frame inputs."""
    if frame_file:
        return np.array(Image.open(frame_file))
    elif frame_data:
        return decode_frame(frame_data)
    return None
