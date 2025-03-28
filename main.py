import sqlite3

sql_statements = [ 
    """CREATE TABLE IF NOT EXISTS Item (
            ItemID INTEGER PRIMARY KEY AUTOINCREMENT, 
            Title TEXT NOT NULL,
            Type TEXT NOT NULL,
            AuthorPublisher TEXT,
            AvailabilityStatus BOOLEAN DEFAULT 1,
            ISBN TEXT,
            PublicationYear INTEGER,
            DueDate DATE,
            BorrowerID INTEGER,
            FOREIGN KEY (BorrowerID) REFERENCES Member(MemberID)
        );""",

    """CREATE TABLE IF NOT EXISTS Person (
            PersonID INTEGER PRIMARY KEY AUTOINCREMENT, 
            Name TEXT NOT NULL, 
            Address TEXT, 
            PhoneNumber TEXT, 
            Email TEXT UNIQUE, 
            Role TEXT NOT NULL 
            CHECK (Role IN ('Member', 'Librarian', 'Volunteer')))
        );""",
  
    """CREATE TABLE IF NOT EXISTS Member (
            MemberID INTEGER NOT NULL,
            JoinDate TEXT NOT NULL,
            MembershipStatus TEXT NOT NULL,
            FOREIGN KEY (MemberID) REFERENCES Person(PersonID)
    );""",
  
    """CREATE TABLE IF NOT EXISTS Librarian (
            LibrarianID INTEGER PRIMARY KEY,
            HireDate DATE NOT NULL,
            Salary INTEGER NOT NULL,
            FOREIGN KEY (LibrarianID) REFERENCES Person(PersonID)
    );""",
  
    """CREATE TABLE IF NOT EXISTS Event (
            EventID INTEGER PRIMARY KEY AUTOINCREMENT,
            EventName TEXT NOT NULL,
            EventDate DATE NOT NULL,
            Attendance INTEGER NOT NULL,
            RoomID INTEGER,
            FOREIGN KEY (RoomID) REFERENCES LibraryRoom(RoomID)
    );""",
  
    """CREATE TABLE IF NOT EXISTS LibraryRoom (
            RoomID INTEGER PRIMARY KEY AUTOINCREMENT,
            Capacity INTEGER NOT NULL,
            RoomType TEXT NOT NULL
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
            ItemTitle TEXT NOT NULL,
            ItemType TEXT NOT NULL,
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

  );""",

    """CREATE TABLE IF NOT EXISTS Volunteer (
            VolunteerID INTEGER NOT NULL,
            Name TEXT NOT NULL,
            EmailAddress TEXT NOT NULL,
            PhoneNumber TEXT
    );"""
]

