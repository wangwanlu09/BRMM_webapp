# wangwanlu636S22023webapp

# COMP636 Web App Design - Motorkha Report

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

- **Admin Dashboard Route (/admin/dashboard):** This route allows administrators to view the list of drivers and perform searches in POST requests.

- **Admin Edit Runs Route (/admin/editruns):** This route is for administrators to edit driver run data, with the option to filter by driver and/or course in POST requests.

- **Edit Run Form Route (/editrunsform/<driver_id>/<course_name>/<run_number>):** This route is used to edit specific driver run data. It allows updates to fields such as run time (seconds), cone hits (cones), and wrong directions (wd) for the selected run. These updates can be made by submitting the form.

- **Admin Add Driver Route (`/admin/adddriver`):** `The adddriver()` function, handled by the `/admin/adddriver` route, manages the addition of new drivers. It validates input fields such as names, birthdates, caregiver information, and car selection. Upon receiving a POST request, it retrieves car details, course information, and associated run numbers from the database. Validating the input, it redirects to the adddriverresult route, passing the verified input. For GET requests, the function renders the `adminadddriver.html` template, displaying form fields and any related error messages. Auxiliary functions like get_car_number(), get_course_name(), and get_caregiver() provide necessary database information to facilitate the driver addition process.

## Assumptions and design decisions

### Assumptions

- **Database Structure Consistency:** I assume that the data in the database adheres to a specific structure and data types, including the consistency of key fields. For instance, I may assume that the `driver` table's `driver_id` field is unique.

- **Data Validity Checking:** I assume that the data submitted in the application is valid and legitimate, without invalid input or malicious content. For example, when submitting forms, we might assume that users will not submit malicious scripts.

- **Database Connectivity:** I assume that the database connection is available without network or permission issues. We may assume that the database server is located at a specific address and port and can be accessed via normal network connections.

- **Authorized User Login:** In the administrator login feature, I assume that only authorized administrators can access it, and unauthorized users cannot log in.

- **Data Integrity:** I assume that the data in the database remains complete, without duplicate records or inconsistent data. For instance, we might assume that course names in the `course` table are unique.

### Design Decisions

- **Route Design:** I chose to use the Flask framework to create multiple routes, with each route corresponding to different application functionalities. For example, we created routes for displaying driver lists, course lists, editing driver run data, and more. This decision helps us clearly partition the functionality of the application and makes the code structure easier to maintain.

- **Templates and View Functions:** I use the Jinja2 template engine to embed dynamic data into HTML pages. This decision allows us to generate page content in a more flexible way and adheres to the DRY (Don't Repeat Yourself) principle. View functions are responsible for retrieving and processing data, then passing it to the appropriate templates for rendering.

- **HTTP Request Methods:** We use HTTP's GET and POST methods for requesting and sending data. GET is used for retrieving data from the server, while POST is used for submitting form data to the server. In our design, GET requests are typically used for data retrieval (e.g., viewing driver lists), while POST requests are used for submitting form data (e.g., editing driver run data). This decision helps separate data retrieval from data submission.

- **Database Access:** I chose to use a MySQL database for data storage and retrieval. In our design, we need to execute database queries carefully to ensure data consistency and security. This decision provides scalability and advantages in data management.

- **Layout and Navigation:** I implemented responsive design using Bootstrap CSS to ensure the application displays well on various screen sizes. A navigation bar is used for navigating to different pages and functionalities. This decision contributes to a user-friendly interface and a consistent look.

- **Administrator Permissions:** I designed an administrator login feature so that only administrators can access specific management functionalities, such as editing driver run data. This decision helps protect sensitive data from unauthorized access.

- **Form Validation:** I validate form data to ensure its validity and completeness. If form data is invalid or incomplete, appropriate error messages are displayed. This decision improves data quality and user experience.

These are some of the key assumptions and design decisions I considered during the design and development of the application. These decisions play a critical role in ensuring the proper functioning of the application, data integrity, and user satisfaction.

## About Database

### Suppose logins were implemented. Why is it important for drivers and the club admin to access different routes? 

Introducing separate routes and access control for drivers and club administrators is essential.

- **User Roles and Route Separation**: In my code, by creating distinct routes and view functions, you ensure that drivers and administrators can only access pages relevant to their roles.   For instance, you can set up a `/driver` route for drivers to view their own run data, while an `/admin` route is created for administrators to perform management tasks. This ensures data privacy and data integrity.

- **Data Segregation**: You can ensure that users with different roles only have access to data they are authorized to view. For example, drivers can only view and edit their own run data, while administrators can view and manage data for all drivers. This is achieved through your database queries and route design.

- **Functionality Separation**: By assigning different functionalities to different user roles, you prevent confusion and system misuse. For example, driver routes might include viewing run data and updating personal information, while admin routes might include adding new drivers and editing run data.

- **Login Verification**: You can validate user identity and roles during login and use decorators or conditional statements in your routes to check if a user has permission to access specific pages. This ensures that only authorized users can access relevant pages.

- **Data Security**: Ensure that only administrators can access sensitive management functionalities like editing run data to protect data security. By restricting access to these routes, you can reduce the risk of data leaks.

Combining these principles with your code helps ensure data privacy and security while providing role-specific functionalities to meet the needs of different user roles. This makes your application more controlled and secure in terms of user access and data management.