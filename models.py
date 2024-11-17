from sqlalchemy import INTEGER, Column, VARCHAR, SmallInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(INTEGER(), primary_key=True)


class Student(BaseModel):
    __tablename__ = "student"
    name = Column(VARCHAR(length=32))
    gender = Column(VARCHAR(length=1))
    birth = Column(VARCHAR(length=10))

    study_year = Column(SmallInteger())
    class_id = Column(VARCHAR(length=1))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "birth": self.birth,
            "study_year": self.study_year,
            "class_id": self.class_id
        }
