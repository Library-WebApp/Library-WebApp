import sqlite3
from datetime import datetime

sql_statements = [ 
    """CREATE TABLE IF NOT EXISTS Item (
            ItemID INTEGER PRIMARY KEY AUTOINCREMENT, 
            Title TEXT NOT NULL,
            Type TEXT NOT NULL,
            AuthorPublisher TEXT,
            AvailabilityStatus BOOLEAN DEFAULT 1,
            ISBN TEXT,
            PublicationYear INTEGER
        );""",

    """CREATE TABLE IF NOT EXISTS Person (
            PersonID INTEGER PRIMARY KEY AUTOINCREMENT, 
            Name TEXT NOT NULL, 
            Address TEXT, 
            PhoneNumber TEXT, 
            Email TEXT UNIQUE, 
            Role TEXT NOT NULL 
            CHECK (Role IN ('Member', 'Librarian', 'Volunteer'))
        );""",
  
    """CREATE TABLE IF NOT EXISTS Member (
            MemberID INTEGER PRIMARY KEY REFERENCES Person(PersonID),
            JoinDate TEXT NOT NULL,
            MembershipStatus TEXT NOT NULL
    );""",
  
    """CREATE TABLE IF NOT EXISTS Librarian (
            LibrarianID INTEGER PRIMARY KEY REFERENCES Person(PersonID),
            HireDate DATE NOT NULL,
            Salary INTEGER NOT NULL
    );""",

    """CREATE TABLE IF NOT EXISTS Volunteer (
            VolunteerID INTEGER PRIMARY KEY REFERENCES Person(PersonID),
            JoinDate TEXT NOT NULL,
            MembershipStatus TEXT NOT NULL
    );""",
  
    """CREATE TABLE IF NOT EXISTS LibraryRoom (
            RoomID INTEGER PRIMARY KEY AUTOINCREMENT,
            Capacity INTEGER NOT NULL,
            RoomType TEXT NOT NULL
    );""",

    """CREATE TABLE IF NOT EXISTS Event (
            EventID INTEGER PRIMARY KEY AUTOINCREMENT,
            EventName TEXT NOT NULL,
            EventDate DATE NOT NULL,
            Attendance INTEGER NOT NULL,
            MaxCapacity INTEGER NOT NULL DEFAULT 20,
            RoomID INTEGER,
            FOREIGN KEY (RoomID) REFERENCES LibraryRoom(RoomID)
    );""",

    """CREATE TABLE IF NOT EXISTS BorrowingRecord (
            RecordID INTEGER PRIMARY KEY AUTOINCREMENT,
            MemberID INTEGER NOT NULL,
            ItemID INTEGER NOT NULL,
            DueDate DATE NOT NULL,
            BorrowDate DATE DEFAULT CURRENT_DATE,
            ReturnDate DATE,
            FineAmount REAL DEFAULT 0,
            FOREIGN KEY (MemberID) REFERENCES Member(MemberID),
            FOREIGN KEY (ItemID) REFERENCES Item(ItemID)
    );""",

   """CREATE TABLE IF NOT EXISTS EventRegistration (
            RegistrationID INTEGER PRIMARY KEY AUTOINCREMENT,
            EventID INTEGER NOT NULL,
            MemberID INTEGER NOT NULL,
            FOREIGN KEY (EventID) REFERENCES Event(EventID),
            FOREIGN KEY (MemberID) REFERENCES Member(MemberID)
    );""",

  """CREATE TABLE IF NOT EXISTS Donation (
            DonationID INTEGER PRIMARY KEY AUTOINCREMENT,
            DonorID INTEGER NOT NULL,
            ItemID INTEGER NOT NULL,
            DateReceived DATE NOT NULL,
            FOREIGN KEY (DonorID) REFERENCES Person(PersonID),
            FOREIGN KEY (ItemID) REFERENCES Item(ItemID)
    );""",

  """CREATE TABLE IF NOT EXISTS HelpRequest (
            RequestID INTEGER PRIMARY KEY AUTOINCREMENT,
            MemberID INTEGER NOT NULL,
            LibrarianID INTEGER,
            RequestDate DATE DEFAULT CURRENT_DATE,
            Description TEXT NOT NULL,
            Status TEXT NOT NULL DEFAULT 'Pending',
            FOREIGN KEY (MemberID) REFERENCES Member(MemberID),
            FOREIGN KEY (LibrarianID) REFERENCES Librarian(LibrarianID)
  );"""
]

