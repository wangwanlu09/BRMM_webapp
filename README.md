# wangwanlu636S22023webapp

# COMP636 Web App Design - Motorkhana Report

## Project Overview

### Project Objectives and Significance

**Project Objectives:** This project aims to develop a web-based application for efficient data management between drivers and administrators. It focuses on:

- **Run Data Tracking:** Recording and tracking driving run data, including time and routes, for drivers.

- **Analysis and Improvement:** Analyzing performance and providing feedback to help drivers enhance their skills.

- **Compliance and Oversight:** Supporting administrators in ensuring legal compliance.

- **Communication and Feedback:** Enabling effective communication between administrators and drivers.

- **Data Visualization:** Providing visual insights through charts and statistics.

### Usage Scenarios and Audience

**Usage Scenarios:** The project caters to drivers and administrators:

- **Drivers:** Record data, assess performance, and receive recommendations.

- **Administrators:** Manage driver data, communicate, and ensure compliance.

## Web application Structure

- The project is built using Python and Flask, as required by the COMP636 course.
- Bootstrap CSS is used to provide style and formatting.
- The project is connected to a MySQL database using the MySQL connection library.
- Multiple routes and view functions are created in Flask to fulfill web functionality requirements.

### Technology Stack

- Python: The project is primarily developed using the Python programming language.
- Flask: Flask framework is used to build the web application, handling HTTP requests and responses.
- MySQL: MySQL database is used for data storage and retrieval.
- Bootstrap CSS: Bootstrap CSS enhances the appearance of the web pages and incorporates responsive design.

### Jinja2 and HTML

The project also employs the following technologies for web view construction:

- **Jinja2 Template Engine:** Jinja2 allows dynamic data to be embedded in HTML templates for content generation. It is integrated into Flask, enabling the insertion of Python code into HTML.

- **HTML Templates:** HTML templates are used to define the structure, layout, and appearance of web pages. They are located in the "templates" directory of the project and are rendered by the Jinja2 template engine. The HTML structure provided incorporates responsive design with Bootstrap CSS.

### Routes and View Functions

In the project, Flask's routes and view functions are used to handle HTTP requests and generate HTTP responses. View functions are typically associated with specific routes (URL paths). They retrieve data from the database during a request and pass this data to Jinja2 templates for HTML response generation. Routes and view functions are central to the core functionality of the project.

### Main Routes and Functions

Here are some of the main routes and functions in the project:

- **Home Route (`/`):** The `home()` function handles requests to the root path. It renders the template named "base.html" using the `render_template()` method, displaying the main content of the project's homepage.

- **List Drivers Route (`/listdrivers`):** The `listdrivers()` function processes requests to the `/listdrivers` path. It establishes a connection to the database, executes an SQL query to retrieve driver list data, passes this data to the `driverlist.html` template, and then presents the driver list on the web page.

- **List Courses Route (`/listcourses`):** The `listcourses()` function handles requests to the `/listcourses` path. It retrieves data from the database related to courses and presents the acquired course data on a web page.

- **Overall Results Route (`/listresults`):** The `listresults()` function displays comprehensive driver results by retrieving and formatting data from the database, presenting it in the `resultslist.html` template. This route is used to view the overall results of drivers, including the minimum time for each course and the total time. It extracts data from the database and calculates overall results.

- **Chart Route (`/showgraph`):** The `showgraph()` function is employed by the `/graph` route to gather data from the database and display the top five drivers based on their minimum course times in the `top5graph.html` template.

- **Admin Login Route (`/admin`):** The `admin()` function operates as the handler for the administrator login, performing credential validation through POST requests, directing to admin dashboard upon successful login, and rendering the "adminLog.html" template for GET requests on the `/admin` route.

- **Admin Dashboard Route (`/admin/dashboard`):** The `admin_dashboard()` function handles both GET and POST requests at the `/admin/dashboard` path. It displays a list of junior drivers and facilitates driver searches. On POST request, it retrieves and presents search results based on provided driver names (surname or first name). The rendered `adminmain.html` template showcases the driver list.

- **Admin Edit Runs Route (`/admin/editruns`):** The `editruns()` function, forming the backbone of the `/admin/editruns route`, facilitates administrators in editing driver run data. It offers filtering by driver and/or course in POST requests. The route enables data retrieval from the database for viewing and editing and presents an interactive interface for selecting drivers and courses via the `admineditrun.html` page. The helper functions get_full_drivers() and get_full_courses() retrieve complete lists of driver and course names, while additional functions like update_db(), get_original_values(), and editruns() are responsible for managing database updates, filtering criteria, and run data modifications.

