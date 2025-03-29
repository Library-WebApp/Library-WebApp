from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

def get_db_connection():
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
    if request.method == 'POST':
        record_id = request.form['record_id']
        try:
            conn = get_db_connection()
            return_date = datetime.now().strftime('%Y-%m-%d')
            conn.execute('UPDATE BorrowingRecord SET ReturnDate = ? WHERE RecordID = ?',
                            (return_date, record_id))
            conn.commit()
            conn.close()
            return redirect(url_for('return_item', success=True))
        except sqlite3.Error as e:
            return render_template('return_item.html', error=str(e))
    return render_template('return_item.html')

# Donate Item
@app.route('/donate-item', methods=['GET', 'POST'])
def donate_item():
    if request.method == 'POST':
        donor_id = request.form['donor_id']
        item_title = request.form['item_title']
        item_type = request.form['item_type']
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO Donation (DonorID, ItemTitle, ItemType, DateReceived) '
                         'VALUES (?, ?, ?, ?)',
                        (donor_id, item_title, item_type, datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            conn.close()
            return redirect(url_for('donate_item', success=True))
        except sqlite3.Error as e:
            return render_template('donate_item.html', error=str(e))
    return render_template('donate_item.html')

# Find Events
@app.route('/find-events', methods=['GET', 'POST'])
def find_events():
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM Event').fetchall()
    conn.close()
    return render_template('find_events.html', events=events)

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
    if request.method == 'POST':
        member_id = request.form['member_id']
        description = request.form['description']
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO HelpRequest (MemberID, Description) VALUES (?, ?)',
                         (member_id, description))
            conn.commit()
            conn.close()
            return redirect(url_for('ask_help', success=True))
        except sqlite3.Error as e:
            return render_template('ask_help.html', error=str(e))
    return render_template('ask_help.html')

if __name__ == '__main__':
    app.run(debug=True)