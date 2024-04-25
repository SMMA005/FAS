const mongoose = require('mongoose');

const studentSchema = mongoose.Schema({
  studentNumber: String,
  surname: String,
  otherNames: String,
  mobileNo: String,
  address: String,
  course: String,
  dateEnrolled: Date,
  image: String // This will store the base64 encoded image
});

const Student = mongoose.model('Student', studentSchema);

module.exports = Student;
