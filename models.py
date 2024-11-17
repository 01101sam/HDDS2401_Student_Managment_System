from sqlalchemy import INTEGER, Column, ForeignKey, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(INTEGER(), primary_key=True)


class Student(BaseModel):
    __tablename__ = "student"
    name = Column(String())
    gender = Column(String())
    birth = Column(String())

    study_year = Column(String())
    class_id = Column(String())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "birth": self.birth,
            "year": self.year,
            "class_id": self.class_id
        }
