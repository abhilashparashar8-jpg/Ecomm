from sqlalchemy import Column, Integer, String, Float, Text
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    youtube_id = Column(String(100), nullable=True)
    category = Column(String(100), index=True, nullable=True)
    stock = Column(Integer, default=0)
