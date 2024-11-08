import os

class Config:
    IMAGE_FOLDER = os.path.join(os.getcwd(), 'enrolled_faces')
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)
