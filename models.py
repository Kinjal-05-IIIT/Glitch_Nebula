from .database import db
class User(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    email=db.Column(db.String(),unique=True,nullable=False)
    password=db.Column(db.String(),nullable=False)
    Name=db.Column(db.String(),nullable=False)
    Address=db.Column(db.String(),unique=True,nullable=False)
    Pin=db.Column(db.Integer(),nullable=False)
    type=db.Column(db.String(),default="General")
    
class HospitalBed(db.Model):
    id =db.Column(db.Integer(),primary_key=True)
    prime_location_name=db.Column(db.String(),nullable=False)
    Price=db.Column(db.Integer(),nullable=False)
    Address=db.Column(db.String(),unique=True,nullable=False)
    Pin_code=db.Column(db.Integer(),nullable=False)
    maximum_number_of_spots=db.Column(db.Integer(),nullable=False)

class AvailableBed(db.Model):
    id =db.Column(db.Integer(),primary_key=True)
    lot_id=db.Column(db.Integer(),db.ForeignKey("hospital_bed.id"),nullable=False)
    status =db.Column(db.String(),nullable=False)

class ReserveBed(db.Model):
    id =db.Column(db.Integer(),primary_key=True)
    spot_id=db.Column(db.Integer(),db.ForeignKey("available_bed.id"),nullable=False)
    user_id=db.Column(db.Integer(),db.ForeignKey("user.id"),nullable=False)
    Parking_Timestamp=db.Column(db.String(),nullable=False)
    Leaving_Timestamp=db.Column(db.String(),nullable=False)
    costPerTime=db.Column(db.Integer(),nullable=False)
    Lot_ID=db.Column(db.Integer(),db.ForeignKey("available_bed.lot_id"),nullable=False)
    date=db.Column(db.String(),nullable=False)
    