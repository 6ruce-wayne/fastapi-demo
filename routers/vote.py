from fastapi import APIRouter,HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from bson.objectid import ObjectId

router = APIRouter()

client = MongoClient("mongodb://localhost:27017")
db = client["votes"]
collection =db["votes"]

class Vote(BaseModel):
    name : str
    count : int

def vote_serializer(Vote)->dict():
    return {"id":Vote._id,"name":Vote.name,"count":Vote.count}

def votes_serializer(votes)->list:
    return [vote_serializer(vote) for vote in votes]

    
@router.get("/vote")
async def root():   
    votes = collection.find({}).to_list(1000)
    if votes:
       return {
            "id": str(votes["_id"]),
            "name": votes["name"],
            "count": votes["count"]
        }
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