triggers = [
    """CREATE TRIGGER IF NOT EXISTS ItemAvailabilityTrigger (
            BEFORE INSERT ON BorrowingRecord
            FOR EACH ROW
            WHEN(SELECT AvailabilityStatus FROM Item WHERE ItemID = NEW.ItemID) != 1
            BEGIN
                SELECT RAISE(ABORT, 'Item is not available for borrowing.');
            END;
    );""",
  
    """CREATE TRIGGER IF NOT EXISTS UpdateItemStatusOnBorrow (
            AFTER INSERT ON BorrowingRecord
            FOR EACH ROW
            BEGIN
                UPDATE Item SET AvailabilityStatus = 0 WHERE ItemID = NEW.ItemID;
            END;
    );""",
  
  """CREATE TRIGGER IF NOT EXISTS UpdateItemStatusOnReturn (
            AFTER UPDATE ON BorrowingRecord
            FOR EACH ROW
            WHEN NEW.ReturnDate IS NOT NULL
            BEGIN
                UPDATE Item SET AvailabilityStatus = 1 WHERE ItemID = NEW.ItemID;
      END;
    );""",
  
  """CREATE TRIGGER IF NOT EXISTS UpdateMemberStatusOnBorrow (
            AFTER INSERT ON BorrowingRecord
            FOR EACH ROW
            BEGIN
                UPDATE Member SET MembershipStatus = 'Active' WHERE MemberID = NEW.MemberID;
            END;
  );""",

  """CREATE TRIGGER IF NOT EXISTS UpdateMemberStatusOnReturn (
            AFTER UPDATE ON BorrowingRecord
            FOR EACH ROW
            WHEN NEW.ReturnDate IS NOT NULL
            BEGIN
                UPDATE Member SET MembershipStatus = 'Inactive' WHERE MemberID = NEW.MemberID;
            END;
    );""",

  
  """CREATE TRIGGER IF NOT EXISTS UpdateLibrarianStatusOnHire(
            AFTER INSERT ON Librarian
            FOR EACH ROW
            BEGIN
                UPDATE Person SET Role = 'Librarian' WHERE PersonID = NEW.LibrarianID;
                UPDATE Librarian SET HireDate = NEW.HireDate;
                "INSERT INTO Person (PersonID, Name, Address, PhoneNumber, Email, Role) VALUES NEW.Librarian;
            END;
    );""",

  """CREATE TRIGGER IF NOT EXISTS UpdateLibrarianStatusOnFired (
            AFTER UPDATE ON Librarian
            FOR EACH ROW
            WHEN NEW.MembershipStatus = 'Fired'
            BEGIN
                UPDATE Person SET Role = 'Librarian' WHERE PersonID = NEW.LibrarianID;
                UPDATE Librarian SET HireDate = NULL;
                "DELETE FROM Person WHERE PersonID = NEW.LibrarianID;
            END;
  );""",
  """CREATE TRIGGER IF NOT EXISTS UpdateEventAttendanceOnRegistration
            AFTER INSERT ON EventRegistration
            FOR EACH ROW
            BEGIN
                UPDATE Event SET Attendance = Event.Attendance + 1 WHERE EventID = NEW.EventID;
            END;
  );""",

  """CREATE TRIGGER IF NOT EXISTS UpdateEventAttendanceOnUnregistration (
            AFTER DELETE ON EventRegistration
            FOR EACH ROW
            BEGIN
                UPDATE Event SET Attendance = Event.Attendance - 1 WHERE EventID = OLD.EventID;
            END;
  );""",

  """CREATE TRIGGER IF NOT EXISTS PreventDuplicateEventRegistration (
            BEFORE INSERT ON EventRegistration
            FOR EACH ROW
            WHEN EXISTS (
              SELECT 1 FROM EveventRegistration WHERE EventID = NEW.EventID AND MemberID = NEW.MemberID)
            BEGIN
              SELECT RAISE(ABORT, 'Member is already registered for this event.');
            END;
  );""",

  """CREATE TRIGGER IF NOT EXISTS SetRequestDate (
            BEFORE INSERT ON HelpRequest
            FOR EACH ROW
            WHEN NEW.RequestDate IS NULL
            BEGIN
                UPDATE HelpRequest SET RequestDate = DATE('now') WHERE RequestID = NEW.RequestID;
            END;
  );""",

  """CREATE TRIGGER IF NOT EXISTS UpdateHelpRequestStatus (
            AFTER INSERT ON HelpRequest
            FOR EACH ROW
            WHEN NEW.Status = 'Resolved'
            BEGIN
                UPDATE HelpRequest SET Status = 'Resolved' WHERE RequestID = NEW.RequestID;
            END;
  );""",

  """CREATE TRIGGER EnforceLibrarianMinSalary (
            BEFORE INSERT ON Librarian
            FOR EACH ROW
            WHEN NEW.Salary < 30000
            BEGIN
                SELECT RAISE(ABORT, 'Librarian salary must be at least 30,000.');
            END;
  );""",
  
  """CREATE TRIGGER SetJoinDate (
            BEFORE INSERT ON Member
            FOR EACH ROW
            WHEN NEW.JoinDate IS NULL
            BEGIN
                UPDATE Member SET JoinDate = DATE('now') WHERE MemberID = NEW.MemberID;
            END;
  );""",
  
  """CREATE TRIGGER SetDueDate (
            BEFORE INSERT ON BorrowingRecord
            FOR EACH ROW
            WHEN NEW.DueDate IS NULL
            BEGIN
                UPDATE BorrowingRecord SET DueDate = DATE('now', '+30 days') WHERE RecordID = NEW.RecordID;
              END;
  );""",
  
    """CREATE TRIGGER IF NOT EXISTS CheckRoomCapacity (
            BEFORE INSERT ON EventRegistraton
            FOR EACH ROW
            WHEN (SELECT Capacity FROM LibraryRoom WHERE RoomID = NEW.RoomID) <= (SELECT Attendance FROM Event WHERE EventID = NEW.EventID)
            BEGIN
                SELECT RAISE(ABORT, 'Event has reached maximum capacity.');
            END;
    );""",
    
    """CREATE TRIGGER IF NOT EXISTS ProcessDonation (
            AFTER INSERT ON Donation
            FOR EACH ROW
            WHEN NEW.ItemID IS NULL
            BEGIN
                Insert INTO Item (Title, Type, AuthorPublisher, AvailabilityStatus, ISBN, PublicationYear)
                VALUES (NEW.ItemTitle, NEW.ItemType, NEW.AuthorPublisher, 1, NEW.ISBN, NEW.PublicationYear);
                UPDATE Donation SET ItemID = (SELECT LAST_INSERT_ROWID() FROM Item) WHERE DonationID = NEW.DonationID;
            END;
      );"""

    
]


