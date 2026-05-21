from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    username = Column(String)
    category = Column(String)
    description = Column(Text)
    status = Column(String, default="OPEN")
