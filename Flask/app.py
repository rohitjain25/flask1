from flask import Flask, flash, render_template, request, redirect, url_for
import os 
from werkzeug.utils import secure_filename
import csv
# import pandas as pd
import subprocess
from datetime import datetime as dt

app = Flask(__name__)

app.secret_key = "secret key"
app.config["FILE_UPLOAD"] = "./uploads"

host_list=[]
def convert_log_to_csv(filename):
    with open('converted.csv', 'w') as out_file,open('uploads/'+filename,'r') as in_file:

        writer = csv.writer(out_file)
        # writer.writerow(['ip', 'datetime','gmt', 'method', 'path', 'httpversion', 'status_code', 'response'])

        for line in in_file:
            columns = line[:-1].split(' ')
            columns[11] = ' '.join(columns[11:])
            writer.writerow(columns[:12])

def get_host_list(filename):
    with open("uploads/access.log","r") as file:
        data = file.readlines()
        for line in data:
            host=line.strip().split(' ')[-1]
            if host not in host_list:
                host_list.append(host)

           

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    return render_template('/upload.html')

@app.route('/record', methods=(['GET', 'POST']))
def display_record():
    if request.method == 'POST':

        if request.files:

            logfile = request.files['logfile']

            if logfile.filename == '':

                flash('No file selected for uploading', "danger")
                # print('Please Upload a file')
                return redirect(request.url)

            # print(logfile)

            logfile.save(os.path.join(app.config['FILE_UPLOAD'], secure_filename(logfile.filename)))
            
            flash('File successfully uploaded',"success")

            # print('file saved')

            decoded_file = logfile.filename #Takes file name so that we can pass it to the convert_log_to_csv function.
            # print(decoded_file)

        '''Calling Function with filename as argument.'''
        convert_log_to_csv(decoded_file) 
        get_host_list(decoded_file) 

    #Stores dates
    date_list= []    

    #Extracting date from csv file, Row 2nd.
    with open('converted.csv', 'r') as rf:
        reader = csv.reader(rf, delimiter=',')
        for row in reader:
            val = row[1].split(":")[0]
            if val not in date_list:
                date_list.append(val) 
        
    # print(date_list)

    bash_highest_requested_list = []

    for i in date_list:
        data_phonepe = subprocess.check_output(['bash', '-c', f'. day_wise.sh; highest_requested {i}'], text=True).split('\n')
        bash_highest_requested_list.append(data_phonepe[:-1])

    var_phonepe = subprocess.check_output(['bash', '-c', '. test.sh'], text=True).split('\n')
    bash_output_date_wise = zip(date_list, bash_highest_requested_list)
    bash_output = []
    topic=[]
    i=0
    while i<len(var_phonepe):
        if '+' in  var_phonepe[i]:
            l2=[]
            topic.append(var_phonepe[i-1])
            i+=1
            while var_phonepe[i].strip()!='':
                l2.append(var_phonepe[i].split(','))
                i+=1
            bash_output.append(l2)
        else:i+=1
    return render_template('record.html', data_date_wise=bash_output_date_wise,  other_bash=zip(topic,bash_output), date=date_list)
   

@app.route('/timestamp', methods=['GET', 'POST'])
def timestamp():
    specified_datetime_record = []
    if request.method == "POST":
        fromdate = request.form['from-date']
        fromtime = request.form['from-time']
        print(fromdate)
        print(fromtime)

        todate = request.form['to-date']
        totime = request.form['to-time']
        print(todate)
        print(totime)
        date1 = dt.strptime(fromdate, "%d/%b/%Y")
        date2 = dt.strptime(todate, "%d/%b/%Y")
        time1 = dt.strptime(fromtime, "%H:%M:%S")
        time2 = dt.strptime(totime, "%H:%M:%S")
    
        if(date1 > date2):
            flash('Error!! Check your from date', "danger")
            
        elif(date1 == date2):
            if(time1 > time2):
                flash('Error!! Check your from time', "danger")
                
            else:
                try:
                    specified_datetime_record.append(subprocess.check_output(['bash', '-c', f'. day_wise.sh; specified_timestamp {fromdate} {fromtime} {todate} {totime}'], text=True))
                except:
                    flash('Offfoo !!! Error occured', 'danger')
        else:
            try:
                specified_datetime_record.append(subprocess.check_output(['bash', '-c', f'. day_wise.sh; specified_timestamp {fromdate} {fromtime} {todate} {totime}'], text=True))
            except:
                 flash('Offfoo !!! Please enter the timstamps correctly', 'danger')
    
        # print(specified_datetime_record)

    
    

        # print(hostname)
    return render_template('timestamp.html', record_date=specified_datetime_record)

@app.route('/host_record', methods=['GET', 'POST'])
def hostname_record():
    if request.method == 'POST':
        hostname = request.form['hostname']
        print(hostname)
        print(host_list)

        if hostname not in host_list:
            flash(f"Enter correct host name!! BTW These are the hostnames {host_list} ", "info")
            # return redirect(request.url)
        else:
            flash(f'Great your record of host - {hostname}', "success")
            return redirect(url_for('display_record'))

    return render_template('app_record.html')

if __name__ == '__main__':
    app.run(debug=True)