- **Edit Run Form Route (`/editrunsform/<driver_id>/<course_name>/<run_number>`):** The `editrunsform()` function manages the adjustment of individual driver run details via the `/editrunsform/<driver_id>/<course_name>/<run_number>` route, allowing modifications to run time, cone hits, and wrong directions. It provides error messaging within the "editrunsform.html" template and supports data submission for updates.

- **Admin Add Driver Route (`/admin/adddriver`):** `The adddriver()` function, handled by the `/admin/adddriver` route, manages the addition of new drivers. It validates input fields such as names, birthdates, caregiver information, and car selection. Upon receiving a POST request, it retrieves car details, course information, and associated run numbers from the database. Validating the input, it redirects to the adddriverresult route, passing the verified input. For GET requests, the function renders the `adminadddriver.html` template, displaying form fields and any related error messages. Auxiliary functions like get_car_number(), get_course_name(), and get_caregiver() provide necessary database information to facilitate the driver addition process.

- **Admin Add Driver Result Route (`/admin/adddriver/result`):** This route is responsible for processing data related to adding new drivers, handling both GET and POST requests. The function `adddriverresult()` retrieves and processes the driver's personal details, car information, and course data from the request's arguments. It then performs validations such as confirming the car number's existence. Upon ensuring the data's validity, it inserts the driver's information into the database, incorporating the driver, run, and course tables. If any data is missing or if inconsistencies are found, it provides appropriate feedback or error messages.

- **Admin Add Success Route (`/admin/add/success`):** The `addsuccess()` function serves as the route for displaying a success page. On GET requests, it renders the "successpage.html" template, providing a success message to the user.

## Assumptions and design decisions

### Assumptions

- **Database Structure Consistency:** I assume that the data in the database adheres to a specific structure and data types, including the consistency of key fields. For instance, I may assume that the `driver` table's `driver_id` field is unique.

- **Data Validity Checking:** I assume that the data submitted in the application is valid and legitimate, without invalid input or malicious content. For example, when submitting forms, we might assume that users will not submit malicious scripts.

- **Database Connectivity:** I assume that the database connection is available without network or permission issues. We may assume that the database server is located at a specific address and port and can be accessed via normal network connections.

- **Authorized User Login:** In the administrator login feature, I assume that only authorized administrators can access it, and unauthorized users cannot log in.

- **Data Integrity:** I assume that the data in the database remains complete, without duplicate records or inconsistent data. For instance, we might assume that course names in the `course` table are unique.

- **Database Security Measures:** It is assumed that the database includes security measures such as encrypted passwords, safeguarding sensitive user and administrator credentials.

### Design Decisions

- **Route Design:** I chose to use the Flask framework to create multiple routes, with each route corresponding to different application functionalities. For example, we created routes for displaying driver lists, course lists, editing driver run data, and more. This decision helps us clearly partition the functionality of the application and makes the code structure easier to maintain.

