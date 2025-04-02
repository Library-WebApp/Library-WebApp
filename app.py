from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

def get_db_connection():
    print("Connecting to database...")
    conn = sqlite3.connect('354_mini_project.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('base.html')

# Find Item
@app.route('/find-item', methods=['GET', 'POST'])
def find_item():
    conn = get_db_connection()
    if request.method == 'POST':
        search_term = request.form['search_term']
        items = conn.execute(
            "SELECT * FROM Item WHERE Title LIKE ? OR AuthorPublisher LIKE ?",
            (f'%{search_term}%', f'%{search_term}%')
        ).fetchall()
    else:
        # Get all items when it's a GET request
        items = conn.execute("SELECT * FROM Item").fetchall()
    conn.close()
    return render_template('find_item.html', items=items)

# Borrow Item
@app.route('/borrow-item', methods=['GET', 'POST'])
def borrow_item():
    conn = get_db_connection()

    # Get all items and members for display
    items = conn.execute("SELECT * FROM Item").fetchall()
    members = conn.execute("""
        SELECT p.PersonID, p.Name 
        FROM Person p
        JOIN Member m ON p.PersonID = m.MemberID
        WHERE p.Role = 'Member'
    """).fetchall()

    if request.method == 'POST':
        member_id = request.form['member_id']
        item_id = request.form['item_id']
        try:
            # Check if item is available
            item = conn.execute("SELECT AvailabilityStatus FROM Item WHERE ItemID = ?", (item_id,)).fetchone()
            if not item or not item['AvailabilityStatus']:
                return render_template('borrow_item.html', 
                                      items=items, 
                                      members=members,
                                      error="Item is not available for borrowing")

            borrow_date = datetime.now().strftime('%Y-%m-%d')
            due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

            # Create borrowing record
            conn.execute('INSERT INTO BorrowingRecord (MemberID, ItemID, DueDate, BorrowDate) '
                        'VALUES (?, ?, ?, ?)',
                        (member_id, item_id, due_date, borrow_date))

            # Update item availability
            conn.execute('UPDATE Item SET AvailabilityStatus = 0 WHERE ItemID = ?', (item_id,))

            conn.commit()
            conn.close()
            return redirect(url_for('borrow_item', success=True))
        except sqlite3.Error as e:
            return render_template('borrow_item.html', 
                                 items=items, 
                                 members=members,
                                 error=str(e))

    conn.close()
    return render_template('borrow_item.html', items=items, members=members)

# Return Item
@app.route('/return-item', methods=['GET', 'POST'])
def return_item():
    conn = get_db_connection()

    # Get all members for display
    members = conn.execute("""
        SELECT p.PersonID, p.Name 
        FROM Person p
        JOIN Member m ON p.PersonID = m.MemberID
        WHERE p.Role = 'Member'
    """).fetchall()

    if request.method == 'POST':
        # Handle member selection or item return
        if 'member_id' in request.form:
            # Member selected - show their borrowed items
            member_id = request.form['member_id']
            borrowed_items = conn.execute("""
                SELECT br.RecordID, i.Title, i.ItemID, br.BorrowDate, br.DueDate
                FROM BorrowingRecord br
                JOIN Item i ON br.ItemID = i.ItemID
                WHERE br.MemberID = ? AND br.ReturnDate IS NULL
            """, (member_id,)).fetchall()

            return render_template('return_item.html', 
                                 members=members,
                                 borrowed_items=borrowed_items,
                                 selected_member=member_id)

        elif 'record_id' in request.form:
            # Item return submitted
            record_id = request.form['record_id']
            try:
                return_date = datetime.now().strftime('%Y-%m-%d')

                # Get item ID from the borrowing record
                record = conn.execute("""
                    SELECT ItemID FROM BorrowingRecord WHERE RecordID = ?
                """, (record_id,)).fetchone()

                if record:
                    # Update borrowing record
                    conn.execute("""
                        UPDATE BorrowingRecord 
                        SET ReturnDate = ? 
                        WHERE RecordID = ?
                    """, (return_date, record_id))

                    # Update item availability
                    conn.execute("""
                        UPDATE Item 
                        SET AvailabilityStatus = 1 
                        WHERE ItemID = ?
                    """, (record['ItemID'],))

                    conn.commit()

                # Get member ID to show their remaining borrowed items
                member_record = conn.execute("""
                    SELECT MemberID FROM BorrowingRecord WHERE RecordID = ?
                """, (record_id,)).fetchone()

                if member_record:
                    borrowed_items = conn.execute("""
                        SELECT br.RecordID, i.Title, i.ItemID, br.BorrowDate, br.DueDate
                        FROM BorrowingRecord br
                        JOIN Item i ON br.ItemID = i.ItemID
                        WHERE br.MemberID = ? AND br.ReturnDate IS NULL
                    """, (member_record['MemberID'],)).fetchall()

                conn.close()
                return render_template('return_item.html',
                                    members=members,
                                    borrowed_items=borrowed_items,
                                    selected_member=member_record['MemberID'],
                                    success="Item returned successfully!")
            except sqlite3.Error as e:
                return render_template('return_item.html', 
                                    members=members,
                                    error=str(e))

    conn.close()
    return render_template('return_item.html', members=members)

# Donate Item
@app.route('/donate-item', methods=['GET', 'POST'])
def donate_item():
    conn = get_db_connection()

    # Get all potential donors (people who aren't necessarily members)
    donors = conn.execute("""
        SELECT PersonID, Name FROM Person
            WHERE Role IN ('Member', 'Volunteer', 'Donor')
            ORDER BY Name
        """).fetchall()

    if request.method == 'POST':
        # Check if the donor selection form was submitted
        if 'donor_id' in request.form and 'item_title' not in request.form:
            # Donor selected, render the donation form
            selected_donor = request.form['donor_id']
            selected_donor_name = next((donor['Name'] for donor in donors if str(donor['PersonID']) == selected_donor), "Unknown")
            return render_template('donate_item.html', donors=donors, selected_donor=selected_donor, selected_donor_name=selected_donor_name)

        # Handle the donation form submission
        donor_id = request.form['donor_id']
        item_title = request.form['item_title']
        item_type = request.form['item_type']
        author_publisher = request.form.get('author_publisher', None)
        isbn = request.form.get('isbn', None)
        publication_year = request.form.get('publication_year', None)
        date_received = request.form.get('date_received', datetime.now().strftime('%Y-%m-%d'))

        # Validate publication year
        if publication_year:
            try:
                publication_year = int(publication_year)
                if publication_year < 1000 or publication_year > datetime.now().year:
                    raise ValueError("Invalid publication year")
            except ValueError:
                return render_template('donate_item.html', donors=donors, selected_donor=donor_id, error="Invalid publication year")

        try:
            # First add the item to the Item table
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Item (Title, Type, AuthorPublisher, ISBN, PublicationYear, AvailabilityStatus)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (item_title, item_type, author_publisher, isbn, publication_year))
            item_id = cur.lastrowid

            # Then record the donation
            cur.execute("""
                INSERT INTO Donation (DonorID, ItemID, DateReceived)
                    VALUES (?, ?, ?)
                """, (donor_id, item_id, date_received))

            conn.commit()
            conn.close()
            return redirect(url_for('donate_item', success=True))
        except sqlite3.Error as e:
            return render_template('donate_item.html', donors=donors, selected_donor=donor_id, error=str(e))

    conn.close()
    return render_template('donate_item.html', donors=donors)

