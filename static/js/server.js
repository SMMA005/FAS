const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();

// Middlewares
app.use(cors());
app.use(bodyParser.json({ limit: "30mb", extended: true }));
app.use(bodyParser.urlencoded({ limit: "30mb", extended: true }));

// MongoDB connection string, replace <username>, <password>, and <dbname> with your details
const CONNECTION_URL = 'mongodb://admin:admin@localhost:27017/dbface';
const PORT = process.env.PORT || 5000;

mongoose.connect(CONNECTION_URL, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => app.listen(PORT, () => console.log(`Server Running on Port: http://localhost:${PORT}`)))
  .catch((error) => console.log(`${error} did not connect`));

// Prevent deprecation warnings
mongoose.set('useFindAndModify', false);
const Student = require('./models/Student'); // Import the model

// Add Student Route
app.post('/addstudent', (req, res) => {
  const studentData = req.body;
  
  const newStudent = new Student(studentData);
  newStudent.save()
    .then(() => res.status(201).json({ message: "Student added successfully!" }))
    .catch((error) => res.status(409).json({ message: error.message }));
});
