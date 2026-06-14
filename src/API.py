import os
from pathlib import Path
from dotenv import load_dotenv
# from google import genai

from fastapi import FastAPI, HTTPException
import mysql.connector
from mysql.connector import Error

from fastapi.middleware.cors import CORSMiddleware

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

user = "root"
password = ""

def get_connection():
    # setup info
    return mysql.connector.connect(
        host="localhost", 
        user=user,
        password=password,
        database="cs-dob_backend"
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
        print(rows)

        professions = []
        for row in rows:
            print(row["Profession_Name"])
            professions.append(row["Profession_Name"])
        # print(ids)

        cursor.close()
        conn.close()
        return professions
    
    except Error as e :
        # return error
        raise HTTPException(status_code=500,detail=str(e))