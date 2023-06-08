from fastapi import APIRouter,HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from bson.objectid import ObjectId

router = APIRouter()

userdb = str("6rucewayne")
pwdb = str("sqHLQjeAiDqPB3qZ")
client = MongoClient("mongodb+srv://6rucewayne:"+pwdb+"@cluster0.muzyzlw.mongodb.net/")
db = client["votes-simple"]
collection =db["votes"]

#Model objects
class Vote(BaseModel):
    name : str
    count : int

#Schema objects
def vote_serializer(vote)->dict():
    return {
        "id":str(vote["_id"]),
        "name":vote["name"],
        "count":vote["count"]
        }

def votes_serializer(votes)->list:
    return [vote_serializer(vote) for vote in votes]

#get all votes    
@router.get("/vote")
async def root():   
    votes = votes_serializer(collection.find({}))
    if votes:
       return {"status":"OK","data":votes}
    else:
        raise HTTPException(status_code=404,detail="Vote not found")

#Create
@router.post("/vote")
async def create_vote(vote: Vote):
    result = collection.insert_one(vote.dict())
    return {
        "id": str(result.inserted_id),
        "name": vote.name,
        "count": vote.count
    }
#Read
@router.get("/vote/{vote_id}")
async def read_vote(vote_id: str):
    vote = collection.find_one({"_id": ObjectId(vote_id)})
    if vote:
        return {
            "id": str(vote["_id"]),
            "name": vote["name"],
            "count": vote["count"]
        }
    else:
        raise HTTPException(status_code=404,detail="Vote not found")
    
#Update
@router.put("/vote/{vote_id}")
async def update_vote(vote_id: str, vote: Vote):
    result = collection.update_one({"_id": ObjectId(vote_id)}, {"$set": vote.dict(exclude_unset=True)})
    if result.modified_count == 1:
        return {
            "id": vote_id,
            "name": vote.name,
            "count": vote.count
        }
    else:
        raise HTTPException(status_code=404,detail="Vote not found")
    
#Delete
@router.delete("/vote/{vote_id}")
async def delete_vote(vote_id: str):
    result = collection.delete_one({"_id": ObjectId(vote_id)})
    if result.deleted_count == 1:
        return {
            "status": "deleted",
        }
    else:
        raise HTTPException(status_code=404,detail="Vote not found")