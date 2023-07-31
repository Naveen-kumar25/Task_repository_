from fastapi import FastAPI,Depends,Body,HTTPException
from database import get_db
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from model import User,Restricted_token
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage



app = FastAPI()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#by using the Cryptcontext we can Hash the password 


def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)
    
def get_password_hash(password):
    return pwd_context.hash(password)
#this method is used to hash the password which is entered by the user


#api to create a user by password hashing
@app.post("/create/user")
def create_user(a : dict= Body(...) , dep :Session = Depends(get_db)):
    hashed_password = get_password_hash(a["password"])
    a["password"] = hashed_password
    b_query = User(**a)
    dep.add(b_query)
    dep.commit()
    dep.close()


def create_jwt_token(data: dict, secret_key: str, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encoded_jwt

#this api is to login the user by checking user email and password with password hashing
#and also to send the jwt token as response 
@app.post("/login")
def login(a : dict= Body(...) , dep: Session = Depends(get_db)):
    user = dep.query(User).filter(User.email == a["email"]).first()

    if not user or not verify_password(a["password"], user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=20)
    access_token = create_jwt_token(
        data={"sub": user.lastname},
        secret_key="you can give any secrect key",
        expires_delta=access_token_expires,
    )


    return {"access_token": access_token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def check_token_blacklist(tokens:str = Depends(oauth2_scheme),dep: Session = Depends(get_db)):
    b_query = dep.query(Restricted_token).filter(Restricted_token.token == tokens).first()

    if b_query:
        raise HTTPException(status_code=401,detail="token is already in db")
    
    return "token is not created"


@app.get("/checking/user")
def checkinguser(token:str = Depends(check_token_blacklist)):

    return {"message":"welcome to the world"}


@app.post("/logout")
def logout(tokens:str = Depends(oauth2_scheme),dep: Session = Depends(get_db)):
    v = Restricted_token(token = tokens)
    dep.add(v)
    dep.commit()
    
    dep.close()
    return {"message":"logout successfull"}



@app.post("/reset-password")
def reset_password(email:str, dep: Session = Depends(get_db)):
    b = dep.query(User).filter((User.email) == email ).first()


    if not b :
        raise HTTPException(status_code=401,detail="email doest not exist in the db")
    
    
    email_server = "smtp.gmail.com"
    email_port = 587
    email_user = "naveenkumarthota22@gmail.com"
    password = "blaankmkcbuzarxe"

    server = smtplib.SMTP(email_server,email_port)
    server.starttls()

    server.login(email_user,password)

    message = EmailMessage()
    message["From"] = email_user
    message["To"] = email
    message["Subject"] = "reset password link"
    message.set_content(f"Hello,{email}!\nthis is a test email")
    
    server.send_message(message)

    server.quit()

@app.post("/set-new-password")
def set_new_password(email: str,new_password: str, dep: Session = Depends(get_db)):
    user = dep.query(User).filter(User.email == email ).first()

    if not user :
        raise HTTPException(status_code=404, detail="Invalid email")

    user.password = pwd_context.hash(new_password)
    
    dep.commit()
    dep.close()

    return {"message": "Password reset successful"}




