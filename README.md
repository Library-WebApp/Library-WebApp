# Community Library Management System

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.1.0%2B-green)
![SQLite](https://img.shields.io/badge/SQLite-3.0-lightgrey)
![Database Design](https://img.shields.io/badge/Database-BCNF_Compliant-brightgreen)

A comprehensive Flask-based web application for managing community library operations with complete database normalization and full CRUD functionality.

## Live Demo
Access the live application: [https://librarydatabase.pythonanywhere.com/](https://librarydatabase.pythonanywhere.com/)

## Features

- **Inventory Management**:
  - Search, borrow, and return library items (books, DVDs, magazines)
  - Donation tracking system
  - Real-time availability status
- **Event Management**:
  - Event registration with capacity control
  - Attendance tracking
  - Room allocation
- **User Management**:
  - Member, librarian, and volunteer roles
  - Membership status tracking
- **Support System**:
  - Help request ticketing
  - Request status tracking

## Database Schema (BCNF Compliant)

### Entity Specifications
1. **Item** (Books, magazines, CDs)
   - ItemID (PK), Title, Type, Author/Publisher, AvailabilityStatus, ISBN, PublicationYear
2. **Person** (All library users)
   - PersonID (PK), Name, Address, PhoneNumber, Email, Role
3. **Member** (Person specialization)
   - MemberID (PK/FK), JoinDate, MembershipStatus
4. **Librarian** (Person specialization)
   - LibrarianID (PK/FK), HireDate, Salary
5. **Volunteer** (Person specialization)
   - VolunteerID (PK/FK), JoinDate, MembershipStatus
6. **Event**
   - EventID (PK), EventName, EventDate, Attendance, MaxCapacity, RoomID (FK)
7. **LibraryRoom**
   - RoomID (PK), Capacity, RoomType
8. **BorrowingRecord**
   - RecordID (PK), MemberID (FK), ItemID (FK), DueDate, BorrowDate, ReturnDate, FineAmount
9. **EventRegistration**
   - RegistrationID (PK), EventID (FK), MemberID (FK)
10. **Donation**
    - DonationID (PK), DonorID (FK), ItemID (FK), DateReceived
11. **HelpRequest**
    - RequestID (PK), MemberID (FK), LibrarianID (FK), RequestDate, Description, Status

### Normalization Analysis
All tables satisfy Boyce-Codd Normal Form (BCNF) with:
- No partial dependencies
- No transitive dependencies
- All attributes functionally dependent on primary keys
- Comprehensive foreign key relationships

## Technical Architecture

### Backend
- **Flask** web framework with RESTful routing
- **SQLite** database with:
  - 11 normalized tables
  - 5 automated triggers for business logic
  - Complex constraints and relationships
- Transaction management for data integrity

### Frontend
- Dynamic templating with **Jinja2**
- Form validation and error handling
- Responsive interface for all operations

### Key Features
- Role-based access control
- Automated availability updates
- Event capacity enforcement
- Fine calculation system

## Key Skills Demonstrated

### Database Engineering
- Designed and implemented fully normalized schema (BCNF)
- Created complex entity relationships with proper constraints
- Implemented SQL triggers for business logic enforcement
- Developed comprehensive data validation

### Full-Stack Development
- Built complete web application with Python/Flask backend
- Designed intuitive user interfaces
- Implemented secure authentication workflows
- Created comprehensive error handling

### System Design
- Entity Relationship Modeling
- Business logic implementation
- User workflow automation
- Performance optimization

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Library-WebApp/Library-WebApp.git
   cd Library-WebApp
   ```
2. Run the application:
   ```bash
   python app.py
   ```
3. Access the application at `http://localhost:5001`

## Usage Examples

### Librarian Functions
- Process item checkouts/returns
- Manage event registrations
- Respond to help requests
- Generate reports

### Member Functions
- Search and borrow items
- Register for events
- Submit help tickets
- View borrowing history

### Volunteer Functions
- Register availability
- View assigned tasks
- Update membership status

## Project Documentation

### ER Diagrams
![ER Diagram](https://github.com/Library-WebApp/Library-WebApp/blob/main/LibraryDatabaseERDiagram.png)

### Database Triggers
1. `ItemAvailabilityTrigger`: Ensures items are available before borrowing
2. `UpdateItemStatusOnBorrow`: Updates availability after checkout
3. `UpdateItemStatusOnReturn`: Updates availability after return
4. `UpdateMemberStatusOnBorrow`: Updates member status when borrowing
5. `UpdateMemberStatusOnReturn`: Updates member status when returning

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for any enhancements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
