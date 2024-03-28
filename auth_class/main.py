from fastapi import FastAPI , Depends ,  HTTPException

from fastapi.security import OAuth2PasswordBearer , OAuth2PasswordRequestForm

from typing import Annotated

from auth_class.setting import db_url

from auth_class.model import Usersdata

from sqlmodel import SQLModel, create_engine , select , Session

from contextlib import asynccontextmanager

from jose import jwt , JWTError

from datetime import datetime, timedelta, timezone


engine = create_engine(db_url , connect_args={"sslmode" :"require"} , pool_recycle=300 , echo = True)

@asynccontextmanager
async def lifespan(app:FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


def get_session():
    session = Session(engine)
    yield session



app = FastAPI(
    title="Auth",
    lifespan = lifespan
)





# oauth2 sehema
ouath = OAuth2PasswordBearer(tokenUrl = "token")

# root route
@app.get('/')
def root_route():
    return {"message" :"Hello"}


# token route

@app.get('/token')

def token_route(token : Annotated[str , Depends(ouath)] ,  session : Annotated[Session, Depends(get_session)]):
    try:
     # jwt token decode
     username = jwt.decode(token , 'key' , algorithms='HS256')['email']
     
     # match the username with db email
     statment = select(Usersdata).where(username == Usersdata.email)

    
     result = session.exec(statment).all()
    
    # print the result
     return result
    except JWTError:
         # token expire error handling
        raise HTTPException(status_code=404 , detail="Token has expired")

# login route
@app.post('/formdata')

def form_route (formdata : Annotated[OAuth2PasswordRequestForm , Depends() ] , session : Annotated[Session , Depends(get_session)]):
    # statment condition
    statment = select(Usersdata).where(formdata.username == Usersdata.email)

    # execute stayment
    result = session.exec(statment).all()
    

    if result:
        # conditon for checking email and password
        if result[0].password == formdata.password:
         expire = datetime.now(timezone.utc) + timedelta(seconds = 15)
         # encode
         token  = jwt.encode({"email" : formdata.username , 'exp' : expire} , "key" , algorithm="HS256")
         return {
             "message" : "Correct Email and password",
             "token" : token
             }
        
        else:
            raise HTTPException(status_code=404 , detail="Incorect Password")
    else:
        raise HTTPException(status_code=404 , detail="Email Not Found")
    

# signup route
@app.post('/signup')

def siginup_route(formdata : Annotated[OAuth2PasswordRequestForm, Depends()], session : Annotated[Session , Depends(get_session)]):
    

    statment = select(Usersdata).where(formdata.username == Usersdata.email)

    result  = session.exec(statment).all()

    if result :
        raise HTTPException(status_code=404 , detail="Email already exist")
    else:
        # enter data in db
        data = Usersdata(email=formdata.username , password=formdata.password)

        session.add(data)
        session.commit()
        session.close()

        return {"message" : 'Data added'}
