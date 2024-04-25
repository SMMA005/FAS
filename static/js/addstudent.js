// Get access to the camera!
if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream) {
        // Link to the video source (webcam)
        var video = document.getElementById('video');
        video.srcObject = stream;
        video.play();
    });
}

// Elements for taking the snap
var canvas = document.getElementById('canvas');
var context = canvas.getContext('2d');
var video = document.getElementById('video');

// Trigger photo take
document.getElementById("snap").addEventListener("click", function() {
    context.drawImage(video, 0, 0, 640, 480);
});

// Example of form submit event listener
document.getElementById('studentForm').addEventListener('submit', function(e) {
    e.preventDefault();

    // You can now send the form data and the image from the canvas to your server
    // This part will need to be implemented based on your backend

    console.log('Form Submitted');
    // Optionally, convert canvas to image and send
    var imageData = canvas.toDataURL('image/png');
    console.log(imageData);
});
document.getElementById('studentForm').addEventListener('submit', function(e) {
    e.preventDefault();

    // Convert canvas to image blob
    canvas.toBlob(function(blob) {
        // Initialize FormData
        var formData = new FormData();
        
        // Append image file to FormData
        formData.append("studentImage", blob, "studentImage.png");
        
        // Append other form data
        formData.append("studentNumber", document.getElementById('studentNumber').value);
        formData.append("surname", document.getElementById('surname').value);
        formData.append("otherNames", document.getElementById('otherNames').value);
        formData.append("mobileNo", document.getElementById('mobileNo').value);
        formData.append("address", document.getElementById('address').value);
        formData.append("course", document.getElementById('course').value);
        formData.append("dateEnrolled", document.getElementById('dateEnrolled').value);

        // Send FormData to server
        fetch('YOUR_BACKEND_ENDPOINT_HERE', { // Replace YOUR_BACKEND_ENDPOINT_HERE with your actual backend endpoint
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            // Handle success (e.g., show a success message, redirect to another page)
        })
        .catch((error) => {
            console.error('Error:', error);
            // Handle errors here (e.g., show an error message)
        });
    }, 'image/png');
});


// window.addEventListener('load', function() {
//     var video = document.getElementById('video');
//     var snap = document.getElementById('snap');
//     var canvas = document.getElementById('canvas');
//     var imageData = document.getElementById('imageData');

//     navigator.mediaDevices.getUserMedia({ video: true })
//         .then(function(stream) {
//             video.srcObject = stream;
//         })
//         .catch(function(error) {
//             console.log("Error accessing the camera:", error);
//         });

//     snap.addEventListener('click', function() {
//         canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
//         imageData.value = canvas.toDataURL('image/png');
//     });
// });