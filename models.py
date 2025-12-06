# models.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    bio = Column(String, nullable=True)

    artworks = relationship("Artwork", back_populates="artist")


class Artwork(Base):
    __tablename__ = "artworks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    artist_id = Column(Integer, ForeignKey("artists.id"))

    artist = relationship("Artist", back_populates="artworks")
    exhibitions = relationship("Exhibition", back_populates="artwork")


class Exhibition(Base):
    __tablename__ = "exhibitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"))

    artwork = relationship("Artwork", back_populates="exhibitions")