def add_item(conn, Item):
    sql = '''INSERT INTO Item (Title, Type, AuthorPublisher, AvailabilityStatus, ISBN, PublicationYear, DueDate, BorrowerID)
    VALUES (?, ?, ?, ?, ?, ?, ?)''' , 
    cur = conn.cursor()
    cur.execute(sql, Item)
    conn.commit()
    return cur.lastrowid


def add_person(conn, Person):
    sql = '''INSERT INTO Person (Name, Address, PhoneNumber, Email, Role) VALUES (?, ?, ?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, Person)
    conn.commit()
    return cur.lastrowid

def add_member(conn, Member):
    sql = '''INSERT INTO Member (MemberID, JoinDate, MembershipStatus) VALUES (?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, Member)
    conn.commit()
    return cur.lastrowid
    

def add_librarian(conn, Librarian):
    sql = '''INSERT INTO Librarian (LibrarianID, HireDate, Salary) VALUES (?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, Librarian)
    conn.commit()


# Library Management Functions
def find_item(conn, search_term):
    sql = '''SELECT * FROM Item WHERE Title LIKE ? OR AuthorPublisher LIKE ?'''
    cur = conn.cursor()
    cur.execute(sql, (f'%{search_term}%', f'%{search_term}%'))
    return cur.fetchall()

def borrow_item(conn, member_id, item_id):
    sql = '''INSERT INTO BorrowingRecord (MemberID, ItemID, DueDate) 
             VALUES (?, ?, date('now', '+30 days'))'''
    cur = conn.cursor()
    cur.execute(sql, (member_id, item_id))
    conn.commit()
    return cur.lastrowid

def return_item(conn, record_id):
    sql = '''UPDATE BorrowingRecord 
             SET ReturnDate = date('now') 
             WHERE RecordID = ?'''
    cur = conn.cursor()
    cur.execute(sql, (record_id,))
    conn.commit()

def donate_item(conn, donor_id, title, item_type, author_publisher=None):
    sql = '''INSERT INTO Donation (DonorID, ItemTitle, ItemType, DateReceived) 
             VALUES (?, ?, ?, date('now'))'''
    cur = conn.cursor()
    cur.execute(sql, (donor_id, title, item_type))
    conn.commit()
    return cur.lastrowid

def find_events(conn, search_term=None):
    sql = '''SELECT * FROM Event 
             WHERE EventName LIKE ? OR EventDate >= date('now')'''
    cur = conn.cursor()
    cur.execute(sql, (f'%{search_term}%',) if search_term else ('%',))
    return cur.fetchall()

def register_for_event(conn, member_id, event_id):
    sql = '''INSERT INTO EventRegistration (EventID, MemberID) VALUES (?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, (event_id, member_id))
    conn.commit()
    return cur.lastrowid

