from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="ClassTrack API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "ClassTrack API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Backend is working"}

@app.get("/api/students")
async def get_students():
    return {"students": []}

@app.get("/api/faculty")
async def get_faculty():
    return {"faculty": []}

@app.post("/api/students")
async def create_student(student: dict):
    return {"message": "Student created", "student": student}

@app.post("/api/faculty")
async def create_faculty(faculty: dict):
    return {"message": "Faculty created", "faculty": faculty}

if __name__ == "__main__":
    uvicorn.run("main_minimal:app", host="0.0.0.0", port=5001, reload=True)