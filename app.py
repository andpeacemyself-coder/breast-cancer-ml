from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.context import CryptContext
from datetime import datetime
import os

BASE_DIR = os.path.dirname(__file__)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'db.sqlite3')}")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Database setup
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    records = relationship("Record", back_populates="owner")

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)

class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_input = Column(Text, nullable=False)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship("User", back_populates="records")

# Create tables
Base.metadata.create_all(bind=engine)

# Helpers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db=None):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()

# Routes
@app.get("/")
def index(request: Request):
    # Landing page
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register")
def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "errors": []})

@app.post("/register")
def register_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), db=Depends(get_db)):
    errors = []
    if len(username) < 3:
        errors.append("Username must be at least 3 characters")
    if "@" not in email or len(email) < 5:
        errors.append("Enter a valid email address")
    if len(password) < 6:
        errors.append("Password must be at least 6 characters")
    if db.query(User).filter((User.username == username) | (User.email == email)).first():
        errors.append("User with that username or email already exists")
    if errors:
        return templates.TemplateResponse("register.html", {"request": request, "errors": errors})
    user = User(username=username, email=email, password_hash=pwd_context.hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/login")
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
def login_post(request: Request, username: str = Form(...), password: str = Form(...), db=Depends(get_db)):
    user = db.query(User).filter((User.username == username) | (User.email == username)).first()
    if not user or not user.verify_password(password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

@app.get("/dashboard")
def dashboard(request: Request, db=Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.get("/records")
def records_get(request: Request, db=Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    records = db.query(Record).filter(Record.user_id == user.id).order_by(Record.created_at.desc()).all()
    return templates.TemplateResponse("records.html", {"request": request, "user": user, "records": records, "errors": []})

@app.post("/records")
def records_post(request: Request, test_input: str = Form(...), result: str = Form(None), db=Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    errors = []
    if not test_input or len(test_input.strip()) < 3:
        errors.append("Test input must be at least 3 characters")
    if errors:
        records = db.query(Record).filter(Record.user_id == user.id).order_by(Record.created_at.desc()).all()
        return templates.TemplateResponse("records.html", {"request": request, "user": user, "records": records, "errors": errors})
    record = Record(user_id=user.id, test_input=test_input.strip(), result=(result or ""))
    db.add(record)
    db.commit()
    return RedirectResponse(url="/records", status_code=303)

# Simple startup message
@app.on_event("startup")
def startup_event():
    print("FastAPI app initialized. Visit / to see the landing page.")
