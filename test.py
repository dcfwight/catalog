# Simple test to see if we can connect to AWS Postgres, using psycopg2
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context # password hashing


import psycopg2
from sqlalchemy import create_engine

Base = declarative_base()
# END of configuration code

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(256), index=True, nullable=False)
    password_hash = Column(String(64))
    email = Column(String(256), nullable=False, unique=True)
    picture = Column(String(250))

    # hashing is a one-way process - we store the hashed password,
    # and NEVER the actual password.
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    # So, to verify it, we take the offered password,
    # run the hashing process again, and check against the hashed password
    # which is stored.
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)	

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'username' : self.name,
            'password_hash': self.password_hash,
            'email': self.email
        }

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, index=True, unique=True)
    creator_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    
    
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
        'id': self.id,
        'name' : self.name,
        'creator_id': self.creator_id
        }
    
class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, index=True)
    description = Column(String(1024))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    creator_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    edited_time = Column(Integer)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name' : self.name,
            'description': self.description,
            'edited_time': self.edited_time,
            'category_id': self.category_id,
            'creator_id': self.creator_id
        }


try:
    engine = create_engine('postgresql+psycopg2://doug:udacious@catalogdbinstance.c6lebb60ocvv.us-east-1.rds.amazonaws.com:5432/catalog_db')
    Base.metadata.create_all(engine)
    print ('tables created')
except:
    print ("unable to connect to AWS postgres database using psycopg2")

print ('done')