from fastapi import APIRouter,File,UploadFile,HTTPException,Depends,status
from typing import Annotated
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import aiofiles
import uuid
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import bcrypt
import hashlib


router = APIRouter()

#mount
router.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


#Oauth2PasswordBearer instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#Model User
class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
    "romz": {
        "username": "romz",
        "full_name": "Parinya Kunchai",
        "email": "rmninthailand@gmail.com",
        "hashed_password": "$2b$12$xvsCpt5D.zU908JQwDaMD.pNJeeJpsM9UkSt7c.kooQPD6TrmNGfK",
        "disabled": True,
    },
}
#ัInput check password
def fake_hash_password(password: str):  
    hashpassword = password.encode('utf-8')
    return hashpassword

class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)  
    if not bcrypt.checkpw(hashed_password,user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}

@router.get('/user/hash/{word}')
async def user_hash(word:str):
    passw = word.encode('utf-8')
    mysalt = bcrypt.gensalt()
    pwd_hash = bcrypt.hashpw(passw,mysalt)
    return pwd_hash

#getuser
@router.get("/user/me")
async def read_users_me(current_user: Annotated[User,Depends(get_current_active_user)]):
    return current_user

#counters
@router.get("/picture")
async def count_pictures(token: Annotated[str,Depends(oauth2_scheme)]): #insert oauth
    dir_parth = r'uploads'
    count = 0
    for path in os.listdir(dir_parth):
        if os.path.isfile(os.path.join(dir_parth, path)):
            count += 1
    return {"message":"Total pictures = "+str(count)}

#upload fiess picutres
@router.post("/picture_upload2")
async def post_endpoint(in_file: UploadFile = File(...)):
    random_name = uuid.uuid4()
    async with aiofiles.open(f"uploads/{random_name}.jpg", "wb") as out_file:
        while content := await in_file.read(1024):  # async read chunk
            await out_file.write(content)


    return {"message": "Uploaded","data": str(out_file.name),"Picture":FileResponse(out_file.name)}

#Get picture file
@router.get("/picture/{file_name}")
async def get_picture(file_name:str):
    path =  "uploads/"+file_name+".jpg"
    return FileResponse(path)
#Remove picture file
@router.delete("/picture/{file_name}")
async def delete_picture(file_name:str):
    path="uploads/"+file_name+".jpg"
    if os.path.exists(path):
        os.remove(path)
        return {"message": "Deleted"}
    else:
        raise HTTPException(status_code=404,detail="Not found")