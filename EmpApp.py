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

#below
@app.route("/getemp", methods=['GET', 'POST'])
def getemp():
    return render_template('GetEmp.html')

def show_image(bucket):
    s3_client = boto3.client('s3')

    emp_id = request.form['emp_id']

    try:
        for item in s3_client.list_objects(Bucket=bucket)['Contents']:
            presigned_url=s3_client.generate_presigned_url('get_object',Params={'Bucket':bucket, 'Key':item['Key']},ExpiresIn=100)
            if emp_id in item['Key']:
                public_urls=https://s3-toosweewah-bucket.s3.amazonaws.com/mountain.jpeg
    except Exception as e:
        return render_template('IdNotFound.html')
    return public_urls





@app.route("/apply", methods=['GET', 'POST'])
def apply():
    return render_template('ApplyLeave.html')

@app.route("/gotoviewallleave", methods=['GET', 'POST'])
def gotoviewallleave():
    return render_template('ViewApplyLeave.html')

@app.route("/gotoapproveleave", methods=['GET', 'POST'])
def gotoapproveleave():
    return render_template('ApproveLeave.html')

@app.route("/addemp", methods=['GET','POST'])
def AddEmp():
    if request.method=='POST':

        emp_id = request.form['emp_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        pri_skill = request.form['pri_skill']
        location = request.form['location']
        leave_start_date=0000-00-00
        leave_end_date=0000-00-00
        leave_reason='none'
        leave_status='none'
        gender='ss'     
        job_title = request.form['job_title']
        date_of_hired=request.form['date_of_hired']
        hourly_wage='1'
        hours_worked= '1'
        monthly_pay = '1'
        emp_image_file = request.files['emp_image_file']        

# %s,%s,%s
        insert_sql = "INSERT INTO employee VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor = db_conn.cursor()

        if emp_image_file.filename == "":
            return "Please select a file"

        try:
# hourly_wage,hours_worked,monthly_pay
            cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location,leave_start_date,leave_end_date,leave_reason,leave_status,gender,job_title,date_of_hired,hourly_wage,hours_worked,monthly_pay))
            db_conn.commit()
            emp_name = "" + first_name + " " + last_name
            # Upload image file in S3 #
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
        except Exception as e:
            return str(e)
        finally:
            cursor.close()

        print("all modification done...")
        return render_template('AddEmpOutput.html', name=emp_name)
    else:
        return render_template('GetEmp.html', name=emp_name)

  
   # ffname=[record[0] for record in records]
   # llname=[record[1] for record in records]
   


#below
@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    if request.method =='POST':
       try:
            eid = request.form['emp_id']
            cursor = db_conn.cursor()
            fetch_sql = "Select emp_id, first_name, last_name, pri_skill, location from employee where emp_id=%s"
            cursor.execute(fetch_sql,(eid))
            emp=cursor.fetchall()
            db_conn.commit()
            (emp_id, first_name, last_name, pri_skill, location)=emp[0]
            image_url=show_image(custombucket)
           
            return render_template('GetEmpOutput.html',id=emp_id,fname=first_name,lname=last_name,interest=pri_skill,location=location,image_url=image_url)
       except Exception as e:
            return render_template('IdNotFound.html')
    else:
        return render_template('AddEmp.html',fetchdata=fetchdata)

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

#Foo   
@app.route("/payroll", methods=['GET', 'POST'])
def Payroll():
    try:
      payroll_emp_id = request.form['payroll_emp_id']
      payroll = "Select emp_id, first_name, last_name, hourly_wage, hours_worked, monthly_pay from employee where emp_id=%s"
      cursor = db_conn.cursor()
      cursor.execute(payroll,(payroll_emp_id))
      view_records = cursor.fetchall()
      db_conn.commit()
      (emp_id, first_name, last_name, hourly_wage, hours_worked, monthly_pay)=view_records[0]
      return render_template('Payroll.html', emp_id=emp_id, first_name=first_name,last_name=last_name,hourly_wage=hourly_wage, leave_end_date=leave_end_date, hours_worked=hours_worked, monthly_pay=monthly_pay)
    except Exception as e:
      return render_template('IdNotFound.html')

#Foo
@app.route("/updatePayroll", methods=['GET', 'POST'])
def UpdatePayroll():
    try:
      hourly_wage = request.form['hourly_wage']
      eid = request.form['emp_id']
      updateHourly = "update employee set hourly_wage = %s where emp_id=%s"
      cursor = db_conn.cursor()
      cursor.execute(updateHourly,(hourly_wage,eid))
      db_conn.commit()
      return render_template('UpdatePayroll.html')
    except Exception as e:
      return render_template('IdNotFound.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
