from sqlalchemy import Column,String,DateTime,Integer,Text,Boolean
from datetime import datetime
from database import Base




class User(Base):
    __tablename__ = 'user'
    firstname = Column(String(25),nullable = False , unique = True ,primary_key= True)
    lastname = Column(String(25),nullable = False , unique = True)
    email = Column(String(40) , unique = True)
    password = Column(Text,nullable=False)
    date_of_birth = Column(DateTime(),nullable=False)


    def __repr__(self):
        return f"<User firstname = {self.firstname} email = {self.email}"
    

class Restricted_token(Base):
    __tablename__ = 'restricted_token'
    id = Column(Integer,primary_key= True)
    token = Column(String(250),unique= True)







    