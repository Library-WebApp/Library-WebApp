from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Database connection helper function
def get_db_connection():
    conn = sqlite3.connect('354_mini_project.db')
    conn.row_factory = sqlite3.Row
    return conn

# Routes for library functions

@app.route('/find_item', methods=['GET'])
def find_item():
    title = request.args.get('title')
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM Item WHERE Title LIKE ? OR AuthorPublisher LIKE ?', 
                         (f'%{title}%', f'%{title}%')).fetchall()
    conn.close()
    return jsonify([dict(item) for item in items])

@app.route('/borrow_item', methods=['POST'])
def borrow_item():
    data = request.json
    member_id = data['member_id']
    item_id = data['item_id']
    conn = get_db_connection()
    due_date = datetime.now() + timedelta(days=30)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO BorrowingRecord (MemberID, ItemID, DueDate) VALUES (?, ?, ?)', 
                   (member_id, item_id, due_date.strftime('%Y-%m-%d')))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'message': 'Item borrowed successfully', 'record_id': record_id})

@app.route('/return_item', methods=['POST'])
def return_item():
    data = request.json
    record_id = data['record_id']
    conn = get_db_connection()
    conn.execute('UPDATE BorrowingRecord SET ReturnDate = date("now") WHERE RecordID = ?', (record_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Item returned successfully'})

@app.route('/donate_item', methods=['POST'])
def donate_item():
    data = request.json
    donor_id = data['donor_id']
    title = data['title']
    item_type = data['item_type']
    author_publisher = data['author_publisher']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Donation (DonorID, ItemTitle, ItemType, AuthorPublisher, DateReceived) VALUES (?, ?, ?, ?, date("now"))',
                   (donor_id, title, item_type, author_publisher))
    donation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'message': 'Item donated successfully', 'donation_id': donation_id})

@app.route('/find_events', methods=['GET'])
def find_events():
    search_term = request.args.get('search_term')
    conn = get_db_connection()
    if search_term:
        events = conn.execute('SELECT * FROM Event WHERE EventName LIKE ? OR EventDate >= date("now")',
                              (f'%{search_term}%',)).fetchall()
    else:
        events = conn.execute('SELECT * FROM Event WHERE EventDate >= date("now")').fetchall()
    conn.close()
    return jsonify([dict(event) for event in events])

@app.route('/register_for_event', methods=['POST'])
def register_for_event():
    data = request.json
    member_id = data['member_id']
    event_id = data['event_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO EventRegistration (EventID, MemberID) VALUES (?, ?)', (event_id, member_id))
    registration_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'message': 'Registered for event successfully', 'registration_id': registration_id})

@app.route('/volunteer_signup', methods=['POST'])
def volunteer_signup():
    data = request.json
    name = data['name']
    email = data['email']
    phone = data['phone']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Volunteer (Name, EmailAddress, PhoneNumber) VALUES (?, ?, ?)', (name, email, phone))
    volunteer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'message': 'Volunteer signup successful', 'volunteer_id': volunteer_id})

@app.route('/request_help', methods=['POST'])
def request_help():
    data = request.json
    member_id = data['member_id']
    description = data['description']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO HelpRequest (MemberID, Description) VALUES (?, ?)', (member_id, description))
    request_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'message': 'Help request submittsed successfully', 'request_id': request_id})

if __name__ == '__main__':
    app.run(debug=True)

