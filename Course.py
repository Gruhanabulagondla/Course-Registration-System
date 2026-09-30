import sqlite3

DATABASE = "course_registration.db"


# -------------------------------
# DATABASE CONNECTION
# -------------------------------
def connect():
    return sqlite3.connect(DATABASE)


# -------------------------------
# CREATE TABLES
# -------------------------------
def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            year INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            instructor TEXT NOT NULL,
            seats INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            registration_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            status TEXT DEFAULT 'Registered',
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            FOREIGN KEY(course_id) REFERENCES courses(course_id)
        )
    """)

    conn.commit()
    conn.close()


# -------------------------------
# ADD SAMPLE STUDENTS
# -------------------------------
def add_sample_students():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]

    if count == 0:
        students = [
            ("Rahul", "CSE", 2),
            ("Anjali", "CSE-AI", 3),
            ("Kiran", "ECE", 2),
            ("Sneha", "CSE", 1)
        ]

        cursor.executemany("""
            INSERT INTO students
            (name, department, year)
            VALUES (?, ?, ?)
        """, students)

        conn.commit()

    conn.close()


# -------------------------------
# ADD SAMPLE COURSES
# -------------------------------
def add_sample_courses():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM courses")
    count = cursor.fetchone()[0]

    if count == 0:
        courses = [
            ("Python Programming", "Dr. Kumar", 30),
            ("Java Programming", "Prof. Sharma", 25),
            ("Machine Learning", "Dr. Reddy", 20),
            ("Database Management", "Prof. Priya", 30),
            ("Web Development", "Dr. Anil", 25)
        ]

        cursor.executemany("""
            INSERT INTO courses
            (course_name, instructor, seats)
            VALUES (?, ?, ?)
        """, courses)

        conn.commit()

    conn.close()


# -------------------------------
# VIEW STUDENTS
# -------------------------------
def view_students():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    print("\n--- Students ---")

    for student in students:
        print(
            f"ID: {student[0]} | "
            f"Name: {student[1]} | "
            f"Department: {student[2]} | "
            f"Year: {student[3]}"
        )

    conn.close()


# -------------------------------
# ADD STUDENT
# -------------------------------
def add_student():
    name = input("Enter student name: ")
    department = input("Enter department: ")
    year = int(input("Enter year: "))

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students
        (name, department, year)
        VALUES (?, ?, ?)
    """, (name, department, year))

    conn.commit()

    print("Student added successfully.")
    print("Student ID:", cursor.lastrowid)

    conn.close()


# -------------------------------
# VIEW COURSES
# -------------------------------
def view_courses():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    print("\n--- Available Courses ---")

    for course in courses:
        print(
            f"ID: {course[0]} | "
            f"Course: {course[1]} | "
            f"Instructor: {course[2]} | "
            f"Available Seats: {course[3]}"
        )

    conn.close()


# -------------------------------
# ADD COURSE
# -------------------------------
def add_course():
    course_name = input("Enter course name: ")
    instructor = input("Enter instructor name: ")
    seats = int(input("Enter number of seats: "))

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO courses
        (course_name, instructor, seats)
        VALUES (?, ?, ?)
    """, (course_name, instructor, seats))

    conn.commit()

    print("Course added successfully.")
    print("Course ID:", cursor.lastrowid)

    conn.close()


# -------------------------------
# REGISTER FOR COURSE
# -------------------------------
def register_course():

    view_students()
    student_id = int(input("\nEnter Student ID: "))

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM students
        WHERE student_id = ?
    """, (student_id,))

    student = cursor.fetchone()

    if not student:
        print("Student not found.")
        conn.close()
        return

    view_courses()
    course_id = int(input("\nEnter Course ID: "))

    cursor.execute("""
        SELECT * FROM courses
        WHERE course_id = ?
    """, (course_id,))

    course = cursor.fetchone()

    if not course:
        print("Course not found.")
        conn.close()
        return

    if course[3] <= 0:
        print("No seats available.")
        conn.close()
        return

    # Check duplicate registration
    cursor.execute("""
        SELECT * FROM registrations
        WHERE student_id = ?
        AND course_id = ?
        AND status = 'Registered'
    """, (student_id, course_id))

    existing = cursor.fetchone()

    if existing:
        print("Student is already registered for this course.")
        conn.close()
        return

    cursor.execute("""
        INSERT INTO registrations
        (student_id, course_id)
        VALUES (?, ?)
    """, (student_id, course_id))

    cursor.execute("""
        UPDATE courses
        SET seats = seats - 1
        WHERE course_id = ?
    """, (course_id,))

    conn.commit()

    print("\nCourse registration successful!")
    print("Registration ID:", cursor.lastrowid)

    conn.close()


