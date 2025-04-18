from fastapi import FastAPI, status, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor      #gives column names and value
import models
from database import SessionLocal, Base, get_db, engine
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

#Validation of body in postman
class Schema(BaseModel):
    title: str
    content: str
    published: bool = True          #default True

while True:
    try:
        connection = psycopg2.connect(host=os.getenv("HOST"),database=os.getenv("DATABASE"),
                                user=os.getenv("USER"),password=os.getenv("PASSWORD"), cursor_factory=RealDictCursor)
        cursor = connection.cursor()
        print("Database connection successful")
        break
    except Exception as error:
        print(f"Database connection failed. Error: {error}")


posts_list = [{"title":"pokemon","content":"then we fight","id":1}]


# SQLAlchemy
@app.get("/sqlalchemy")
def sql_get(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()

    return {"data": posts}


@app.post("/sqlalchemy", status_code=status.HTTP_201_CREATED)
def sql_post(post: Schema, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())  # unpacks post.dict to not manually type post.title, post.content, etc.
    db.add(new_post)
    db.commit()  # similar to connection.commit()
    db.refresh(new_post)  # similar to RETURNING *

    return {"data": new_post}


@app.get("/sqlalchemy/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()  # similar to WHERE id = id  -  filter by models.post.id == id, also finds the first instance - first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

    return {"data": post}


@app.delete("/sqlalchemy/{id}")
def delete(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail=f"Post with id: {id} not found")
    db.delete(post)
    db.commit()

    return {"data": f"Post with id {id} successfully deleted"}


@app.put("/sqlalchemy/{id}")
def update(id: int, post: Schema, db: Session = Depends(get_db)):
    update_post = db.query(models.Post).filter(models.Post.id == id)
    first_post = update_post.first()
    if not first_post:
        raise HTTPException(status_code=404, detail=f"Post with id: {id} not found")

    update_post.update(post.dict())
    db.commit()
    return {"data": update_post.first()}