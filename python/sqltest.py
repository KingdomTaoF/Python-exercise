from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Person(Base):
    __tablename__ = 'person'

    id   = Column(Integer, primary_key=True)
    name = Column(String(32))

    def __repr__(self):
        return "<Person(name='%s')>" % self.name