from commonLib.models.base_class import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Attestation(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    signature = Column(String, unique=True, nullable=False)
    stamp = Column(String, unique=True, nullable=False)



