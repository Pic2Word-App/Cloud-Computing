from sqlalchemy import Column, DateTime, Integer, String, Float

from .database import Base

class jenis_kelamin(enumerate):
  lakilaki = "Laki-laki"
  perempuan = "Perempuan"

class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    jenis_kelamin = Column(String, nullable=True)
    tanggal_lahir = Column(DateTime, nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
class Token(Base):
    __tablename__ = "token"
    
    token_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    access_token = Column(String)
    token_type = Column(String)
    
    
class Image(Base):
    __tablename__ = "image"
    
    image_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    image_url = Column(String)
    image_name = Column(String)
    prediction = Column(String)
    translate = Column(String)
    
    