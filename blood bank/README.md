# Blood Bank Management System

A comprehensive blood bank management system built with Flask.

## Features

- User Authentication (Admin, Donor, Hospital)
- Donor Management
- Hospital Management
- Blood Request System
- Donation Tracking
- Real-time Notifications
- Admin Dashboard
- Donor Dashboard
- Hospital Dashboard

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd blood-bank
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

5. Run the application:
```bash
python app.py
```

6. Access the application at `http://localhost:5000`

## File Structure

```
blood-bank/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── 01_landing.html
│   ├── 02_login.html
│   ├── 03_register.html
│   ├── 04_blood-request.html
│   ├── 05_donor-dashboard.html
│   ├── 06_hospital-dashboard.html
│   └── 07_admin-dashboard.html
├── static/               # Static files
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
└── models/              # Database models
    └── models.py
```

## Usage

1. Register as an admin, donor, or hospital
2. Login with your credentials
3. Access your respective dashboard
4. Perform actions based on your role:
   - Admin: Manage users, view requests, generate reports
   - Donor: Update profile, view donation history, schedule appointments
   - Hospital: Request blood, view request history, manage inventory

## Security Features

- Password hashing
- Session management
- Role-based access control
- CSRF protection
- Input validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@lifeflow.in or create an issue in the GitHub repository.

## Acknowledgments

- Indian Red Cross Society
- National Blood Transfusion Council
- Ministry of Health and Family Welfare, Government of India 