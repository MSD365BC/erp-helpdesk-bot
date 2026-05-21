from app.database import SessionLocal
from app.models import Ticket

def create_ticket(user_id, username, category, description):
    db = SessionLocal()
    ticket = Ticket(
        user_id=str(user_id),
        username=username,
        category=category,
        description=description
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    db.close()
    return ticket.id

def get_user_tickets(user_id):
    db = SessionLocal()
    data = db.query(Ticket).filter_by(user_id=str(user_id)).all()
    db.close()
    return data

def get_all_tickets():
    db = SessionLocal()
    data = db.query(Ticket).all()
    db.close()
    return data

def update_ticket(ticket_id, status):
    db = SessionLocal()
    ticket = db.query(Ticket).get(ticket_id)
    if ticket:
        ticket.status = status
        db.commit()
    db.close()
