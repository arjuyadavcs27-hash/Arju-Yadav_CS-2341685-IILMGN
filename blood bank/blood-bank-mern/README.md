# Blood Bank Management System (MERN Stack)

A full-stack blood bank management system built with MongoDB, Express.js, React.js, and Node.js.

## Features

- User authentication for donors and blood banks
- Search for blood banks and donors by location and blood group
- Donor registration and profile management
- Blood bank registration and inventory management
- Real-time blood availability tracking
- Responsive and modern UI

## Prerequisites

- Node.js (v14 or higher)
- MongoDB
- npm or yarn

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd blood-bank-mern
```

2. Install server dependencies:
```bash
cd server
npm install
```

3. Install client dependencies:
```bash
cd ../client
npm install
```

4. Create a `.env` file in the server directory:
```env
MONGODB_URI=mongodb://localhost:27017/blood-bank
JWT_SECRET=your_jwt_secret
PORT=5000
```

5. Start the server:
```bash
cd server
npm run dev
```

6. Start the client:
```bash
cd client
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

## Project Structure

```
blood-bank-mern/
├── client/                 # React frontend
│   ├── public/            # Static files
│   └── src/               # React source code
│       ├── components/    # Reusable components
│       ├── pages/         # Page components
│       └── App.js         # Main App component
└── server/                # Node.js backend
    ├── models/            # MongoDB models
    ├── routes/            # API routes
    ├── middleware/        # Custom middleware
    └── server.js          # Server entry point
```

## API Endpoints

### Donors
- `GET /api/donors` - Get all donors
- `GET /api/donors/:id` - Get single donor
- `POST /api/donors/register` - Register new donor
- `PATCH /api/donors/:id` - Update donor
- `DELETE /api/donors/:id` - Delete donor

### Blood Banks
- `GET /api/blood-banks` - Get all blood banks
- `GET /api/blood-banks/:id` - Get single blood bank
- `POST /api/blood-banks/register` - Register new blood bank
- `PATCH /api/blood-banks/:id` - Update blood bank
- `PATCH /api/blood-banks/:id/inventory` - Update inventory
- `DELETE /api/blood-banks/:id` - Delete blood bank

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 