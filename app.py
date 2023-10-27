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



#Admin private (adminmain)
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
    driver_id_to_name = {}
    for junior in juniorList:
        driver_id_to_name[junior[0]] = junior[1] 
    # Modify juniorList to update caregiver names
    for i, junior in enumerate(juniorList):
        if junior[4] is not None:  # If there is a caregiver
            if junior[4] in driver_id_to_name:  # Check if caregiver ID is in the dictionary
                juniorList[i] = junior[:4] + (driver_id_to_name[junior[4]],) + junior[5:]
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



# Edit part
# Edit runs(admin private)
# Optional parameter part
@app.route("/admin/editruns", methods=["GET", "POST"])
def editruns():
    driverRunlist = [] 
    if request.method == "POST":
        select_full_driver = request.form.get("fdriver")
        select_full_course = request.form.get("fcourse")

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
        else:
            return render_template ("admineditrun.html", full_drivers=get_full_drivers(), full_courses=get_full_courses())
        
        driverRunlist = connection.fetchall()

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


# Edit parameter
def get_original_values(driver_id, course_name, run_number, cursor):
    # Execute a query to retrieve the original data
    query = """
            SELECT run.seconds, run.cones, run.wd
            FROM run
            INNER JOIN course ON run.crs_id = course.course_id
            WHERE run.dr_id = %s
            AND course.name = %s
            AND run.run_num = %s;
            """
    cursor.execute(query, (driver_id, course_name, run_number))
    original_values = cursor.fetchone()
    print(original_values)

    cursor.fetchall()

   # Convert the query result into a dictionary
    original_values_dict = {
        "seconds": original_values[0],
        "cones": original_values[1],
        "wd": original_values[2]
    }

    return original_values_dict


def update_db(driver_id, course_name, run_number, update_values, cursor):
    error_messages = []

    original_values = get_original_values(driver_id, course_name, run_number, cursor)

    if original_values is None:
        return ["No data found for the specified criteria."]  # Handling Data Not Found Scenarios

    # Initialize Variables and Set Default Values
    new_seconds = original_values["seconds"]
    new_cones = original_values["cones"]
    new_wd = original_values["wd"]

    # Validate and Process Valid Input for "Seconds"
    if "seconds" in update_values:
        new_seconds = update_values["seconds"]
        if re.match(r"^[0-9]*\.?[0-9]+$", new_seconds):  # "Use regular expressions to validate if it's a valid number.
            try:
                new_seconds = float(new_seconds)
                if not (0 <= new_seconds <= 1000):
                    error_messages.append("Please enter a number between 0 and 1000 for Seconds.")
                elif new_seconds == 0:  # Check if input is 0 and set to None
                    new_seconds = None
            except ValueError:
                error_messages.append("Please enter a valid number for Seconds.")
        else:
            error_messages.append("Please enter a valid number for Seconds.")

    # Validate and Process Valid Input for "cones"
    if "cones" in update_values:
        new_cones = update_values["cones"]
        if re.match(r"^[0-9]+$", new_cones):  # Use regular expressions to check if it's a valid integer
            new_cones = int(new_cones)
            if not (0 <= new_cones <= 25):
                error_messages.append("Please enter a number between 0 and 25 for Cones.")
            elif new_cones == 0:  # Check if input is 0 and set to None
                new_cones = None
        else:
            error_messages.append("Please enter a valid number for Cones.")


    # Validate and Process Valid Input for "cones"
    if "wd" in update_values:
        new_wd = update_values["wd"]
        if not re.match(r"^[01]$", new_wd):
            error_messages.append("Please enter '1' or '0' for WD.")

    if error_messages:
        return error_messages

    update_query = "UPDATE run r " \
              "INNER JOIN course c ON r.crs_id = c.course_id " \
              "SET r.seconds = %s, r.cones = %s, r.wd = %s " \
              "WHERE r.dr_id = %s AND r.run_num = %s AND c.name = %s"
    cursor.execute(update_query, (new_seconds, new_cones, new_wd, driver_id, run_number, course_name))

    connection.commit()
    return "Field updated successfully"


