from sqlalchemy import Integer, Column, Boolean, String,LargeBinary
from commonLib.models.base_class import Base






class AttestedDocuments(Base):
    __tablename__="attested_documents"
    id=Column(String, primary_key=True, nullable=False)
    document_ref=Column(String, nullable=False)
    document=Column(String,nullable=False)
    commissioner_id=Column(String,nullable=False)



