def volunteer_signup(conn, name, email, phone):
    sql = '''INSERT INTO Volunteer (Name, EmailAddress, PhoneNumber) VALUES (?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, (name, email, phone))
    conn.commit()
    return cur.lastrowid

def request_help(conn, member_id, description):
    sql = '''INSERT INTO HelpRequest (MemberID, Description) VALUES (?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, (member_id, description))
    conn.commit()
    return cur.lastrowid

# Sample data population
def populate_sample_data(conn):
    # Sample LibraryRoom data
    rooms = [
        (30, 'Study Room'),
        (100, 'Event Hall'),
        (20, 'Computer Lab'),
        (15, 'Meeting Room'),
        (50, 'Reading Room')
    ]
    
    for room in rooms:
        add_library_room(conn, room)

    # Sample Person/Member data
    persons = [
        ('John Doe', '123 Main St', '555-0101', 'john@email.com', 'Member'),
        ('Jane Smith', '456 Oak Ave', '555-0102', 'jane@email.com', 'Librarian'),
        ('Bob Wilson', '789 Pine Rd', '555-0103', 'bob@email.com', 'Member'),
        ('Alice Brown', '321 Elm St', '555-0104', 'alice@email.com', 'Volunteer')
    ]
    
    for person in persons:
        add_person(conn, person)

    # Sample Items
    items = [
        ('The Great Gatsby', 'Book', 'F. Scott Fitzgerald', 1, '978-0743273565', 1925),
        ('To Kill a Mockingbird', 'Book', 'Harper Lee', 1, '978-0446310789', 1960),
        ('Python Programming', 'Book', 'John Smith', 1, '978-1234567890', 2020),
        ('The Matrix', 'DVD', 'Warner Bros', 1, None, 1999)
    ]
    
    for item in items:
        add_item(conn, item)

    # Sample Events
    events = [
        ('Book Club Meeting', '2024-02-01', 0, 1),
        ('Children Story Time', '2024-02-05', 0, 2),
        ('Programming Workshop', '2024-02-10', 0, 3)
    ]
    
    for event in events:
        add_event(conn, event)

# Populate the database with sample data
try:
    with sqlite3.connect('354_mini_project.db') as conn:
        populate_sample_data(conn)
        print("Sample data inserted successfully.")
except sqlite3.Error as e:
    print("Error inserting sample data:", e)

    return cur.lastrowid

def add_volunteer(conn, Volunteer):
    sql = '''INSERT INTO Volunteer (VolunteerID, Name, EmailAddress, PhoneNumber) VALUES (?, ?, ?, ?'''
    cur = conn.cursor()
    cur.execute(sql, Volunteer)
    conn.commit()    
    return cur.lastrowid

def add_event(conn, Event):
    sql = '''INSERT INTO Event (EventName, EventDate, Attendance, RoomID) VALUES (?, ?, ?, ?)'''
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
    sql = '''INSERT INTO Donation (DonorID, ItemID, ItemTitle, ItemType, DateReceived)'''
    cur = conn.cursor()
    cur.execute(sql, Donation)
    conn.commit()
    return cur.lastrowid

def add_help_request(conn, HelpRequest):
    sql = '''INSERT INTO HelpRequest (MemberID, LibrarianID, RequestDate, Description, Status) VALUES (?, ?, ?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, HelpRequest)
    conn.commit()
    return cur.lastrowid





# create a database connection
try:
    with sqlite3.connect('354_mini_project.db') as conn:
        # create a cursor
        cursor = conn.cursor()

        # execute statements
        for statement in sql_statements:
            cursor.execute(statement)

        # commit the changes
        conn.commit()

        print("Tables created successfully.")
except sqlite3.OperationalError as e:
    print("Failed to create tables:", e)