@app.route("/editrunsform/<driver_id>/<course_name>/<run_number>", methods=["GET", "POST"])
def editrunsform(driver_id, course_name, run_number):
    error_messages = [] 

    if request.method == "POST":
        edit_field = request.form.get("edit_field")
        new_value = request.form.get("new_value")

        cursor = connection.cursor()

        if new_value is not None and new_value != "":
            if edit_field in ["seconds", "cones", "wd"]:
                result = update_db(driver_id, course_name, run_number, {edit_field: new_value}, cursor)
                if isinstance(result, list):
                    error_messages = result
                else:
                    return "Field updated successfully" 
                cursor.close()

    return render_template("editrunsform.html", driver_id=driver_id, course_name=course_name, run_number=run_number, error_messages=error_messages)


                          
# Edit part
# Add Driver(admin private)
def is_valid_name(name):
    if not re.match(r"^[A-Za-z ]{2,50}$", name):
        return False, "Name must be 2 to 50 characters long and contain only letters and spaces."
    return True, ""

@app.route("/admin/adddriver", methods=["GET", "POST"])
def adddriver():
    error_messages = {
        "firstname": [],
        "surname": [],
        "birthdate":[],
        "caregiver":[],
    }
    if request.method == "POST":
        input_firstname = request.form.get("firstname")
        input_surname = request.form.get("surname")
        selected_driver_type = request.form.get("driverType")
        Select_birthdate = request.form.get("birthdate")
        Select_caregiver = request.form.get("caregiver")
        Select_car_number = request.form.get("carnum")
        select_course_names = request.form.getlist("coursename")
        #course_info_list = request.args.getlist("course_info_list")

         # Ensure these fields are set to the default values if not provided in the form
        seconds = request.form.get("seconds", 0)
        cones = request.form.get("cones")
        wd = request.form.get("wd", 0)

        # Validate names
        is_valid, name_error = is_valid_name(input_firstname)
        if not is_valid:
            error_messages["firstname"].append(name_error)

        is_valid, name_error = is_valid_name(input_surname)
        if not is_valid:
            error_messages["surname"].append(name_error)
            
        # Validate and process based on user's choice
        if selected_driver_type == "junior1":
            # Junior (Age 12 to 25) option is selected
            if not Select_birthdate:
                return "Birthdate is required for this option" 
                # error_messages["birthdate"].append("Birthdate is required for this option.")
            if not Select_caregiver:
                Select_caregiver = None
        elif selected_driver_type == "junior2":
            if not Select_caregiver:
                error_messages["caregiver"].append("Caregiver is required for this option.")
            if not Select_birthdate:
                return "Birthdate is required for this option" 
                # error_messages["birthdate"].append("Birthdate is required for this option.")
        else:
            # Neither option is selected, so set both to None
            Select_birthdate = None
            Select_caregiver = None


        # Assuming Select_birthdate is in the format 'YYYY-MM-DD'
        if Select_birthdate:
            selected_birthdate = datetime.strptime(Select_birthdate, "%Y-%m-%d")
        # Calculate the current date
            current_date = datetime.now()
        # Ensure the selected birthdate is not in the future (i.e., after the current date)
            if selected_birthdate > current_date:
                return "Birthdate cannot be in the future."
                # error_messages["birthdate"].append("Birthdate cannot be in the future.")
            else:
                # Calculate the age
                age = current_date.year - selected_birthdate.year - ((current_date.month, current_date.day) < (selected_birthdate.month, selected_birthdate.day))
        else:
            age = None

        connection = getCursor()
        # add car information
        if Select_car_number:
            car_number_query ="""
                    SELECT car_num 
                    FROM car
                    WHERE car_num = %s
                    """
            connection.execute(car_number_query,(Select_car_number,))
            car_number = connection.fetchone()
            # Car Number Corresponding to Car Model and Drive Class
            if car_number:
                car_query ="""
                    SELECT model, drive_class
                    FROM car
                    WHERE car_num = %s;
                    """
            connection.execute(car_query,(Select_car_number,))
            car = connection.fetchone() 
            if car:
                model, drive_class = car

        if select_course_names:
            # Create lists to store course information
            course_ids = []
            names = []
            images = []

            for course_name in select_course_names:
                course_query = """
                    SELECT course_id, name, image
                    FROM course
                    WHERE name = %s;
                """
                connection.execute(course_query, (course_name,))
                result = connection.fetchone()
                if result:
                    course_id, name, image = result
                    course_ids.append(course_id)
                    names.append(name)
                    images.append(image)


                    for course_id in course_ids:
                        course_query = """
                            SELECT run_num
                            FROM run
                            WHERE crs_id = %s;
                        """
                        connection.execute(course_query, (course_id,))
                        results = connection.fetchall()

                        run_nums = [result[0] for result in results]

                        seconds = [0] * len(course_ids)
                        wd = [0] * len(course_ids)
                        cones = [0] * len(course_ids)

                
        return redirect(url_for('adddriverresult', input_firstname=input_firstname,input_surname=input_surname, 
                        Select_birthdate=Select_birthdate, age=age, Select_caregiver=Select_caregiver, 
                        Select_car_number=Select_car_number, model=model,drive_class=drive_class, 
                        course_ids=course_ids, names=names, images=images, run_nums=run_nums,
                        seconds=seconds, cones=cones, wd=wd))

    return render_template("adminadddriver.html", error_messages=error_messages, caregiver=get_caregiver(), car_number=get_car_number(), course_name=get_course_name())

