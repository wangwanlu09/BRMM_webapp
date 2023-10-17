from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect
from flask import flash  # message flash

app = Flask(__name__)
app.secret_key="codekey"

dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

@app.route("/")
def home():
    connection = getCursor()
    return render_template("base.html")


@app.route("/listdrivers")
def listdrivers():
    connection = getCursor()
    connection.execute("SELECT d.driver_id, CONCAT(d.surname, ' ', d.first_name) as name, d.date_of_birth, d.age, d.caregiver, c.model, c.drive_class FROM driver as d INNER JOIN car as c ON d.car = c.car_num ORDER BY d.surname;")
    driverList = connection.fetchall()
    print(driverList)
    return render_template("driverlist.html", driver_list = driverList)


@app.route("/listcourses")
def listcourses():
    connection = getCursor()
    connection.execute("SELECT * FROM course;")
    courseList = connection.fetchall()
    return render_template("courselist.html", course_list = courseList)


@app.route("/rundetails", methods=["GET", "POST"])
def rundetails():
    if request.method == "POST":
        select_full_name = request.form.get("name")
    else:
        select_full_name = request.args.get("name")  # Get name parameter

    if select_full_name:
        connection = getCursor()
        connection.execute("SELECT driver_id AS id, CONCAT(surname, ' ', first_name, CASE WHEN age <= 16 THEN ' (J)' ELSE '' END) AS full_name, model, drive_class FROM driver INNER JOIN car ON driver.car = car.car_num WHERE CONCAT(surname, ' ', first_name) = %s", (select_full_name,))
        driverDetails = connection.fetchone()
        if driverDetails:
            id, full_name, model, drive_class = driverDetails
            
            # In this section, execute second query.
            run_query = """
                SELECT dr_id, name, run_num, seconds, cones, wd, 
                    CASE
                        WHEN seconds IS NOT NULL AND cones IS NOT NULL AND wd IS NOT NULL THEN ROUND((seconds + cones * 5 + wd * 10),2)
                        WHEN seconds IS NOT NULL AND cones IS NOT NULL THEN ROUND((seconds + cones * 5),2)
                        WHEN seconds IS NOT NULL AND wd IS NOT NULL THEN ROUND((seconds + wd * 10),2)
                        WHEN seconds IS NOT NULL THEN ROUND(seconds,2)
                        ELSE NULL
                    END AS run_total
                FROM run 
                INNER JOIN course ON run.crs_id = course.course_id
                WHERE dr_id = %s
                ORDER BY Name;
                """
            connection.execute(run_query, (id,))
            runDetails = connection.fetchall()
            
            return render_template("rundetails.html", full_names=get_full_names(), driverDetails=(id, full_name, model, drive_class), runDetails=runDetails)
        
    return render_template("rundetails.html", full_names=get_full_names())

def get_full_names():
    connection = getCursor()
    connection.execute ("SELECT CONCAT(surname, ' ', first_name) FROM driver ORDER BY surname;")
    full_names = [row[0] for row in connection.fetchall()]
    return full_names


@app.route("/listresults")
def listresults():
    connection = getCursor()
    results_query="""
            SELECT
            d.driver_id,
            CONCAT(surname, ' ', first_name, CASE WHEN age <= 16 THEN ' (J)' ELSE '' END) AS full_name, 
            c.model, r.crs_id, 
            CASE
                WHEN MIN(min_course_time) IS NULL THEN 'dnf'
                ELSE ROUND(MIN(min_course_time), 2)
            END AS min_course_time
            FROM driver AS d
            INNER JOIN car AS c ON d.car = c.car_num
            LEFT JOIN (
            SELECT dr_id, crs_id,
                CASE
                    WHEN seconds IS NOT NULL AND cones IS NOT NULL AND wd IS NOT NULL THEN ROUND((seconds + cones * 5 + wd * 10),2)
			        WHEN seconds IS NOT NULL AND cones IS NOT NULL THEN ROUND((seconds + cones * 5),2)
			        WHEN seconds IS NOT NULL AND wd IS NOT NULL THEN ROUND((seconds + wd * 10),2)
			        WHEN seconds IS NOT NULL THEN ROUND(seconds,2)
                END AS min_course_time
            FROM run
            ) AS r ON d.driver_id = r.dr_id
            GROUP BY d.driver_id, r.crs_id
            ORDER BY d.driver_id ASC, r.crs_id ASC;
            """
    connection.execute(results_query)
    resultsList = connection.fetchall()
    # Sort the results by overall result
    #resultsList.sort(key=lambda x: x[5])  
    return render_template("resultslist.html", results_list=resultsList)



@app.route("/graph")
def showgraph():
    connection = getCursor()
    bestDriverList= connection.fetchall()
    connection.execute()
    top5graph = connection.fetchall()
    # connection.execute("SELECT * FROM 
    # Insert code to get top 5 drivers overall, ordered by their final results.
    # Use that to construct 2 lists: bestDriverList containing the names, resultsList containing the final result values
    # Names should include their ID and a trailing space, eg '133 Oliver Ngatai '

    return render_template("top5graph.html", name_list = bestDriverList, value_list = resultsList)

#admin login
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        # Handle the submission logic of the login form
        username = request.form.get("username")
        password = request.form.get("password")
        # Verify the username and password here
        if username == "wangwanlu" and password == "1154882":
            # Login successful
            return redirect(url_for("admin_dashboard"))
        else:
            # Login failed, display an error message
            flash ("The account is wrong. Please check your usernamet.")
    # Render the login page
    return render_template("adminLog.html")

# Example admin dashboard page
@app.route("/admin/dashboard")
def admin_dashboard():
    connection = getCursor()
    connection.execute("SELECT d.driver_id, CONCAT(d.surname, ' ', d.first_name) as name, d.date_of_birth, d.age, d.caregiver, c.model, c.drive_class FROM driver as d INNER JOIN car as c ON d.car = c.car_num ORDER BY d.age DESC,d.surname DESC;")
    juniorList = connection.fetchall()
    return render_template("juniorlist.html", junior_list=juniorList)

