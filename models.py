from sqlalchemy import Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
# We are now adding in a password hashing module - there are many - we are using passlib and custom_app_context
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    password_hash = Column(String(64))
    
    # hashing is a one-way process - we store the hashed password, and NEVER the actual password.
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)
    
    # So, to verify it, we take the offered password, run the hashing process again, and check against the hashed password which is stored.
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


engine = create_engine('sqlite:///users.db')
 

Base.metadata.create_all(engine)