#Find Event
@app.route('/find-events', methods=['GET', 'POST'])
def find_events():
    conn = get_db_connection()

    # Get all members for selection
    members = conn.execute("""
        SELECT p.PersonID, p.Name 
        FROM Person p
        JOIN Member m ON p.PersonID = m.MemberID
        WHERE p.Role = 'Member'
        ORDER BY p.Name
    """).fetchall()

    if request.method == 'POST':
        member_id = request.form.get('member_id')
        search_term = request.form.get('search_term', '')
        action = request.form.get('action')

        if member_id:
            # Build query based on search term
            query = """
                SELECT e.*, 
                       EXISTS(SELECT 1 FROM EventRegistration er 
                              WHERE er.EventID = e.EventID AND er.MemberID = ?) AS IsRegistered
                FROM Event e
                WHERE e.EventName LIKE ? OR e.EventDate LIKE ?
                ORDER BY e.EventDate
            """
            events = conn.execute(query, 
                                (member_id, 
                                 f'%{search_term}%', 
                                 f'%{search_term}%')).fetchall()

            # Handle registration/unregistration
            if 'event_id' in request.form:
                event_id = request.form['event_id']
                try:
                    if action == 'register':
                        # Check if already registered
                        existing_reg = conn.execute("""
                            SELECT 1 FROM EventRegistration 
                            WHERE EventID = ? AND MemberID = ?
                        """, (event_id, member_id)).fetchone()

                        if not existing_reg:
                            # Register for event
                            conn.execute("""
                                INSERT INTO EventRegistration (EventID, MemberID)
                                VALUES (?, ?)
                            """, (event_id, member_id))

                            # Update attendance count
                            conn.execute("""
                                UPDATE Event 
                                SET Attendance = Attendance + 1 
                                WHERE EventID = ?
                            """, (event_id,))

                            conn.commit()

                            # Refresh events list
                            events = conn.execute(query, 
                                                (member_id, 
                                                 f'%{search_term}%', 
                                                 f'%{search_term}%')).fetchall()

                            return render_template('find_events.html',
                                                members=members,
                                                events=events,
                                                selected_member=member_id,
                                                search_term=search_term,
                                                success="Successfully registered for event!")

                    elif action == 'unregister':
                        # Check if registered
                        existing_reg = conn.execute("""
                            SELECT 1 FROM EventRegistration 
                            WHERE EventID = ? AND MemberID = ?
                        """, (event_id, member_id)).fetchone()

                        if existing_reg:
                            # Unregister from event
                            conn.execute("""
                                DELETE FROM EventRegistration
                                WHERE EventID = ? AND MemberID = ?
                            """, (event_id, member_id))

                            # Update attendance count
                            conn.execute("""
                                UPDATE Event 
                                SET Attendance = Attendance - 1 
                                WHERE EventID = ?
                            """, (event_id,))

                            conn.commit()

                            # Refresh events list
                            events = conn.execute(query, 
                                                (member_id, 
                                                 f'%{search_term}%', 
                                                 f'%{search_term}%')).fetchall()

                            return render_template('find_events.html',
                                                members=members,
                                                events=events,
                                                selected_member=member_id,
                                                search_term=search_term,
                                                success="Successfully unregistered from event!")

                except sqlite3.Error as e:
                    return render_template('find_events.html',
                                        members=members,
                                        selected_member=member_id,
                                        search_term=search_term,
                                        error=str(e))

            return render_template('find_events.html', 
                                members=members,
                                events=events,
                                selected_member=member_id,
                                search_term=search_term)

    # Default GET request - show all events
    events = conn.execute("SELECT * FROM Event ORDER BY EventDate").fetchall()
    conn.close()
    return render_template('find_events.html', members=members, events=events)
    
