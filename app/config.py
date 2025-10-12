import os

class Config:
    SECRET_KEY = "change-me"
    DATA_DIR = "data"
    ALLOWED_IMAGE_EXT = {"jpg","jpeg","png","gif","webp"}
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads", "equipment")
