from flask import current_app as app,request,jsonify
from .models import User
from .database import db

@app.post("/api/login")
def api_login():
    email=request.json.get("email")
    pwd=request.json.get("pwd")
    try:
        this_user=User.query.filter_by(email=email).first()
        if this_user:
            if this_user.password==pwd:
                if this_user.type=='Admin':
                    return jsonify(message="Admin Logged in successfully")
                else:
                    return jsonify(message="User Logged in successfully")
            else:
                return jsonify(error="Incorrect password"),400
        else:
            return jsonify(error="User not found"),404
    except:
        return jsonify(error="Internal Server Error"),500
    
@app.post("/api/register")
def api_register():
    
    email = request.json.get("email")
    pwd = request.json.get("password")
    name = request.json.get("name")
    address = request.json.get("address")
    pin = int(request.json.get("pin"))
    vrn = request.json.get("vrn")
    try:
        this_user = User.query.filter_by(email=email).first()
        if this_user:
            return jsonify(error="User already exists"), 400
        else:
            user1 = User(email=email, password=pwd, Name=name, Address=address, Pin=pin, VRN=vrn)
            db.session.add(user1)
            db.session.commit()
            return jsonify(message="User created successfully"), 201

    except:
        return jsonify(error="Internal Server Error"), 500