# Register for Event
@app.route('/register-event', methods=['GET', 'POST'])
def register_event():
    if request.method == 'POST':
        event_id = request.form['event_id']
        member_id = request.form['member_id']
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO EventRegistration (EventID, MemberID) VALUES (?, ?)',
                         (event_id, member_id))
            conn.commit()
            conn.close()
            return redirect(url_for('register_event', success=True))
        except sqlite3.Error as e:
            return render_template('register_event.html', error=str(e))
    return render_template('register_event.html')

# Volunteer
@app.route('/volunteer', methods=['GET', 'POST'])
def volunteer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('INSERT INTO Person (Name, Email, PhoneNumber, Role) VALUES (?, ?, ?, "Volunteer")',
                        (name, email, phone))
            person_id = cur.lastrowid
            cur.execute('INSERT INTO Volunteer (VolunteerID, JoinDate, MembershipStatus) VALUES (?, ?, ?)',
                        (person_id, datetime.now().strftime('%Y-%m-%d'), 'Pending'))
            conn.commit()
            conn.close()
            return redirect(url_for('volunteer', success=True))
        except sqlite3.Error as e:
            return render_template('volunteer.html', error=str(e))
    return render_template('volunteer.html')

# Ask for Help
@app.route('/ask-help', methods=['GET', 'POST'])
def ask_help():
    conn = get_db_connection()

    # Get all members for selection
    members = conn.execute("""
        SELECT p.PersonID, p.Name 
        FROM Person p
        JOIN Member m ON p.PersonID = m.MemberID
        WHERE p.Role = 'Member'
        ORDER BY p.Name
    """).fetchall()

    if request.method == 'POST':
        member_id = request.form.get('member_id')
        description = request.form.get('description')

        try:
            if member_id and not description:
                # Just member selected - show their previous requests
                previous_requests = conn.execute("""
                    SELECT h.RequestID, h.Description, h.RequestDate, p.Name
                    FROM HelpRequest h
                    JOIN Person p ON h.MemberID = p.PersonID
                    WHERE h.MemberID = ?
                    ORDER BY h.RequestDate DESC
                """, (member_id,)).fetchall()

                return render_template('ask_help.html',
                                    members=members,
                                    selected_member=member_id,
                                    previous_requests=previous_requests)

            elif member_id and description:
                # New request submitted
                conn.execute("""
                    INSERT INTO HelpRequest (MemberID, Description, RequestDate)
                    VALUES (?, ?, ?)
                """, (member_id, description, datetime.now().strftime('%Y-%m-%d')))

                conn.commit()

                # Get updated request list
                previous_requests = conn.execute("""
                    SELECT h.RequestID, h.Description, h.RequestDate, p.Name
                    FROM HelpRequest h
                    JOIN Person p ON h.MemberID = p.PersonID
                    WHERE h.MemberID = ?
                    ORDER BY h.RequestDate DESC
                """, (member_id,)).fetchall()

                return render_template('ask_help.html',
                                    members=members,
                                    selected_member=member_id,
                                    previous_requests=previous_requests,
                                    success="Your request has been submitted!")

        except sqlite3.Error as e:
            return render_template('ask_help.html',
                                members=members,
                                error=str(e))

    conn.close()
    return render_template('ask_help.html', members=members)

if __name__ == '__main__':
    app.run(debug=True, port=5001)