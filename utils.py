import os

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)
def upload_to_cloudinary(file):
    result = cloudinary.uploader.upload(file.file)
    return result["secure_url"]

def upload_file_to_cloudinary(file):
    result = cloudinary.uploader.upload(
        file.file,
        resource_type="raw",
        folder="materials",
        public_id=file.filename,
        overwrite=True,
        use_filename=True,
    )
    return result["secure_url"]