triggers = [
    """CREATE TRIGGER IF NOT EXISTS ItemAvailabilityTrigger
       BEFORE INSERT ON BorrowingRecord
       FOR EACH ROW
       WHEN (SELECT AvailabilityStatus FROM Item WHERE ItemID = NEW.ItemID) != 1
       BEGIN
           SELECT RAISE(ABORT, 'Item is not available for borrowing.');
       END;""",

    """CREATE TRIGGER IF NOT EXISTS UpdateItemStatusOnBorrow 
       AFTER INSERT ON BorrowingRecord
       FOR EACH ROW
       BEGIN
           UPDATE Item SET AvailabilityStatus = 0 WHERE ItemID = NEW.ItemID;
       END;""",

    """CREATE TRIGGER IF NOT EXISTS UpdateItemStatusOnReturn 
       AFTER UPDATE ON BorrowingRecord
       FOR EACH ROW
       WHEN NEW.ReturnDate IS NOT NULL
       BEGIN
           UPDATE Item SET AvailabilityStatus = 1 WHERE ItemID = NEW.ItemID;
       END;""",

    """CREATE TRIGGER IF NOT EXISTS UpdateMemberStatusOnBorrow 
       AFTER INSERT ON BorrowingRecord
       FOR EACH ROW
       BEGIN
           UPDATE Member SET MembershipStatus = 'Active' WHERE MemberID = NEW.MemberID;
       END;""",

    """CREATE TRIGGER IF NOT EXISTS UpdateMemberStatusOnReturn 
       AFTER UPDATE ON BorrowingRecord
       FOR EACH ROW
       WHEN NEW.ReturnDate IS NOT NULL
       BEGIN
           UPDATE Member SET MembershipStatus = 'Inactive' WHERE MemberID = NEW.MemberID;
       END;"""
]

def add_item(conn, Item):
    try:
        sql = '''INSERT INTO Item (Title, Type, AuthorPublisher, AvailabilityStatus, ISBN, PublicationYear)
                 VALUES (?, ?, ?, ?, ?, ?)''' 
        cur = conn.cursor()
        cur.execute(sql, Item)
        conn.commit()
        return cur.lastrowid  
    except sqlite3.Error as e:
        print(f"Error inserting item: {e}")
        return None

def add_person(conn, Person):
    sql_check_email = '''SELECT 1 FROM Person WHERE Email = ?'''
    cur = conn.cursor()
    cur.execute(sql_check_email, (Person[3],))
    if cur.fetchone():
        print(f"Error: The email {Person[3]} is already in use.")
        return None
    sql = '''INSERT INTO Person (Name, Address, PhoneNumber, Email, Role) VALUES (?, ?, ?, ?, ?)'''
    cur.execute(sql, Person)
    conn.commit()
    return cur.lastrowid

def add_member(conn, Member):
    sql = '''INSERT INTO Member (MemberID, JoinDate, MembershipStatus) VALUES (?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, Member)
    conn.commit()
    return cur.lastrowid

def add_librarian(conn, Librarian):
    sql = '''INSERT INTO Librarian (LibrarianID, HireDate, Salary) VALUES (?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, Librarian)
    conn.commit()
    return cur.lastrowid

def add_volunteer(conn, Volunteer):
    sql = '''INSERT INTO Volunteer (VolunteerID, JoinDate, MembershipStatus) VALUES (?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, Volunteer)
    conn.commit()
    return cur.lastrowid

def add_event(conn, Event):
    sql = '''INSERT INTO Event (EventName, EventDate, Attendance, MaxCapacity, RoomID) VALUES (?, ?, ?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, Event)
    conn.commit()
    return cur.lastrowid

def add_library_room(conn, LibraryRoom):
    sql = '''INSERT INTO LibraryRoom (Capacity, RoomType) VALUES (?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, LibraryRoom)
    conn.commit()
    return cur.lastrowid

def add_borrowing_record(conn, BorrowingRecord):
    sql = '''INSERT INTO BorrowingRecord (MemberID, ItemID, DueDate, BorrowDate, ReturnDate, FineAmount) VALUES (?, ?, ?, ?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, BorrowingRecord)
    conn.commit()
    return cur.lastrowid

