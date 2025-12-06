# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from datetime import datetime

# ------------------------
# Database setup
# ------------------------
DATABASE_URL = "sqlite:///./artlog.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ------------------------
# Models - MUST MATCH YOUR DATABASE SCHEMA
# ------------------------
class Artist(Base):
    __tablename__ = "artists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    country = Column(String)
    art_style = Column(String)

class Artwork(Base):
    __tablename__ = "artworks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    year = Column(Integer)
    image_url = Column(String)
    artist_id = Column(Integer, ForeignKey('artists.id'))
    created_at = Column(DateTime)

class Exhibition(Base):
    __tablename__ = "exhibitions"
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String)  # From your database screenshot
    theme = Column(String)     # From your database screenshot
    date = Column(DateTime)    # From your database screenshot
    artwork_id = Column(Integer, ForeignKey('artworks.id'))
    created_at = Column(DateTime)

# DON'T create tables - they already exist!
# Base.metadata.create_all(bind=engine)

# ------------------------
# Pydantic Schemas - FIXED
# ------------------------
class ArtistCreate(BaseModel):
    name: str
    country: str
    art_style: str

class ArtistResponse(ArtistCreate):
    id: int
    class Config:
        orm_mode = True  # Change to from_attributes=True if using Pydantic V2

class ArtworkCreate(BaseModel):
    title: str
    description: Optional[str] = None
    year: int
    image_url: Optional[str] = None
    artist_id: int

class ArtworkResponse(ArtworkCreate):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        orm_mode = True  # Change to from_attributes=True if using Pydantic V2

class ExhibitionCreate(BaseModel):
    location: str
    theme: str
    date: str  # Frontend sends as string
    artwork_id: Optional[int] = None

class ExhibitionResponse(BaseModel):
    id: int
    location: str
    theme: str
    date: str  # Will convert datetime to string
    artwork_id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True  # Change to from_attributes=True if using Pydantic V2
    
    @validator('date', pre=True)
    def convert_datetime_to_str(cls, v):
        if isinstance(v, datetime):
            # Return ISO format string
            return v.isoformat()
        return v

# ------------------------
# Login schema
# ------------------------
class LoginData(BaseModel):
    username: str
    profile_picture: str

# ------------------------
# FastAPI app
# ------------------------
app = FastAPI(title="Art-log Backend")

# ------------------------
# CORS setup
# ------------------------
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# Dependency
# ------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------
# Login route
# ------------------------
@app.post("/login")
def login(data: LoginData):
    if data.username.strip() == "":
        raise HTTPException(status_code=400, detail="Username is required")
    return {
        "message": "Login successful",
        "username": data.username,
        "profile_picture": data.profile_picture
    }

# ------------------------
# Artist routes
# ------------------------
@app.post("/artists/", response_model=ArtistResponse)
def create_artist(artist: ArtistCreate, db: Session = Depends(get_db)):
    db_artist = Artist(**artist.dict())
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist

@app.get("/artists/{artist_id}", response_model=ArtistResponse)
def read_artist(artist_id: int, db: Session = Depends(get_db)):
    db_artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not db_artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return db_artist

@app.get("/artists/", response_model=List[ArtistResponse])
def read_artists(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Artist).offset(skip).limit(limit).all()

# Update Artist route
@app.put("/artists/{artist_id}", response_model=ArtistResponse)
def update_artist(artist_id: int, artist: ArtistCreate, db: Session = Depends(get_db)):
    db_artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not db_artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    
    for key, value in artist.dict().items():
        setattr(db_artist, key, value)
    
    db.commit()
    db.refresh(db_artist)
    return db_artist

# Delete Artist route
@app.delete("/artists/{artist_id}")
def delete_artist(artist_id: int, db: Session = Depends(get_db)):
    db_artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not db_artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    
    db.delete(db_artist)
    db.commit()
    return {"message": "Artist deleted successfully"}

# ------------------------
# Artwork routes
# ------------------------
@app.post("/artworks/", response_model=ArtworkResponse)
def create_artwork(artwork: ArtworkCreate, db: Session = Depends(get_db)):
    db_artwork = Artwork(**artwork.dict())
    db.add(db_artwork)
    db.commit()
    db.refresh(db_artwork)
    return db_artwork

