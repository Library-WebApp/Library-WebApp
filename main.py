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
            Role TEXT NOT NULL, 
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
            FOREIGN KEY (LibrarianID) REFERENCES Person(PersonID))
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
    );"""

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
  );"""
  """CREATE TRIGGER IF NOT EXISTS UpdateEventAttendanceOnRegistration
            AFTER INSERT ON EventRegistration
            FOR EACH ROW
            BEGIN
                UPDATE Event SET Attendance = Event.Attendance + 1 WHERE EventID = NEW.EventID;
            END;
  );"""

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
