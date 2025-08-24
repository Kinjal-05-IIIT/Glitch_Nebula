from flask import Flask,render_template,redirect,request,session
from flask import current_app as app
from datetime import datetime,date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .models import *
app.secret_key="Kinjal@05"



@app.route("/",methods=["GET","POST"])
@app.route("/login",methods=["GET","POST"])

def login():
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("pwd")
        this_user=User.query.filter_by(email=email).first()
        if this_user:
            if this_user.password==password:
                session['email']=this_user.email
                if this_user.type=='Admin':
                    spots=HospitalBed.query.all()
                    return redirect("/adminhome")
                else:
                    return redirect("/userhome")
            else:
                return render_template("login.html",s="Password is Incorrect!!")
        else:
            return render_template("login.html",s="User does not exist!!")

    return render_template("login.html")
    
@app.route("/register",methods=["GET","POST"])

def register():
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("pwd")
        name=request.form.get("name")
        address=request.form.get("Address")
        pin=request.form.get("pin")
        this_user=User.query.filter_by(email=email).first()
        if this_user:
            return "User already exists"
        else:
            user1=User(email=email,password=password,Name=name,Address=address,Pin=pin)
            db.session.add(user1)
            db.session.commit()
            return redirect("/login")
    return render_template("register.html")

@app.route("/userhome",methods=["GET","POST"])
def userhome():
    d=dict()
    email=session.get("email")
    u=User.query.filter_by(email=email).first()
    if not u:
        return redirect("/login")
    b=ReserveBed.query.filter_by(user_id=u.id).all()
    for item in b:
        lotID=item.Lot_ID
        c=HospitalBed.query.filter_by(id=lotID).first()
        d[item]=c
    return render_template("userhome.html",Username=email,b=b,d=d)

@app.route("/usersummary",methods=["GET","POST"])
def usersummary():
    email=session.get("email")
    u=User.query.filter_by(email=email).first()
    k=ReserveBed.query.filter_by(user_id=u.id).all()
    hour=0
    min=0
    sec=0
    lot=dict()
    if k==[]:
        return render_template("usersummary.html",Username=email,k=k)
    for i in k:
        dt1 = datetime.strptime(i.Leaving_Timestamp, "%H:%M:%S.%f")
        dt2 = datetime.strptime(i.Parking_Timestamp, "%H:%M:%S.%f")
        s = str(dt1 - dt2)
        sec=sec+int(s[s.find(":")+4:s.find(":")+6])
        if sec>=60:
            min=min+1
            sec=sec-60
        min=min+int(s[s.find(":")+1:s.find(":")+3])
        if min>=60:
            hour=hour+1
            min=min-60
        if i.Lot_ID not in list(lot.keys()):
            lot[i.Lot_ID]=0
       
        hour=hour+int(s[0:s.find(":")])
        lot[i.Lot_ID]=lot[i.Lot_ID]+((int(s[0:s.find(":")])+1)*i.costPerTime)
    x=list(lot.keys())
    y=[lot[i] for i in x]
    plt.figure()
    plt.bar(x, y, color='blue')
    plt.title("Bar chart")
    plt.xlabel("Parking Lots")
    plt.ylabel("Money spent(in rupees)")
    plt.savefig("static/usergraph.png")
    plt.close()
    return render_template("usersummary.html",Username=email,h=hour,m=min,s=sec,k=k)

@app.route("/adminhome",methods=["GET","POST"])
def adminhome():
    if request.method=='POST':
        lot_id=request.form.get("View")
        b=AvailableBed.query.filter_by(lot_id=int(lot_id)).all()
    else:
        b=[]
    spots=HospitalBed.query.all()
    email=session.get("email")
    return render_template("adminhome.html",Username=email,spots=spots,b=b)



@app.route("/adminsearch",methods=["GET","POST"])
def adminsearch():
    k=None
    s="None"
    if request.method=="POST":
        search=request.form.get("search")
        info=request.form.get("info")
        
        if search=="User ID":
            k=ReserveBed.query.filter_by(user_id=info).all()
            s="user"
        elif search=="Address":
            k=HospitalBed.query.filter_by(prime_location_name=info).all()
            s="lot"
        else:
            k=HospitalBed.query.filter_by(Pin_code=info).all()
            s="lot"
    email=session.get("email")
    return render_template("adminsearch.html",Username=email,k=k,s=s)

