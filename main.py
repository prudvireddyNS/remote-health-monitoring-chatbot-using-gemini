from config import apiKey
import google.generativeai as genai
import mysql.connector as conn
from mic import hear
from datetime import datetime
import pyttsx3
import csv
from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)
engine=pyttsx3.init('sapi5')
voices=engine.getProperty('voices')
engine.setProperty('voice',voices[0].id)

db= conn.connect(host ='localhost',password = '0000',user ='root',database = 'victims')
cursor = db.cursor()
print("Connected")





def runQuery(query,params):
    cursor.execute(query,params)    
    cursor.execute("commit")

def speak(audio):
    engine.say(audio)
    engine.runAndWait()
def gemini_result(prompt):
    messages=[]
    systemMessage="You are an AI bot"
    genai.configure(api_key=apiKey)
    model = genai.GenerativeModel('gemini-pro',generation_config={'temperature':0})
    model.max_output_tokens =10
    chat = model.start_chat()
    response = model.generate_content(prompt+"in 100 characters")
    result = response.text
    return result
    #speak(response.text)

#prompt=hear()




def takeDetails():
    name = input("Enter the name")
    date =  datetime.today().strftime('%Y-%m-%d')
    symptoms = input("Enter your Symptoms")
    query = "INSERT INTO patients(patient_name,joining_date,symptoms) VALUES( %s , %s,%s)"
    params = (name,date,symptoms,)
    runQuery(query,params)
    print("!!!!!!Details Added Successfully!!!!!!")
    query = "select patient_id from patients where patient_name = %s"
    params= (name,)
    cursor.execute(query,params)
    id = cursor.fetchone()
    print(type(id[0]))
    diagnose(symptoms,id[0])
    cursor.execute("SELECT * FROM patients")
    a= cursor.fetchall()
    convert_csv(a)

    

def diagnose(symptoms,id):
    prompt = "I'm suffering from "+symptoms+"suggest me two best medicines to diagnose them"
    ds =gemini_result(prompt)
    print(ds)
    strid =str(id) 
    query = "select prev_diagnosis from patients where patient_id = %s"
    params= (strid,)
    cursor.execute(query,params)
    p= cursor.fetchone()
    query = "UPDATE patients SET latest_diagnosis = %s  WHERE patient_id = %s"
    params =(ds,strid,)
    runQuery(query,params)
    print(p[0])
    
def alreadyVisited():
    print("Please enter your ID number______ or your name")
    pid = input()
    strpid = str(pid)
    query = "select patient_name from patients where patient_id = %s"
    params = (pid,)
    cursor.execute(query,params)
    user_name = cursor.fetchone()
    print("Welcome Mr : ",user_name[0])
    new_symptoms = input("Enter your new symptoms : ")
    query = "UPDATE patients set new_symptoms = %s where patient_id = %s"
    params = (new_symptoms,strpid)
    runQuery(query,params)
    print("Updated")
    query = "SELECT latest_diagnosis FROM patients WHERE patient_id = %s"
    params=(strpid,)
    cursor.execute(query,params)
    temp = cursor.fetchone()
    query = "UPDATE patients set prev_diagnosis = %s where patient_id = %s"
    params = (temp[0],strpid)
    runQuery(query,params)
    diagnose(new_symptoms,pid)

def convert_csv(a):

    csv_file ='data2.csv'
# Write to CSV file
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Write the header (column names)
        column_names = [i[0] for i in cursor.description]
        writer.writerow(column_names)
        
        # Write the data rows
        writer.writerows(a)


    



def newVisit():
    takeDetails()


while True:
    print("!!!!!!!!Menu Options!!!!!!!!!!")
    print("1.Already visited?")
    print("2.New Visit")
    user_option = int(input())
    if user_option ==1:
        alreadyVisited()
    else:
        newVisit()
