"""
Author: Lav Sharma
Created on: 29th Oct 2023
"""

from pydantic import BaseModel


class HeartbeatResult(BaseModel):
    is_alive: bool