# -------------------------------
# VIEW REGISTRATIONS
# -------------------------------
def view_registrations():

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            registrations.registration_id,
            students.name,
            students.department,
            courses.course_name,
            courses.instructor,
            registrations.status
        FROM registrations
        JOIN students
        ON registrations.student_id = students.student_id
        JOIN courses
        ON registrations.course_id = courses.course_id
    """)

    registrations = cursor.fetchall()

    print("\n--- Course Registrations ---")

    if not registrations:
        print("No registrations found.")
    else:
        for registration in registrations:
            print(
                f"Registration ID: {registration[0]} | "
                f"Student: {registration[1]} | "
                f"Department: {registration[2]} | "
                f"Course: {registration[3]} | "
                f"Instructor: {registration[4]} | "
                f"Status: {registration[5]}"
            )

    conn.close()


# -------------------------------
# SEARCH STUDENT REGISTRATIONS
# -------------------------------
def search_student():

    student_id = int(input("Enter Student ID: "))

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            students.name,
            students.department,
            courses.course_name,
            courses.instructor,
            registrations.status
        FROM registrations
        JOIN students
        ON registrations.student_id = students.student_id
        JOIN courses
        ON registrations.course_id = courses.course_id
        WHERE students.student_id = ?
    """, (student_id,))

    registrations = cursor.fetchall()

    print("\n--- Student Courses ---")

    if not registrations:
        print("No course registrations found.")
    else:
        print("Student:", registrations[0][0])
        print("Department:", registrations[0][1])

        for registration in registrations:
            print(
                f"Course: {registration[2]} | "
                f"Instructor: {registration[3]} | "
                f"Status: {registration[4]}"
            )

    conn.close()


# -------------------------------
# DROP COURSE
# -------------------------------
def drop_course():

    registration_id = int(input("Enter Registration ID: "))

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT course_id, status
        FROM registrations
        WHERE registration_id = ?
    """, (registration_id,))

    registration = cursor.fetchone()

    if not registration:
        print("Registration not found.")
        conn.close()
        return

    if registration[1] == "Dropped":
        print("Course is already dropped.")
        conn.close()
        return

    cursor.execute("""
        UPDATE registrations
        SET status = 'Dropped'
        WHERE registration_id = ?
    """, (registration_id,))

    cursor.execute("""
        UPDATE courses
        SET seats = seats + 1
        WHERE course_id = ?
    """, (registration[0],))

    conn.commit()

    print("Course dropped successfully.")

    conn.close()


# -------------------------------
# MAIN MENU
# -------------------------------
def main():

    create_tables()
    add_sample_students()
    add_sample_courses()

    while True:

        print("\n================================")
        print("     COURSE REGISTRATION SYSTEM")
        print("================================")
        print("1. View Students")
        print("2. Add Student")
        print("3. View Courses")
        print("4. Add Course")
        print("5. Register for Course")
        print("6. View Registrations")
        print("7. Search Student Courses")
        print("8. Drop Course")
        print("9. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            view_students()

        elif choice == "2":
            add_student()

        elif choice == "3":
            view_courses()

        elif choice == "4":
            add_course()

        elif choice == "5":
            register_course()

        elif choice == "6":
            view_registrations()

        elif choice == "7":
            search_student()

        elif choice == "8":
            drop_course()

        elif choice == "9":
            print("Thank you for using Course Registration System!")
            break

        else:
            print("Invalid choice. Please try again.")


main()