@app.route("/adminsummary",methods=["GET","POST"])
def adminsummary():
    x=[]
    y=[]
    t=0
    email=session.get("email")
    lot=HospitalBed.query.all()
    for i in lot:
        x.append(i.id)
        reserve=ReserveBed.query.filter_by(Lot_ID=i.id).all()
        if reserve==None:
            y.append(0)
            continue
        for k in reserve:
            dt1 = datetime.strptime(k.Leaving_Timestamp, "%H:%M:%S.%f")
            dt2 = datetime.strptime(k.Parking_Timestamp, "%H:%M:%S.%f")
            s = str(dt1 - dt2)
            n=s.find(':')
            p=(int(s[0:n])+1)*k.costPerTime
            t+=p
        y.append(t)
        t=0
    plt.figure()
    plt.bar(x, y, color='blue')
    plt.title("Bar chart")
    plt.xlabel("Hospital Beds")
    plt.ylabel("Revenue generated in Rupees")
    plt.savefig("static/graph.png")
    plt.close()
    b=None
    if request.method=="POST":
        a=request.form.get('View')
        b=ReserveBed.query.filter_by(Lot_ID=a).all()
        if b==[]:
            return redirect("/adminsummary")
        else:
            sizes=[0,0,0,0,0,0]
            y=[0,0,0,0,0,0,0,0,0,0,0,0]
            labels = ['12 am-4 am', '4 am-8 am', '8 am-12 noon', '12 noon-4pm', '4 pm-8 pm', '8 pm-12 am']
            colors = ['red', 'green', 'yellow', 'pink', 'orange','blue']
            for j in b:
                s=j.Parking_Timestamp
                if j.Parking_Timestamp[0:s.find(":")] in ['00','01','02','03']:
                    sizes[0]=sizes[0]+1
                elif j.Parking_Timestamp[0:s.find(":")] in ['04','05','06','07']:
                    sizes[1]=sizes[1]+1
                elif j.Parking_Timestamp[0:s.find(":")] in ['08','09','10','11']:
                    sizes[2]=sizes[2]+1
                elif j.Parking_Timestamp[0:s.find(":")] in ['12','13','14','15']:
                    sizes[3]=sizes[3]+1
                elif j.Parking_Timestamp[0:s.find(":")] in ['16','17','18','19']:
                    sizes[4]=sizes[4]+1
                else:
                    sizes[5]=sizes[5]+1
            for i in sizes:
                i=i//len(b)
            p=[]
            q=[]
            r=[]
            for i in range(len(sizes)):
                if sizes[i]!=0:
                    p.append(sizes[i])
                    q.append(colors[i])
                    r.append(labels[i])
            sizes=p
            colors=q
            labels=r
            for j in b:
                s=j.date
                s=s[s.find("-")+1:s.find("-")+3]
                y[int(s)-1]=y[int(s)-1]+1


       
        plt.figure(figsize=(5,4))
        plt.pie(sizes, labels=labels, colors=colors,autopct='%1.1f%%', shadow=True, startangle=140)

        plt.title('Daily distribution')
        plt.axis('equal')
        plt.savefig("static/pie.png")
        plt.close()
        x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        plt.figure(figsize=(5,4))
        plt.scatter(x, y,color='blue',label='Points')
        plt.plot(x, y, color='red', label='Line')
        plt.xlabel('Months')
        plt.ylabel('Frequency')
        plt.title('Monthly Distribution')
        plt.savefig("static/scatter.png")
    spots=HospitalBed.query.all()
    return render_template("adminsummary.html",Username=email,spots=spots,b=b)

@app.route("/adminusers",methods=["GET","POST"])
def adminusers():
    users=User.query.all()
    email=session.get("email")
    return render_template("adminusers.html",Username=email,users=users)