def get_car_number():
    connection = getCursor()
    connection.execute("SELECT car_num FROM car;")
    car_number = [row[0] for row in connection.fetchall()]
    return car_number

def get_course_name():
    connection = getCursor()
    connection.execute("SELECT name FROM course;")
    course_name = [row[0] for row in connection.fetchall()]
    return course_name

def get_caregiver():
    connection = getCursor()
    connection.execute("SELECT driver_id FROM driver WHERE age IS NULL")
    caregiver = [row[0] for row in connection.fetchall()]
    return caregiver


@app.route("/admin/adddriver/result", methods=["GET", "POST"])
def adddriverresult():
    # driver table
    first_name = request.args.get('input_firstname')
    surname = request.args.get("input_surname")
    date_of_birth = request.args.get('Select_birthdate')
    age = request.args.get('age')
    caregiver = request.args.get('Select_caregiver')
    car = request.args.get('Select_car_number')

    # car table
    model = request.args.get('model')
    drive_class = request.args.get('drive_class')
    car_num = request.args.get('Select_car_number')

    # course table
    course_id = request.args.getlist('course_ids')
    name = request.args.getlist('names')
    image = request.args.getlist('images')

     # run table
    crs_id = request.args.getlist('course_ids')
    run_num = request.args.getlist('run_nums')
    seconds = request.args.getlist('seconds')
    cones = request.args.getlist('cones')
    wd = request.args.getlist('wd')

    
    cursor = connection.cursor()
    if car != car_num:
            connection.rollback()
            return "Invalid car number. Please choose an existing car."
    
    insert_driver_query = """
    INSERT INTO driver (first_name, surname, date_of_birth, age, caregiver, car)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    values_driver = (first_name, surname, date_of_birth, age, caregiver, car_num)
    cursor.execute(insert_driver_query, values_driver)
    new_driver_id = cursor.lastrowid


    run_num_count = 0
    for j in range(len(course_id)):
        insert_run_query = """
        INSERT INTO run (dr_id, crs_id, run_num,seconds,cones,wd)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        values_run = (new_driver_id, crs_id[j], run_num[j], seconds[j], cones[j], wd[j])
        cursor.execute(insert_run_query, values_run)
        run_num_count += 1

    connection.commit()          
    cursor.close()


    return render_template('adddriverresult.html', input_firstname=first_name, input_surname=surname, 
                           Select_birthdate=date_of_birth, age=age, Select_caregiver=caregiver, 
                           Select_car_number=car, model=model, drive_class=drive_class, car_num=car_num,
                           course_ids=course_id, names=name, images=image,
                           run_nums=run_num, seconds=seconds, cones=cones, wd=wd) 


@app.route("/admin/add/success", methods=["GET", "POST"])
def addsuccess():
    return render_template('successpage.html')