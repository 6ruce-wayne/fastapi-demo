from fastapi import APIRouter,File,UploadFile,HTTPException
from typing import Annotated
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import aiofiles
import uuid
import os

router = APIRouter()

router.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@router.get("/picture")
async def count_pictures():
    dir_parth = r'uploads'
    count = 0
    for path in os.listdir(dir_parth):
        if os.path.isfile(os.path.join(dir_parth, path)):
            count += 1
    return {"message":"Total pictures = "+str(count)}


@router.post("/picture_upload2")
async def post_endpoint(in_file: UploadFile = File(...)):
    random_name = uuid.uuid4()
    async with aiofiles.open(f"uploads/{random_name}.jpg", "wb") as out_file:
        while content := await in_file.read(1024):  # async read chunk
            await out_file.write(content)


    return {"message": "Uploaded","data": str(out_file.name),"Picture":FileResponse(out_file.name)}

@router.get("/picture/{file_name}")
async def get_picture(file_name:str):
    path =  "uploads/"+file_name+".jpg"
    return FileResponse(path)

@router.delete("/picture/{file_name}")
async def delete_picture(file_name:str):
    path="uploads/"+file_name+".jpg"
    if os.path.exists(path):
        os.remove(path)
        return {"message": "Deleted"}
    else:
        raise HTTPException(status_code=404,detail="Not found")