@app.route("/addlot",methods=["GET","POST"])
def addlot():
    if request.method=="POST":
        f=request.form.get("func")
        if f=="Cancel":
            return redirect("/adminhome")
        else:
            loc=request.form.get("location")
            address=request.form.get("address")
            pin=request.form.get("pin")
            price=request.form.get("price")
            max_spots=request.form.get("max_spots")
            k=HospitalBed(prime_location_name=loc,Address=address,Pin_code=pin,Price=price,maximum_number_of_spots=max_spots)
            db.session.add(k)
            db.session.commit()
            c=1
            for i in range(int(max_spots)):
                p=AvailableBed(id=k.id*1000+c,lot_id=k.id,status="Vacant")
                db.session.add(p)
                db.session.commit()
                c=c+1
        return redirect("/adminhome")
    return render_template("newPL.html")
@app.route("/editPL",methods=["GET","POST"])
def editPL():
    if request.method=="POST":
        b=request.form.get("Edit")
        k=HospitalBed.query.filter_by(id=b).first()
    return render_template("editPL.html",k=k)

@app.route("/editPL2",methods=["GET","POST"])
def editPL2():
    if request.method=="POST":
        f=request.form.get("func")
        if f=="Cancel":
            return redirect("/adminhome")
        else:
            add=request.form.get("add")
            price=request.form.get("Price")
            max_spots=request.form.get("max spots")
            k=HospitalBed.query.filter_by(Address=add).first()
            k.Price=price
            k.maximum_number_of_spots=max_spots
            db.session.commit()
            b=AvailableBed.query.filter_by(lot_id=k.id).all()
            if len(b)>int(max_spots):
                for i in range(len(b)-int(max_spots)):
                    c=(AvailableBed.query.filter_by(lot_id=k.id).all())[-1]
                    db.session.delete(c)
                    db.session.commit()
            else:
                p=(HospitalBed.query.filter_by(lot_id=k.id).all())[-1]
                for i in range(abs(len(b)-int(max_spots))):
                    c=HospitalBed(id=p.id+i+1,lot_id=k.id,status="Vacant")
                    db.session.add(c)
                    db.session.commit()
            return redirect("/adminhome")
    return render_template("editPL.html",k=k)

@app.route("/viewparkingspot",methods=["GET","POST"])
def viewparkingspot():
    if request.method=="POST":
        b=request.form.get("ViewPS")
        k=HospitalBed.query.filter_by(id=b).first()
    return render_template("viewPS.html",k=k)

@app.route("/viewparkingspot2",methods=["GET","POST"])
def viewparkingspot2():
    if request.method=="POST":
        b=request.form.get("action")
        if b=="Cancel":
            return redirect("/adminhome")
        else:
            a=request.form.get("id")
            k=HospitalBed.query.filter_by(id=a).first()
            l=k.lot_id
            if b=="Delete":
                db.session.delete(k)
                db.session.commit()
                t=HospitalBed.query.filter_by(id=l).first()
                t.maximum_number_of_spots= t.maximum_number_of_spots-1  
                db.session.commit()
                return redirect("/adminhome")
            else:
                k=ReserveBed.query.filter_by(spot_id=b).all()
                for i in k:
                    if i.Parking_Timestamp==i.Leaving_Timestamp:
                        a=i 
                t=datetime.now().time()
                t=str(t)
                dt1 = datetime.strptime(t, "%H:%M:%S.%f")
                dt2 = datetime.strptime(a.Parking_Timestamp, "%H:%M:%S.%f")
                s = str(dt1 - dt2)
                n=s.find(':')
                s=(int(s[0:n])+1)*a.costPerTime 
            return render_template("occupiedPS.html",a=a,s=s)   
    return render_template("viewPS.html",k=k)

@app.route("/lotsearch",methods=["GET","POST"])
def lotsearch():
    k=[]
    d=dict()
    c=0
    if request.method=="POST":
        info=request.form.get("info")
        k=HospitalBed.query.filter_by(prime_location_name=info).all()
        for i in k:
            b=AvailableBed.query.filter_by(lot_id=i.id).all()
            for j in b:
                if j.status=='Vacant':
                    c=c+1
            d[i.id]=c
            c=0
    email=session.get("email")
    return render_template("userhome.html",Username=email,k=k,d=d)