- **Templates and View Functions:** I use the Jinja2 template engine to embed dynamic data into HTML pages. This decision allows us to generate page content in a more flexible way and adheres to the DRY (Don't Repeat Yourself) principle. View functions are responsible for retrieving and processing data, then passing it to the appropriate templates for rendering.

- **HTTP Request Methods:** We use HTTP's GET and POST methods for requesting and sending data. GET is used for retrieving data from the server, while POST is used for submitting form data to the server. In our design, GET requests are typically used for data retrieval (e.g., viewing driver lists), while POST requests are used for submitting form data (e.g., editing driver run data add driver). This decision helps separate data retrieval from data submission.

- **Database Access:** I chose to use a MySQL database for data storage and retrieval. In our design, we need to execute database queries carefully to ensure data consistency and security. This decision provides scalability and advantages in data management.

- **Layout and Navigation:** I implemented responsive design using Bootstrap CSS to ensure the application displays well on various screen sizes. A navigation bar is used for navigating to different pages and functionalities. This decision contributes to a user-friendly interface and a consistent look.

- **Administrator Permissions:** I designed an administrator login feature so that only administrators can access specific management functionalities, such as editing driver run data. This decision helps protect sensitive data from unauthorized access.

- **Form Validation:** I validate form data to ensure its validity and completeness. If form data is invalid or incomplete, appropriate error messages are displayed. This decision improves data quality and user experience.

These are some of the key assumptions and design decisions I considered during the design and development of the application. These decisions play a critical role in ensuring the proper functioning of the application, data integrity, and user satisfaction.

## About Database

### What SQL statement creates the car table and defines its three fields/columns? 

```sql
CREATE TABLE IF NOT EXISTS car (
    car_num INT PRIMARY KEY NOT NULL,
    model VARCHAR(20) NOT NULL,
    drive_class VARCHAR(3) NOT NULL
);
```

- **The provided SQL code creates a table named `car` with three fields/columns**:
`car_num`: as an integer type acting as the primary key.
`model` as a variable character (string) type with a maximum length of 20 characters.
`drive_class` as a variable character (string) type with a maximum length of 3 characters.

### Which line of SQL code sets up the relationship between the car and driver tables?

The relationship between the `car` and `driver` tables is established in the `CREATE TABLE IF NOT EXISTS driver` block using the following lines:

```sql
car INT NOT NULL,
FOREIGN KEY (car) REFERENCES car(car_num)
ON UPDATE CASCADE
ON DELETE CASCADE
```

The line `car INT NOT NULL` in the `CREATE TABLE IF NOT EXISTS driver` block sets up the column in the `driver` table to hold the foreign key referencing the `car_num` column in the `car` table. The `FOREIGN KEY (car) REFERENCES car(car_num)` defines this relationship, ensuring that the `car` field in the `driver` table references the primary key `car_num` in the `car` table. This relationship is set to trigger cascading updates and deletions.

When modifications are made to the referenced `car_num` within the car table, the effects will cascade to the car field in the driver table due to the `ON UPDATE CASCADE` option. Similarly, if a linked `car_num` record in the car table is deleted, the corresponding entry in the driver table's car field will also be removed following the `ON DELETE CASCADE` option.

### Which 3 lines of SQL code insert the Mini and GR Yaris details into the car table?

Certainly, the three lines of SQL code that insert the 'Mini' and 'GR Yaris' details into the `car` table are:

```sql
INSERT INTO car VALUES
(11,'Mini','FWD'),
(17,'GR Yaris','4WD'),
(18,'MX-5','RWD'),
(20,'Camaro','RWD'),
(22,'MX-5','RWD'),
(31,'Charade','FWD'),
(36,'Swift','FWD'),
(44,'BRZ','RWD');
```

The provided SQL code includes multiple insertions; however, specifically, the lines involving the 'Mini' and 'GR Yaris' details correspond to the first two entries within the `INSERT INTO car VALUES` statement. Adjust the SQL file for proper data insertion.

### How to set a default value of 'RWD' for the driver_class field in the SQL？

To set a default value of 'RWD' for the `driver_class` field in the `car` table, a modification in the table definition by adding a `DEFAULT` constraint would be necessary. Below is the altered SQL code to include the default value:

```sql
CREATE TABLE IF NOT EXISTS car (
    car_num INT PRIMARY KEY NOT NULL,
    model VARCHAR(20) NOT NULL,
    drive_class VARCHAR(3) NOT NULL
);
```

```sql
CREATE TABLE IF NOT EXISTS car (
    car_num INT PRIMARY KEY NOT NULL,
    model VARCHAR(20) NOT NULL,
    drive_class VARCHAR(3) NOT NULL DEFAULT 'RWD'
);
```

By including the `DEFAULT 'RWD'` in the `drive_class` field's definition, any new records inserted into the `car` table that don't explicitly specify a `driver_class` value will default to 'RWD'. This setting only applies to subsequent insertions and does not impact existing data.

### Why Is It Important for Drivers and Club Admins to Access Different Routes in an Implemented Login System?

Implementing separate routes and access control for drivers and club administrators is pivotal for a well-structured and secure application:

- **User Roles and Route Segmentation:** By creating dedicated routes for different user roles, such as `/driver` for drivers and `/admin` for club administrators, you ensure that each user role accesses only the pages relevant to their specific functions. This segregation maintains data privacy and integrity.

- **Data Segregation:** Segregating data ensures that users have access only to the data they are authorized to view or manage. For instance, drivers can only view and manage their own run data, while administrators can access and modify data for all drivers. Properly designed database queries and route assignments ensure this segregation.

- **Functionality Separation:** Distinct routes for each user role prevent confusion and misuse. For example, driver routes might allow viewing run data and personal information updates, while admin routes might facilitate functions like adding new drivers or editing run data.

- **Login Verification:** Validating user identities and roles during login is crucial. Using decorators or conditional statements in routes to verify user permissions guarantees that only authorized users can access specific pages based on their roles.

- **Data Security:** Limiting access to sensitive functionalities, such as editing run data, exclusively to administrators ensures higher data security. By controlling access to these routes, the risk of data breaches or unauthorized access is significantly reduced.

By integrating these principles into the code, the application maintains robust data privacy and security, providing role-specific functionalities to meet the unique needs of different user roles. This approach ensures controlled, secure access and effective data management within the application.