def add_event_registration(conn, EventRegistration): 
    sql = '''INSERT INTO EventRegistration (EventID, MemberID) VALUES (?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, EventRegistration)
    conn.commit()
    return cur.lastrowid

def add_donation(conn, Donation):
    sql = '''INSERT INTO Donation (DonorID, ItemID, DateReceived) VALUES (?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, Donation)
    conn.commit()
    return cur.lastrowid

def add_donation_with_current_date(conn, donor_id, item_id):
    cur = conn.cursor()
    cur.execute("""
            INSERT INTO Donation (DonorID, ItemID, DateReceived)
                VALUES (?, ?, ?)
        """, (donor_id, item_id, datetime.now().strftime('%Y-%m-%d')))
    conn.commit()

def add_help_request(conn, HelpRequest):
    sql = '''INSERT INTO HelpRequest (MemberID, LibrarianID, RequestDate, Description, Status) VALUES (?, ?, ?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, HelpRequest)
    conn.commit()
    return cur.lastrowid

def populate_sample_data(conn):
    # Sample LibraryRoom data
    rooms = [
        (30, 'Study Room'),
        (100, 'Event Hall'),
        (20, 'Computer Lab'),
        (15, 'Meeting Room'),
        (50, 'Reading Room'),
        (10, 'Quiet Room'),
        (25, 'Conference Room'),
        (40, 'Lounge'),
        (60, 'Workshop Area'),
        (70, 'Classroom')
    ]

    for room in rooms:
        add_library_room(conn, room)

    # Sample Person/Member data
    persons = [
       ('John Doe', '123 Main St', '555-0101', 'john@email.com', 'Member'),
       ('Jane Smith', '456 Oak Ave', '555-0102', 'jane@email.com', 'Librarian'),
       ('Bob Wilson', '789 Pine Rd', '555-0103', 'bob@email.com', 'Member'),
       ('Alice Brown', '321 Elm St', '555-0104', 'alice@email.com', 'Volunteer'),
       ('Eve White', '101 Maple St', '555-0105', 'eve@email.com', 'Member'),
       ('Sam Black', '202 Pine St', '555-0106', 'sam@email.com', 'Member'),
       ('Mia Green', '303 Oak St', '555-0107', 'mia@email.com', 'Librarian'),
       ('Liam Gray', '404 Cedar St', '555-0108', 'liam@email.com', 'Volunteer'),
       ('Sophia Blue', '505 Birch St', '555-0109', 'soph@email.com', 'Member'),
       ('Oliver Ng', '606 Willow St', '555-0110', 'oliver@email.com', 'Librarian'),
       ('Lily Pink', '707 Cherry St', '555-0111', 'lily@email.com', 'Librarian'),
       ('Jack Orange', '808 Walnut St', '555-0112', 'jack@email.com', 'Volunteer'),
       ('Emma Purple', '909 Pine St', '555-0113', 'emma@email.com', 'Member'),
       ('Noah Brown', '1011 Elm St', '555-0114', 'noah@email.com', 'Member'),
       ('Olivia Green', '1112 Maple St', '555-0115', 'oliv@email.com', 'Librarian'),
       ('William Gray', '1213 Cedar St', '555-0116', 'willia@email.com', 'Volunteer'),
       ('Ava Blue', '1314 Birch St', '555-0117', 'ava@email.com', 'Member'),
       ('Ethan Yellow', '1415 Willow St', '555-0118', 'ethan@email.com', 'Member'),
       ('Mia Pink', '1516 Cherry St', '555-0119', 'miaP@email.com', 'Librarian'),
       ('Michael Orange', '1617 Walnut St', '555-0120', 'michael@email.com', 'Volunteer'),
       ('Emily Purple', '1718 Pine St', '555-0121', 'emily@email.com', 'Volunteer'),
        ('Bob Black', '1819 Oak St', '555-0122', 'bobie@email.com', 'Volunteer'),
        ('Sophia White', '1920 Elm St', '555-0123', 'sophia@email.com', 'Volunteer'),
        ('Bobby Green', '2021 Maple St', '555-0124', 'bobby@email.com', 'Volunteer'),
        ('Emma Red', '2222 Pine St', '555-0125', 'em@email.com', 'Volunteer'),
        ('James Blue', '2323 Oak St', '555-0126', 'james@email.com', 'Librarian'),
        ('Olivia Yellow', '2424 Elm St', '555-0127', 'oliviaY@email.com', 'Librarian'),
        ('Stewart Green', '2525 Maple St', '555-0128', 'stewart@email.com', 'Librarian'),
        ('Jordan Blue', '2626 Birch St', '555-0129', 'jordan@email.com', 'Librarian'),
        ('Emily Robert' , '2727 Willow St', '555-0130', 'emy@email.com', 'Member'),
        ('Malaika Qureshi', '2828 Cedar St', '555-0131', 'malaika@email.com', 'Librarian'),
        ('Lebron James', '2929 Birch St', '555-0132', 'lebron@email.com', 'Volunteer'),
        ('Snow White', '3030 Willow St', '555-0133', 'snow@email.com', 'Volunteer'),
        ('Rachel Zegler', '3131 Cedar St', '555-0134', 'rachel@email.com', 'Volunteer')
    ]

    member_join_date = datetime.now().strftime('%Y-%m-%d')
    volunteer_join_date = datetime.now().strftime('%Y-%m-%d')
    librarian_hire_date = datetime.now().strftime('%Y-%m-%d')
    librarian_salary = 80000

    for person in persons:
        name, address, phone, email, role = person
        person_id = add_person(conn, (name, address, phone, email, role))
        if person_id is None:
            print(f"Failed to add person {name}")
            continue
        if role == 'Member':
            add_member(conn, (person_id, member_join_date, 'Active'))
        elif role == 'Volunteer':
            add_volunteer(conn, (person_id, volunteer_join_date, 'Active'))
        elif role == 'Librarian':
            add_librarian(conn, (person_id, librarian_hire_date, librarian_salary))

    # Sample Items
    items = [
        ('Sample Book', 'Book', 'Sample Publisher', 1, '1234567890', 2023),
        ('The Great Gatsby', 'Book', 'F. Scott Fitzgerald', 1, '978-0743273565', 1925),
        ('To Kill a Mockingbird', 'Book', 'Harper Lee', 1, '978-0446310789', 1960),
        ('Python Programming', 'Book', 'John Smith', 1, '978-1234567890', 2020),
        ('Inception', 'DVD', 'Warner Bros', 1, None, 2010),
        ('The Matrix', 'DVD', 'Warner Bros', 1, None, 1999),
        ('The Hobbit', 'Book', 'J.R.R. Tolkien', 1, '978-0547928227', 1937),
        ('1984', 'Book', 'George Orwell', 1, '978-0451524935', 1949),
        ('The Catcher in the Rye', 'Book', 'J.D. Salinger', 1, '978-0316769488', 1951),
        ('The Lion King', 'DVD', 'Disney', 1, None, 1994)
    ]

    for item in items:
        add_item(conn, item)
    
    # Sample Events
    events = [
        ('Book Club Meeting', '2024-02-01', 20, 30, 1),
        ('Children Story Time', '2024-02-05', 50, 100, 2),
        ('Programming Workshop', '2024-02-10', 62, 70, 10),
        ('Movie Night: The Matrix', '2024-02-15', 10, 15, 4),
        ('Art Exhibition Opening', '2024-02-20', 32, 50, 5),
        ('Python for Beginners', '2024-02-25', 19, 20, 3),
        ('Digital Literacy Workshop', '2024-03-01', 20, 25, 7),
        ('Poetry Reading Night', '2024-03-05', 27, 50, 5),
        ('Photography Exhibition', '2024-03-10', 60, 60, 9),
        ('Tech Talk: AI in Everyday Life', '2024-03-15', 82, 100, 2)
    ]

    for event in events:
        add_event(conn, event)

    event_registrations = [
        (1, 1),  # Member 1 registers for Book Club Meeting
        (2, 2),  # Member 2 registers for Children Story Time
        (3, 10), # Member 3 registers for Programming Workshop
        (4, 4),  # Member 4 registers for Movie Night: The Matrix
        (5, 5),  # Member 5 registers for Art Exhibition Opening
        (6, 3),  # Member 6 registers for Python for Beginners
        (7, 7),  # Member 7 registers for Digital Literacy Workshop
        (8, 5),  # Member 8 registers for Poetry Reading Night
        (9, 9),  # Member 9 registers for Photography Exhibition
        (10, 2)  # Member 10 registers for Tech Talk: AI in Everyday Life
    ]

    for event_registration in event_registrations:
        add_event_registration(conn, event_registration)
    
    donation = [
        (1, 1, '2025-01-01'),
        (2, 2, '2025-02-07'),
        (3, 3, '2024-01-01'),
        (1, 4, '2024-02-01'),
        (5, 8, '2024-03-05'),
        (2, 5, '2024-02-05'),
        (3, 6, '2024-02-10'),
        (4, 7, '2024-03-01'),
        (6, 9, '2024-03-10'),
        (7, 10, '2024-03-15')
    ]
    
    for donation_record in donation:
        add_donation(conn, donation_record)

    borrow = [
        (1, 1, '2025-01-01', '2024-03-01', '2024-03-31', 0.0),  
        (2, 2, '2024-02-10', '2024-01-15', '2024-02-15', 0.0),    
        (3, 3, '2024-05-01', '2024-02-01', '2024-03-02', 1.5),       
        (1, 4, '2024-04-15', '2024-02-10', '2024-03-10', 0.0),    
        (4, 9, '2024-08-01', '2024-06-10', '2024-07-10', 0.0),    
        (5, 6, '2024-06-01', '2024-04-01', '2024-05-01', 0.0),      
        (6, 7, '2024-07-15', '2024-05-15', '2024-06-15', 0.0),   
        (9, 8, '2024-06-10', '2024-04-25', '2024-05-10', 0.0), 
        (8, 10, '2024-09-01', '2024-07-15', '2024-07-25', 0.0),   
        (10, 5, '2024-08-15', '2024-06-20', '2024-07-10', 0.0) 
    ]

    for borrow_record in borrow:
        add_borrowing_record(conn, borrow_record)

    help_requests = [
        (1, None, "2025-03-28", "Need help finding research papers on AI.", "Pending"),
        (2, 1, "2025-03-27", "Assistance with online library access.", "In Progress"),
        (3, None, "2025-03-26", "Requesting book recommendations on philosophy.", "Pending"),
        (4, 2, "2025-03-25", "Issue with returning a borrowed book.", "Resolved"),
        (5, None, "2025-03-24", "Want to learn how to use library catalog search.", "Pending"),
        (6, 3, "2025-03-23", "Requesting guidance on citing sources for a research paper.", "Resolved"),
        (7, None, "2025-03-22", "Inquiry about library membership renewal process.", "Pending"),
        (8, 4, "2025-03-21", "Need assistance accessing e-books on a tablet.", "In Progress"),
        (9, 1, "2025-03-20", "Looking for historical newspaper archives from the 1900s.", "Pending"),
        (10, None, "2025-03-19", "Question about interlibrary loan procedures.", "Resolved")
    ]
    
    for help_request in help_requests:
        add_help_request(conn, help_request)

try:
    with sqlite3.connect('354_mini_project.db') as conn:
        cursor = conn.cursor()

        # execute table creation statements
        for statement in sql_statements:
            try:
                cursor.execute(statement)
            except sqlite3.OperationalError as e:
                print(f"Warning: Could not execute statement - {e}")

        # execute trigger creation statements
        for trigger in triggers:
            try:
                cursor.execute(trigger)
            except sqlite3.OperationalError as e:
                print(f"Warning: Could not create trigger - {e}")

        conn.commit()
        print("Database schema created successfully with tables and triggers.")
except sqlite3.Error as e:
    print("Failed to initialize database:", e)

try:
    with sqlite3.connect('354_mini_project.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Item")
        item_count = cursor.fetchone()[0]

        if item_count == 0:
            populate_sample_data(conn)
            print("Sample data inserted successfully.")
        else:
            print("Database already contains data - skipping sample data insertion.")
except sqlite3.Error as e:
    print("Error working with sample data:", e)