import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

from datetime import datetime, timedelta, timezone
from typing import Annotated
# from google import genai

from fastapi import FastAPI, HTTPException, Depends, status
import mysql.connector
from mysql.connector import Error

from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pwdlib import PasswordHash
import jwt

from pydantic import BaseModel

# Declare our classes 
class Opportunity(BaseModel):
    ID: int
    name: str
    description: str
    link: str
    location: list[str] = []
    professions: list[str] = []
    repeatable: bool
    user: str

# Declare our Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# Declare our User
class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

password_hash = PasswordHash.recommended()

# Placeholder Database
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": password_hash.hash("secret"),
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": password_hash.hash("secret_2"),
        "disabled": True,
    }
}

# 1. Properly locate and load the .env file from the root folder
root_dir = Path(__file__).resolve().parent.parent
env_path = root_dir / '.env'
load_dotenv(dotenv_path=env_path)

# 2. Verify the API key exists before calling the API
# if not os.getenv("GEMINI_API_KEY"):
#     raise ValueError("Missing GEMINI_API_KEY in your root .env file!")

app=FastAPI()

origins = [
    "http://localhost:3000", # Example for React/Next.js
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Use ["*"] to allow everything for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

DUMMY_HASH = password_hash.hash("dummypassword")

########################### GENERIC APP INFORMATION ###########################

def get_connection():
    # setup info
    return mysql.connector.connect(
        host=os.getenv("CURR_MACH"), 
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

@app.get("/opportunities")
def get_opportunities():
    try:
        conn=get_connection()
        cursor=conn.cursor(dictionary=True)
        cursor.execute("SELECT ID FROM opportunities")
        rows=cursor.fetchall()
        # print(rows)

        ids = []
        for row in rows:
            # print(row["ID"])
            ids.append(row["ID"])
        # print(ids)

        ourOpps = []
        for id in ids:
            sql_query1 = "SELECT * FROM opportunities WHERE id = %s"
            cursor.execute(sql_query1, (id,))
            oppData = cursor.fetchall()[0]

            sql_query2 = "SELECT lat, lon from opp_location WHERE opp_ID = %s"
            cursor.execute(sql_query2, (id,))
            locations=cursor.fetchall()
            oppData["location"] = locations

            sql_query3 = "SELECT profession from opp_professions WHERE opp_ID = %s"
            cursor.execute(sql_query3, (id,))
            professions=cursor.fetchall()
            professions_acc = []
            for profession in professions:
                professions_acc.append(profession["profession"])
            
            oppData["professions"] = professions_acc
            ourOpps.append(oppData)
        
        # print(ourOpps)

        cursor.close()
        conn.close()
        return ourOpps
    
    except Error as e :
        # return error
        raise HTTPException(status_code=500,detail=str(e))

@app.post("/opportunities")
@app.post("/opportunities/")
def post_opportunity(opp: Opportunity):
    try:
        print(opp)
        conn=get_connection()
        cursor=conn.cursor(dictionary=True)
        sql_query = "INSERT INTO opportunities (name, description, link, repeatable, user) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql_query, (opp.name, opp.description, opp.link, opp.repeatable, opp.user))
        conn.commit()
        new_id = cursor.lastrowid

        for location in opp.location:
            sql_query_loc = "INSERT INTO opp_location (opp_ID, lat, lon) VALUES (%s, %s, %s)"
            cursor.execute(sql_query_loc, (new_id, location["lat"], location["lon"]))
        
        for profession in opp.professions:
            sql_query_prof = "INSERT INTO opp_professions (opp_ID, profession) VALUES (%s, %s)"
            cursor.execute(sql_query_prof, (new_id, profession))
        
        conn.commit()

        cursor.close()
        conn.close()
        return {"message": "Opportunity created successfully", "id": new_id}
    
    except Error as e :
        # return error
        raise HTTPException(status_code=500,detail=str(e))

@app.get("/professions")
def get_professions():
    try:
        conn=get_connection()
        cursor=conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM professions")
        rows=cursor.fetchall()
        # print(rows)

        professions = []
        for row in rows:
            # print(row["Profession_Name"])
            professions.append(row["Profession_Name"])
        # print(ids)

        cursor.close()
        conn.close()
        return professions
    
    except Error as e :
        # return error
        raise HTTPException(status_code=500,detail=str(e))


########################### USER AUTHENTICATION ###########################

########### Helper Funcs ###########

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


########### User Paths ###########

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me/")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    return current_user

@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]
