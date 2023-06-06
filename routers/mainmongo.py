from fastapi import FastAPI,HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from bson.objectid import ObjectId

app = FastAPI()

client = MongoClient("mongodb://localhost:27017")
db = client["votes"]
collection =db["votes"]

class Vote(BaseModel):
    name : str
    count : int
    
@app.get("/")
async def root():
    return {"Hello": "World"}

#Create
@app.post("/vote")
async def create_vote(vote: Vote):
    result = collection.insert_one(vote.dict())
    return {
        "id": str(result.inserted_id),
        "name": vote.name,
        "count": vote.count
    }
#Read
@app.get("/vote/{vote_id}")
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
@app.put("/vote/{vote_id}")
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
@app.delete("/vote/{vote_id}")
async def delete_vote(vote_id: str):
    result = collection.delete_one({"_id": ObjectId(vote_id)})
    if result.deleted_count == 1:
        return {
            "status": "deleted",
        }
    else:
        raise HTTPException(status_code=404,detail="Vote not found")