@app.route("/bookPS",methods=["GET","POST"])
def bookPS():
    if request.method=="POST":
        b=request.form.get("book")
        k=HospitalBed.query.filter_by(id=b).first()
        a=AvailableBed.query.filter_by(lot_id=b,status="Vacant").first()
    email=session.get("email")
    c=User.query.filter_by(email=email).first()
    return render_template("bookPS.html",Username=c.id,k=k,a=a)

@app.route("/bookPS2",methods=["GET","POST"])
def bookPS2():
    if request.method=="POST":
        f=request.form.get("action")
        if f=="Cancel":
            return redirect("/userhome")
        else:
            spotID=request.form.get("spotID")
            UserID=request.form.get("userID")
            lotID=request.form.get("lotID")
            price=request.form.get("price")
            vrn=request.form.get("vrn")
            t=datetime.now().time()
            dt=date.today()
            k=ReserveBed(spot_id=spotID,user_id=UserID,Parking_Timestamp=str(t),Leaving_Timestamp=str(t),costPerTime=price,Lot_ID=lotID,date=str(dt))
            db.session.add(k)
            db.session.commit()
            a=AvailableBed.query.filter_by(id=spotID).first()
            a.status="Occupied"
            db.session.commit()
            return redirect("/userhome")
    return render_template("bookPS.html")

@app.route("/releasePS",methods=["GET","POST"])
def releasePS():
    if request.method=="POST":
        parkingID=request.form.get("release")
        k=ReserveBed.query.filter_by(id=parkingID).first()
        b=AvailableBed.query.filter_by(id=k.spot_id).first()
        t=datetime.now().time()
        t=str(t)
        dt1 = datetime.strptime(t, "%H:%M:%S.%f")
        dt2 = datetime.strptime(k.Parking_Timestamp, "%H:%M:%S.%f")
        s = str(dt1 - dt2)
        n=s.find(':')
        s=(int(s[0:n])+1)*k.costPerTime
    return render_template("releasePS.html",k=k,lot_id=b.lot_id,time=t,diff=s)

@app.route("/releasePS2",methods=["GET","POST"])
def releasePS2():
    if request.method=="POST":
        a=request.form.get("action")
        if a=="Cancel":
            return redirect("/userhome")
        else:
            k=request.form.get("spot")
            c=ReserveBed.query.filter_by(spot_id=k).all()
            k=request.form.get("leave")
            c[-1].Leaving_Timestamp=k
            db.session.commit()
            b=AvailableBed.query.filter_by(id=c[-1].spot_id).first()
            b.status="Vacant"
            db.session.commit()
            return redirect("/userhome")
    return render_template("releasePS.html")

@app.route("/editprofile",methods=["GET","POST"])
def editprofile():
    em=session.get('email')
    user=User.query.filter_by(email=em).first()
    return render_template("editprofile.html",user=user)

@app.route("/editprofile2",methods=["GET","POST"])
def editprofile2():
    em=session.get("email")
    b=User.query.filter_by(email=em).first().id
    if request.method=="POST":
        f=request.form.get("action")
        if f=="Cancel":
            if b==1000:
                return redirect("/adminhome")
            else:
                return redirect("/userhome")
        else:
            a=session.get("email")
            email=request.form.get("email")
            name=request.form.get("name")
            pwd=request.form.get("pwd")
            add=request.form.get("add")
            vrn=request.form.get("vrn")
            d=User.query.filter_by(email=a).first()
            d.email=email
            d.Name=name
            d.password=pwd
            d.Address=add
            d.VRN=vrn
            db.session.commit()
            if b==1000 and email==a:
                return redirect("/adminhome")
            elif b>1000 and email==a:
                return redirect("/userhome")
            else:
                return redirect("/")
    return render_template("editprofile.html")

@app.route("/close",methods=["GET","POST"])
def close():
    if request.method=="POST":
        return redirect("/adminhome")
    return render_template("occupiedPS.html")



