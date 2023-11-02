"""
Author: Lav Sharma
Created on: 29th Oct 2023
"""

from sqlalchemy import Column, BIGINT, SMALLINT, TIME, VARCHAR, DATETIME, TEXT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class StoreStatus(Base):
    __tablename__ = 'StoreStatus'
    SS_Id = Column(BIGINT, primary_key=True)
    SD_StoreId = Column(BIGINT, nullable=False)
    SS_StoreStatus = Column(VARCHAR(10), nullable=False)
    SS_TimestampUtc = Column(DATETIME, nullable=False)


class StoreTimezone(Base):
    __tablename__ = 'StoreTimezone'
    ST_Id = Column(BIGINT, primary_key=True)
    SD_StoreId = Column(BIGINT, nullable=False)
    ST_Timezone = Column(VARCHAR(45), nullable=False)


class StoreDetails(Base):
    __tablename__ = 'StoreDetails'
    SD_Id = Column(BIGINT, primary_key=True)
    SD_StoreId = Column(BIGINT, nullable=False)
    SD_Day = Column(SMALLINT, nullable=False)
    SD_StartTimeLocal = Column(TIME, nullable=False)
    SD_EndTimeLocal = Column(TIME, nullable=False)


class Request(Base):
    __tablename__ = 'Request'
    R_Id = Column(BIGINT, primary_key=True)
    R_RequestReceivedTimestamp = Column(DATETIME, nullable=False)
    R_RequestCompletedTimestamp = Column(DATETIME, nullable=True)
    RS_Id = Column(SMALLINT, nullable=False)
    R_OutputFilePath = Column(TEXT, nullable=True)


class RequestStatus(Base):
    __tablename__ = 'RequestStatus'
    RS_Id = Column(SMALLINT, primary_key=True)
    RS_Name = Column(VARCHAR(45), nullable=False, unique=True)
