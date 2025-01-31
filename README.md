# **LabSync - A Lab Management System**

LabSync is an **efficient** lab management system designed to **streamline the management of laboratory resources**,
including **equipment, chemicals, consumables, and bookings**.

With **role-based access control (RBAC)**, LabSync ensures that every user—**Admin, Technician, Researcher, and Standard
User**—has **tailored access to the system**, maintaining **security, accountability, and operational efficiency**.

🚀 **Live Deployment**: [LabSync on Render](https://labsync-rd2f.onrender.com)


## **📌 Table of Contents**

1. [Installation Guide](#installation-guide)
2. [Usage Guide](#usage-guide)
3. [Features](#features)
4. [Project Structure](#project-structure)
5. [Technology Stack](#technology-stack)
6. [Deployment Guide](#deployment-guide)


## **Installation Guide**

### **1️⃣ Install Dependencies**

Run the following command to install all necessary dependencies:

```bash
pip install -r requirements.txt
```

### **2️⃣ Running the Application**

```bash
flask run --host=0.0.0.0 --port=10000
```

Then, navigate to **[`http://localhost:10000/`](http://localhost:10000/)** in your web browser.

## **Usage Guide**

### **1️⃣ Logging In**

To access LabSync, go to **[`http://localhost:10000/`](http://localhost:10000/)** and log in with one of the default
credentials:

| Role           | Default Username | Default Password |
|---------------|------------------|------------------|
| **Admin**      | `admin`          | `admin`          |
| **Technician** | `technician`     | `technician`     |
| **Researcher** | `researcher`     | `researcher`     |
| **User**       | `user`           | `user`           |

### **2️⃣ Account Registration & Approval**

🚨 **Important Note:**

- New users can register for an account, but if they choose **a role other than "User" (e.g., Technician, Researcher,
  Admin)**, their account **must be approved by an Admin** before they can log in.


## **Features**

### **1️⃣ Booking System**

- **Smart Filtering**: Search available rooms based on lab zone, equipment type, date, and time.
- **Conflict-Free Reservations**: Users cannot make overlapping bookings.
- **Flexible Cancellations**: Users can cancel only future bookings.

### **2️⃣ Task Management**

- **Assign Tasks**: Any user can assign tasks to others.
- **Filtering Options**: Filter tasks by type and priority.
- **Role-Specific Actions**:
    - **Task Creator**: Can delete the task.
    - **Task Assignee**: Can accept and complete the task.
- **Overdue Task Alerts**: A warning banner appears at the top.

### **3️⃣ Calendar Integration**

- **Multi-View Support**: Monthly and weekly views available.
- **Event Breakdown**: View all bookings and assigned tasks at a glance.

### **4️⃣ User Profile Management**

- **View Personal & Other User Details**: Users can view their own and others' profiles.

### **5️⃣ Inventory Management (Technician Only)**

- **Update Stock Levels**: Add, remove, or update stock levels for equipment, chemicals, and consumables.
- **Automated Restocking Alerts** when stock falls below reorder levels.

### **6️⃣ Verification System (Admin Only)**

- **Approval Process**: Admins must approve non-user accounts before activation.
- **User Management**: Admins can monitor and manage registered users.

## **Project Structure**

LabSync follows a **modular and organized project structure**, making it easy to **extend, debug, and maintain**.

```bash
SWE-P1/                    # Project Root
│── app/                   # Main Application Code
│   ├── services/          # Business logic & backend services
│   ├── static/            # Static assets (CSS, JS, Images)
│   │   ├── css/           # Stylesheets
│   │   ├── images/        # Static images/icons
│   │   ├── js/            # JavaScript files
│   ├── templates/         # HTML templates for UI rendering
│   ├── __init__.py        # App initialization & configuration
│   ├── routes.py          # API routes & request handling
│
│── sql/                   # Database & SQL-related files
│   ├── logic/             # SQL query functions & logic
│   ├── sample-data/       # Sample datasets for testing
│   ├── schema/            # Database schema & migrations
│
│── .env                   # Environment variables for configuration
│── Dockerfile             # Docker configuration
│── docker-compose.yml     # Docker Compose configuration
│── requirements.txt       # Python dependencies
│── README.md              # Documentation
```

## **Technology Stack**

LabSync is built using **modern technologies** to ensure **scalability, performance, and maintainability**.

| **Category**        | **Technology Used**                           | **Description** |
|---------------------|----------------------------------------------|----------------|
| **Backend**        | [Flask](https://flask.palletsprojects.com/)   | Lightweight Python web framework. |
| **Frontend**       | [HTML5](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5) | Structure and UI components. |
|                   | [CSS3](https://developer.mozilla.org/en-US/docs/Web/CSS) | Styling for responsiveness and UI design. |
|                   | [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript) | Dynamic interactions and event handling. |
|                   | [Bootstrap](https://getbootstrap.com/) | Enhances UI/UX with responsive components. |
| **Database**      | [PostgreSQL](https://www.postgresql.org/) | Relational database for structured data storage. |
| **Authentication** | Flask-Login & Flask-SQLAlchemy | Secure user authentication and database ORM. |
| **Deployment**    | [Render](https://render.com/) | **Cloud-based hosting platform** for automatic deployments. |
