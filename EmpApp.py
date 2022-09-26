from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('www.intellipaat.com')

@app.route("/getemp", methods=['GET', 'POST'])
def getemp():
    return render_template('GetEmp.html')

@app.route("/apply", methods=['GET', 'POST'])
def apply():
    return render_template('ApplyLeave.html')

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    ss = request.form['emp_id']
    take_info = "Select first_name, last_name from employee where emp_id=%s"
    cursor = db_conn.cursor()
    cursor.execute(take_info,ss)
    records = cursor.fetchall()
    db_conn.commit()
  
    ffname=[record[0] for record in records]
    llname=[record[1] for record in records]
    return render_template('GetEmpOutput.html', fname=ffname,lname=llname)

@app.route("/applyleave", methods=['GET', 'POST'])
def ApplyLeave():
    lestdate = request.form['leavestartdate']
    eid = request.form['emp_id']
    updateLeave = "update employee set leave_start_date = %s  where emp_id=%s"
    cursor = db_conn.cursor()
    cursor.execute(updateLeave,(lestdate,eid))
    db_conn.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
