
from fastapi import FastAPI , Query , Path , Body ,Cookie , Header , UploadFile , File, HTTPException , params as Params, Depends, status 
from enum import Enum
from datetime import datetime
from typing import Optional , Annotated , IO, List , Dict
from pydantic import BaseModel , PydanticUserError , Field , EmailStr 
import uvicorn
import filetype
import os
app = FastAPI()

def validate_file_type(file : IO):
    FileSize = 600000000
    acceptedFileTypes = ["image/png", "image/jpeg", "image/jpg", "image/heic", "image/heif", "image/heics", "png",
                          "jpeg", "jpg", "heic", "heif", "heics" 
                          ]
    file_info = filetype.guess(file.file)
    if file_info is None :
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unable to determine file type",)
    detectedContentType = file_info.extension.lower()
    if (
        file.content_type not in acceptedFileTypes 
        or detectedContentType not in acceptedFileTypes

    ):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type",
        )
    
    realFileSize = 0
    for chunk in file.file:
        realFileSize += len(chunk)
        if realFileSize > FileSize :
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail= "file size is too large")
        



def get_file_info(path: str, filename: str) -> Dict[str, str]:
    """
    Get information about a file
    """
    file_path = os.path.join(path, filename)
    file_info = os.stat(file_path)

    # Get file extension
    file_ext = os.path.splitext(filename)[1]
    if file_ext == '':
        file_ext = 'unknown'

    return {
        "filename": filename,
        "last_modified": datetime.fromtimestamp(file_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
        "extension": file_ext
    }

async def get_files_tree() -> Dict[str, List[Dict[str, str]]]:
    base_path = './uploads'
    files_tree = {}
    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)
        if os.path.isdir(folder_path):
            files_tree[folder] = [get_file_info(folder_path, f) for f in os.listdir(folder_path)]
    return files_tree
@app.post("/upload")
async def createUploadFile(file : UploadFile = File()):
    validate_file_type(file)
    
    try:
        datetoday = datetime.now().strftime('%Y-%m-%d')
        directory = f'./upload/{datetoday}'

        if not os.path.exists(directory) :
            os.makedirs(directory)
        date_time_now = datetime.now().strftime('%H%M%S%f')
        filename = f"{date_time_now}_{file.filename}"
        file_location = f"{directory}/{filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
            
        return {"info": f"file '{filename}' saved at {directory}"}
    except Exception as e:
        return{
            "error  " :str(e),
            "filename " : file.filename,
            "content_type" : file.content_type}




