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

@app.route("/gotoviewallleave", methods=['GET', 'POST'])
def gotoviewallleave():
    return render_template('ViewApplyLeave.html')

@app.route("/gotoapproveleave", methods=['GET', 'POST'])
def gotoapproveleave():
    return render_template('ApproveLeave.html')

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


  
   # ffname=[record[0] for record in records]
   # llname=[record[1] for record in records]
   


#below
@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
  #  try:
      eid = request.form['emp_id']
      cursor = db_conn.cursor()
      fetch_sql = "Select emp_id, first_name, last_name, pri_skill, location from employee where emp_id=%s"
      cursor.execute(fetch_sql,(eid))
      emp=cursor.fetchall()
      db_conn.commit()
      (emp_id, first_name, last_name, pri_skill, location)=emp[0]
      image_url=show_image(custombucket)
      return render_template('GetEmpOutput.html',emp_id=emp_id,first_name=first_name,last_name=last_name,pri_skill=pri_skill,location=location,image_url=image_url)
   # except Exception as e:
   #   return render_template('IdNotFound.html')

#below
@app.route("/applyleave", methods=['GET', 'POST'])
def ApplyLeave():
    try:
      start_date = request.form['leave_start_date']
      end_date = request.form['leave_end_date']
      reason = request.form['leave_reason']
      eid = request.form['emp_id']
      updateLeave = "update employee set leave_start_date = %s, leave_end_date = %s, leave_reason =%s, leave_status=%s  where emp_id=%s"
      cursor = db_conn.cursor()
      cursor.execute(updateLeave,(start_date,end_date,reason,'pending',eid))
      db_conn.commit()
      return render_template('AddEmp.html')
    except Exception as e:
      return render_template('IdNotFound.html')


#below
@app.route("/viewleave", methods=['GET', 'POST'])
def ViewLeave():
    try:
      view_leave_emp_id = request.form['view_leave_emp_id']
      view_leave = "Select emp_id, first_name, last_name, leave_start_date, leave_end_date, leave_reason, leave_status from employee where emp_id=%s"
      cursor = db_conn.cursor()
      cursor.execute(view_leave,(view_leave_emp_id))
      view_records = cursor.fetchall()
      db_conn.commit()
      (emp_id, first_name, last_name, leave_start_date, leave_end_date, leave_reason, leave_status)=view_records[0]
      return render_template('ViewApplyLeave.html', emp_id=emp_id, first_name=first_name,last_name=last_name,leave_start_date=leave_start_date, leave_end_date=leave_end_date, leave_reason=leave_reason, leave_status=leave_status)
    except Exception as e:
      return render_template('IdNotFound.html')


#below
@app.route("/approveleave", methods=['GET', 'POST'])
def ApproveLeave():
    try:
      eid = request.form['emp_id']
      approve_va=request.form['action']
      if approve_va=='Approve':
         lestatus='Approve'
      else:
         lestatus='Reject'   
      approve_leave = "Update employee set leave_status=%s where emp_id=%s"
      cursor = db_conn.cursor()
      cursor.execute(approve_leave,(lestatus,eid))
      db_conn.commit()
      return render_template('ApproveLeave.html',first_name=approve_va)
    except Exception as e:
      return render_template('IdNotFound.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
