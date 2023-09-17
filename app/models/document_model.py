from commonLib.models.base_class import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Document(Base):
    id = Column(String, primary_key=True)
    template_name = Column(String, nullable=False)
    document_ref = Column(String, unique=True, nullable=True)
    status = Column(String, nullable=False)
    document = Column(String, nullable=False)
    document_data = Column(String, nullable=False)
    qr_code = Column(String, nullable=True)
    user_id = Column(String, nullable=False)


