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



app = Flask(__name__)


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
    connection.execute("SELECT d.driver_id, CONCAT(d.first_name, ' ', d.surname) as full_name, d.date_of_birth, d.age, d.caregiver, c.model, c.drive_class FROM driver as d INNER JOIN car as c ON d.car = c.car_num ORDER BY d.surname, d.first_name;")
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
        connection.execute("SELECT driver_id AS id, CONCAT(first_name, ' ', surname, CASE WHEN age >= 12 AND age <= 25 THEN ' (J)' ELSE '' END) AS full_name, model, drive_class FROM driver INNER JOIN car ON driver.car = car.car_num WHERE CONCAT(first_name, ' ', surname) = %s", (select_full_name,))
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
                ORDER BY Name ASC;
                """
            connection.execute(run_query, (id,))
            runDetails = connection.fetchall()
            
            return render_template("rundetails.html", full_names=get_full_names(), driverDetails=(id, full_name, model, drive_class), runDetails=runDetails)
        
    return render_template("rundetails.html", full_names=get_full_names())

def get_full_names():
    connection = getCursor()
    connection.execute ("SELECT CONCAT(first_name, ' ', surname) FROM driver ORDER BY surname;")
    full_names = [row[0] for row in connection.fetchall()]
    return full_names

# Overall Results
@app.route("/listresults")
def listresults():
    connection = getCursor()
    results_query = """
        SELECT
        d.driver_id,
        CONCAT(first_name, ' ',surname, CASE WHEN age >= 12 AND age <= 25 THEN ' (J)' ELSE '' END) AS full_name, 
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
                    WHEN seconds IS NOT NULL AND cones IS NOT NULL AND wd IS NOT NULL THEN ROUND((seconds + cones * 5 + wd * 10), 2)
                    WHEN seconds IS NOT NULL AND cones IS NOT NULL THEN ROUND((seconds + cones * 5), 2)
                    WHEN seconds IS NOT NULL AND wd IS NOT NULL THEN ROUND((seconds + wd * 10), 2)
                    WHEN seconds IS NOT NULL THEN ROUND(seconds, 2)
                END AS min_course_time
            FROM run
        ) AS r ON d.driver_id = r.dr_id
        GROUP BY d.driver_id, c.model, r.crs_id 
        ORDER BY d.driver_id ASC, r.crs_id ASC;
    """
    connection.execute(results_query)
    resultsList = connection.fetchall()

    # Create a dictionary to store data for each driver
    driver_data = {}

    for result in resultsList:
        driver_id, full_name, model, course_id, course_time = result[0], result[1], result[2], result[3], result[4]

        # To ensure that the times for Course A, B, C, D, E, and F are stored in the dictionary
        if driver_id not in driver_data:
            driver_data[driver_id] = {'Driver ID': driver_id, 'Name': full_name, 'Car Model': model}

        driver_data[driver_id][course_id] = course_time

    # To calculate the total results and update them
    for driver_id, data in driver_data.items():
        course_times = [data[course] for course in ['A', 'B', 'C', 'D', 'E', 'F']]
        if 'dnf' in course_times:
            data['Overall Results'] = 'NQ'
        else:
            valid_times = [float(time) for time in course_times if time is not None]
            data['Overall Results'] = round(sum(valid_times), 2)

    #Extract data from the dictionary and convert it into a list
    formatted_results = list(driver_data.values())

    # Overall Results sorted
    formatted_results = sorted(formatted_results, key=lambda x: x['Overall Results'] if x['Overall Results'] != 'NQ' else float('inf'))
    return render_template("resultslist.html", results_list=formatted_results)


@app.route("/graph")
def showgraph():
    connection = getCursor()
    Top5_query = """
        SELECT
        d.driver_id,
        CONCAT(first_name, ' ',surname) AS full_name, 
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
                    WHEN seconds IS NOT NULL AND cones IS NOT NULL AND wd IS NOT NULL THEN ROUND((seconds + cones * 5 + wd * 10), 2)
                    WHEN seconds IS NOT NULL AND cones IS NOT NULL THEN ROUND((seconds + cones * 5), 2)
                    WHEN seconds IS NOT NULL AND wd IS NOT NULL THEN ROUND((seconds + wd * 10), 2)
                    WHEN seconds IS NOT NULL THEN ROUND(seconds, 2)
                END AS min_course_time
            FROM run
        ) AS r ON d.driver_id = r.dr_id
        GROUP BY d.driver_id, c.model, r.crs_id 
        ORDER BY d.driver_id ASC, r.crs_id ASC;
    """
    connection.execute(Top5_query)
    resultsList = connection.fetchall()
   
    driver_total_times = {}
    for result in resultsList:
        driver_id, min_course_time = result[0], result[4]
        if driver_id not in driver_total_times:
            driver_total_times[driver_id] = []
        driver_total_times[driver_id].append(min_course_time)

    formatted_results = []
    for result in resultsList:
        driver_id, full_name, model, course_id, course_time = result[0], result[1], result[2], result[3], result[4]
        driver_times = driver_total_times.get(driver_id, [])

        if 'dnf' in driver_times:
            overall_results = 'NQ'
        else:
            valid_times = [float(time) for time in driver_times if time != 'dnf']
            overall_results = round(sum(valid_times), 2)
        
        formatted_result = result + (overall_results,)
        formatted_results.append(formatted_result)

    formatted_results = sorted(formatted_results, key=lambda x: x[5] if x[5] != 'NQ' else float('inf'))

    # Initialize an empty list to store the top 5 unique formatted results
    top5_unique_formatted_results = []
    # Initialize a set to keep track of seen driver IDs to ensure uniqueness
    seen_driver_ids = set()

    for result in formatted_results:
        driver_id = result[0]
        if driver_id not in seen_driver_ids:
            top5_unique_formatted_results.append(result)
            seen_driver_ids.add(driver_id)
        
        if len(top5_unique_formatted_results) >= 5:
            break

    driver_ids = [result[0] for result in top5_unique_formatted_results]
    full_names = [result[1] for result in top5_unique_formatted_results]
    overall_results = [result[5] for result in top5_unique_formatted_results]
    bestDriverList = [f"{driver_ids[i]} {full_names[i]}" for i in range(5)]
    resultsList = overall_results

    return render_template("top5graph.html", name_list=bestDriverList, value_list=resultsList)


#Admin private 
#admin login
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        # Assuming you have clicked the "Log In" button
        return redirect(url_for("admin_dashboard"))
    return render_template("adminLog.html")

#Display junior list & search list
@app.route("/admin/dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if request.method == "POST":
        search_list = searchbar() 
    else:
        search_list = None

    connection = getCursor()
    connection.execute("SELECT d.driver_id, CONCAT(d.first_name, ' ', d.surname, CASE WHEN age >= 12 AND age <= 25 THEN ' (J)' ELSE '' END) as full_name, d.date_of_birth, d.age, d.caregiver, c.model, c.drive_class FROM driver as d INNER JOIN car as c ON d.car = c.car_num ORDER BY d.age DESC, d.surname;")
    juniorList = connection.fetchall()
    return render_template("adminmain.html", junior_list=juniorList, search_list=search_list)

def searchbar():
    if request.method == "POST":
        name = request.form.get("name")

        if name:  # Check if either surname or firstname is provided
            connection = getCursor()
            search_query = """
                SELECT dr_id, CONCAT(first_name, " ", surname) AS full_name, model, name, run_num, seconds, cones, wd
                FROM driver
                INNER JOIN car ON driver.car=car.car_num
                INNER JOIN run ON driver.driver_id=run.dr_id
                INNER JOIN course ON run.crs_id = course.course_id
                WHERE (CONCAT(first_name, " ", surname) LIKE %s)    
                ORDER BY dr_id ASC, name ASC, run_num ASC;
            """
            connection.execute(search_query, ('%' + name + '%',))  #Retrieve records with similar 'surname' or 'first_name' values
            search_list = connection.fetchall()
            return search_list
    return []  # Return an empty list if no search criteria is provided


# Editor part(admin private)
@app.route("/admin/editruns", methods=["GET", "POST"])
def editruns():
    driverRunlist = [] 
    if request.method == "POST":
        select_full_driver = request.form.get("fdriver")
        select_full_course = request.form.get("fcourse")
        new_seconds = request.form.get("new_seconds")  
        new_cones = request.form.get("new_cones") 
        new_wd = request.form.get("new_wd")

        connection = getCursor()

        if select_full_driver and select_full_course:
            query = """
                SELECT driver_id, first_name, surname, 
                name, run_num, seconds, cones, wd
                FROM driver
                INNER JOIN run ON driver.driver_id = run.dr_id
                INNER JOIN course ON run.crs_id = course.course_id
                WHERE CONCAT(driver_id, ' ', first_name, ' ', surname) = %s AND name = %s;
            """
            connection.execute(query, (select_full_driver, select_full_course))

        elif select_full_driver:
            driver_run_query = """
                SELECT driver_id, first_name, surname, 
                name, run_num, seconds, cones, wd
                FROM driver
                INNER JOIN run ON driver.driver_id = run.dr_id
                INNER JOIN course ON run.crs_id = course.course_id
                WHERE CONCAT(driver_id, ' ', first_name, ' ', surname) = %s;
            """
            connection.execute(driver_run_query, (select_full_driver,))

        elif select_full_course:
            course_query = """
                SELECT driver_id, first_name, surname, 
                name, run_num, seconds, cones, wd
                FROM driver
                INNER JOIN run ON driver.driver_id = run.dr_id
                INNER JOIN course ON run.crs_id = course.course_id
                WHERE name = %s
                ORDER BY driver_id;
            """
            connection.execute(course_query, (select_full_course,))

        driverRunlist = connection.fetchall()

        if driverRunlist:
                update_query = """
                    UPDATE driver
                    INNER JOIN run ON driver.driver_id = run.dr_id
                    INNER JOIN course ON run.crs_id = course.course_id
                    SET seconds = %s, cones = %s, wd = %s
                    WHERE CONCAT(driver_id, ' ', first_name, ' ', surname) = %s AND name = %s;
                """
                connection.execute(update_query, (new_seconds, new_cones, new_wd, select_full_driver, select_full_course))


        return render_template("admineditrun.html", full_drivers=get_full_drivers(), full_courses=get_full_courses(), driver_runlist=driverRunlist)
    return render_template("admineditrun.html", full_drivers=get_full_drivers(), full_courses=get_full_courses())

def get_full_drivers():
    connection = getCursor()
    connection.execute("SELECT CONCAT(driver_id, ' ', first_name, ' ', surname) FROM driver;")
    full_drivers = [row[0] for row in connection.fetchall()]
    return full_drivers

def get_full_courses():
    connection = getCursor()
    connection.execute("SELECT name FROM course;")
    full_courses = [row[0] for row in connection.fetchall()]
    return full_courses

# Editor part
@app.route("/admin/adddriver")
def adddriver():
    connection = getCursor()
    return render_template("adminadddriver.html")