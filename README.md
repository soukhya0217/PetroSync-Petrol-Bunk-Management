# PetroSync – Petrol Bunk Management System

PetroSync is a web-based Petrol Bunk Management System developed using Flask, SQLite, HTML, CSS, and JavaScript. It helps manage fuel stock, sales, employees, reports, and billing in a simple and organized way.

## Features

* Admin and manager login
* Dashboard with fuel stock and sales summary
* Fuel stock management
* Petrol and diesel sales entry
* Automatic bill generation
* Employee management
* Sales reports with charts
* Low stock alerts
* Dark and light mode
* Responsive user interface

## Technologies Used

* Python
* Flask
* SQLite
* HTML
* CSS
* JavaScript
* Chart.js

## Project Structure

```bash
petrol_bunk/
│
├── app.py
├── database.db
├── requirements.txt
├── run.sh
├── start.bat
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── stock.html
│   ├── sales.html
│   ├── employees.html
│   └── reports.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Installation and Setup

1. Clone the repository

```bash
git clone https://github.com/your-username/petrosync.git
```

2. Open the project folder

```bash
cd petrosync/petrol_bunk
```

3. Install required packages

```bash
pip install -r requirements.txt
```

4. Run the application

```bash
python app.py
```

5. Open in browser

```bash
http://127.0.0.1:5000
```

## Login Credentials

### Admin Login

```bash
Username: admin
Password: admin123
```

### Manager Login

```bash
Username: manager
Password: manager123
```

## Main Modules

### 1. Dashboard

Displays total fuel stock, recent sales, alerts, and quick overview.

### 2. Fuel Stock Management

Allows the user to view and update petrol and diesel stock.

### 3. Sales Management

Records fuel sales, vehicle number, quantity, price, and total amount.

### 4. Employee Management

Admin can add, update, and delete employee details.

### 5. Reports

Shows daily, weekly, and monthly sales reports with charts.

### 6. Billing

Generates a bill after recording fuel sales.

## Database Tables

* users
* fuel_stock
* sales
* employees

## Purpose of the Project

The purpose of this project is to reduce manual work in petrol bunk operations and maintain records digitally. It improves accuracy in stock handling, sales tracking, employee management, and report generation.

## Future Enhancements

* Online payment integration
* Customer management
* SMS or email bill sending
* Advanced analytics
* Mobile application support

## Author

Soukhya Hegde

## License

This project is created for academic and learning purposes.
