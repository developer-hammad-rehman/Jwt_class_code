from sqlmodel import SQLModel , Field
from typing import Optional

class Usersdata(SQLModel , table = True):
    id : Optional[int] = Field(default= None , primary_key=True)
    email : str
    password:str