@app.get("/artworks/{artwork_id}", response_model=ArtworkResponse)
def read_artwork(artwork_id: int, db: Session = Depends(get_db)):
    db_artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not db_artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    return db_artwork

@app.get("/artworks/", response_model=List[ArtworkResponse])
def read_artworks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Artwork).offset(skip).limit(limit).all()

# Update Artwork route
@app.put("/artworks/{artwork_id}", response_model=ArtworkResponse)
def update_artwork(artwork_id: int, artwork: ArtworkCreate, db: Session = Depends(get_db)):
    db_artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not db_artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    for key, value in artwork.dict().items():
        setattr(db_artwork, key, value)
    
    db.commit()
    db.refresh(db_artwork)
    return db_artwork

# Delete Artwork route
@app.delete("/artworks/{artwork_id}")
def delete_artwork(artwork_id: int, db: Session = Depends(get_db)):
    db_artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not db_artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    db.delete(db_artwork)
    db.commit()
    return {"message": "Artwork deleted successfully"}

# ------------------------
# Exhibition routes - FIXED
# ------------------------
@app.post("/exhibitions/", response_model=ExhibitionResponse)
def create_exhibition(exhibition: ExhibitionCreate, db: Session = Depends(get_db)):
    try:
        # Parse date string to datetime
        date_obj = datetime.fromisoformat(exhibition.date.replace('Z', '+00:00'))
    except:
        try:
            date_obj = datetime.strptime(exhibition.date, "%Y-%m-%d")
        except:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD or ISO format")
    
    db_exhibition = Exhibition(
        location=exhibition.location,
        theme=exhibition.theme,
        date=date_obj,
        artwork_id=exhibition.artwork_id,
        created_at=datetime.utcnow()
    )
    db.add(db_exhibition)
    db.commit()
    db.refresh(db_exhibition)
    return db_exhibition

@app.get("/exhibitions/{exhibition_id}", response_model=ExhibitionResponse)
def read_exhibition(exhibition_id: int, db: Session = Depends(get_db)):
    db_exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
    if not db_exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    return db_exhibition

@app.get("/exhibitions/", response_model=List[ExhibitionResponse])
def read_exhibitions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    exhibitions = db.query(Exhibition).offset(skip).limit(limit).all()
    return exhibitions

# Update Exhibition route
@app.put("/exhibitions/{exhibition_id}", response_model=ExhibitionResponse)
def update_exhibition(exhibition_id: int, exhibition: ExhibitionCreate, db: Session = Depends(get_db)):
    db_exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
    if not db_exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    
    try:
        date_obj = datetime.fromisoformat(exhibition.date.replace('Z', '+00:00'))
    except:
        try:
            date_obj = datetime.strptime(exhibition.date, "%Y-%m-%d")
        except:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD or ISO format")
    
    db_exhibition.location = exhibition.location
    db_exhibition.theme = exhibition.theme
    db_exhibition.date = date_obj
    db_exhibition.artwork_id = exhibition.artwork_id
    
    db.commit()
    db.refresh(db_exhibition)
    return db_exhibition

# Delete Exhibition route
@app.delete("/exhibitions/{exhibition_id}")
def delete_exhibition(exhibition_id: int, db: Session = Depends(get_db)):
    db_exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
    if not db_exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    
    db.delete(db_exhibition)
    db.commit()
    return {"message": "Exhibition deleted successfully"}

# ------------------------
# Test endpoint to check if API is working
# ------------------------
@app.get("/")
def read_root():
    return {"message": "Art-log Backend API is running!", "status": "OK"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/debug/exhibitions")
def debug_exhibitions(db: Session = Depends(get_db)):
    """Debug endpoint to see raw exhibition data"""
    exhibitions = db.query(Exhibition).all()
    result = []
    for ex in exhibitions:
        result.append({
            "id": ex.id,
            "location": ex.location,
            "theme": ex.theme,
            "date": ex.date,
            "date_type": type(ex.date).__name__,
            "artwork_id": ex.artwork_id,
            "created_at": ex.created_at
        })
    return result