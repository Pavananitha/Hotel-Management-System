# Hotel-Management-System
# Hotel Management System (Python + MySQL)

This is a desktop-based Hotel Management System developed using **Python (Tkinter)** for GUI and **MySQL** for the backend. It offers modules for managing guests, room reservations, event halls, restaurant services, drivers, employees, feedback, and payments.

## 📁 Project Structure

PYTHON PROGRAMMING/
│
├── Guest Management
│ ├── GuestManagement.py
│ ├── guestinfo.py
│
├── Room Management
│ ├── roommanagement.py
│ ├── roomreservation.py
│ ├── roomdetails.py
│ ├── reservation.py
│ ├── checkout.py
│
├── Event Hall Booking
│ ├── eventhallbooking.py
│ ├── eventhalldetails.py
│ ├── eventhallmanagement.py
│ ├── eventbookingdetails.py
│
├── Restaurant & Food Services
│ ├── foodmenu.py
│ ├── orderfood.py
│ ├── restaurantmanager.py
│ ├── menumanagement.py
│
├── Employee Management
│ ├── employeesinfo.py
│ ├── employeemanagement.py
│
├── Driver & Parking
│ ├── driversinfo.py
│ ├── drivermanagement.py
│ ├── parkingbooking.py
│
├── Payments & Feedback
│ ├── payments.py
│ ├── feedback.py
│
├── Core
│ ├── Dashboard.py
│ ├── homepage.py
│ ├── view.py
│ ├── view1.py
│ ├── conn.py # Handles MySQL connections
│ ├── cursor.py
│
└── others (.DS_Store, metadata files)


## 💡 Features

- Guest check-in/check-out and info management
- Room booking with dynamic availability and date selection
- Event hall booking and management
- Restaurant menu, food ordering, and billing
- Driver and parking management
- Payment processing and feedback collection
- Employee details and position management
- Dashboard interface for easy navigation

## 🛠️ Requirements

- Python 3.x
- Tkinter (usually included with Python)
- MySQL Server (e.g., XAMPP, WAMP, or standalone)
- `mysql-connector-python` package

Install the connector with:

```bash
pip install mysql-connector-python

🧩 Setup Instructions

Import the provided SQL database (not included here) into your MySQL server.
Update database credentials in conn.py:
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="your_username",
        password="your_password",
        database="your_database_name"
    )
Run homepage.py or Dashboard.py to launch the application.
python homepage.py

📌 Note

Each module is developed using Tkinter frames and follows modular practices.
Use the sliding sidebar in the dashboard to navigate between sections.
The GUI is designed for desktop environments.
📄 License

This project is for educational purposes.

