from fastapi import FastAPI
from fastapi import Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Task Manager Backend!"}

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


# Replace these with your MySQL database details
DATABASE_URL = "mysql+pymysql://root:dbuserdbuser@localhost:3306/learn_db"

# Connect to the MySQL database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Define the Task model
class Task(Base):
    __tablename__ = "tasks"  # Ensure this matches the table name in your MySQL database
    id = Column(Integer, primary_key=True, index=True)  # Primary key column
    title = Column(String(255), index=True)  # Matches a VARCHAR(255) column in your database
    description = Column(String(1024))  # Matches a VARCHAR(1024) column in your database

# Reflect existing database schema or create missing tables
Base.metadata.create_all(bind=engine)

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for request body
class TaskCreate(BaseModel):
    title: str
    description: str

# Endpoint to fetch all tasks
@app.get("/tasks/")
def read_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks

@app.post("/tasks/")
def create_new_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(title=task.title, description=task.description)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/tasks/{task_id}")
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    task_to_update = db.query(Task).filter(Task.id == task_id).first()
    if task_to_update is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task_to_update.title = task.title
    task_to_update.description = task.description
    db.commit()
    db.refresh(task_to_update)
    return task_to_update

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task_to_delete = db.query(Task).filter(Task.id == task_id).first()
    if task_to_delete is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task_to_delete)
    db.commit()
    return task_to_delete