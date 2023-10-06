function saveData() {
    var latitude = document.getElementById('latitude').value;
    var longitude = document.getElementById('longitude').value;
    var cd_value = document.getElementById('cd_value').value;
    var cr_value = document.getElementById('cr_value').value;
    var ni_value = document.getElementById('ni_value').value;
    var pb_value = document.getElementById('pb_value').value;
    var zn_value = document.getElementById('zn_value').value;
    var cu_value = document.getElementById('cu_value').value;
    var co_value = document.getElementById('co_value').value;
    var username = '{{ session["username"] }}'; // Fetch the username from the server

    // Check if any of the input fields are empty
    if (
        latitude === '' ||
        longitude === '' ||
        cd_value === '' ||
        cr_value === '' ||
        ni_value === '' ||
        pb_value === '' ||
        zn_value === '' ||
        cu_value === '' ||
        co_value === ''
    ) {
        alert('All fields are required.'); // Display an error message
        return; // Stop further execution of the function
    }

    // Send the data to the server
    fetch('/save_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            latitude: latitude,
            longitude: longitude,
            cd_value: cd_value,
            cr_value: cr_value,
            ni_value: ni_value,
            pb_value: pb_value,
            zn_value: zn_value,
            cu_value: cu_value,
            co_value: co_value,
            username: username
        }),
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message); // Show a message to the user
            setTimeout(() => {
                latitude = ' ';
                longitude = '';
                cd_value = '';
                cr_value = '';
                ni_value = '';
                pb_value = '';
                zn_value = '';
                cu_value = '';
                co_value = '';
                alert(data.message) = '';
                window.location.reload()
            }, 3000)
        })
        .catch((error) => {
            console.error('Error:', error);
        });
};

function clearFields() {
    const clearedFields = ['latitude', 'longitude', 'cd_value', 'cr_value', 'ni_value', 'pb_value', 'zn_value', 'cu_value', 'co_value'];
    clearedFields.forEach(field => {
        document.getElementById(field).value = '';
    });
};

function predictAndClear() {
    var form = document.getElementById('prediction_form');
    var inputStatus = form.querySelector('input[name="input_status"]:checked');

    if (inputStatus && inputStatus.value === 'add_more') {
        // If "Add More" is selected, clear the input fields
        form.reset();
    }

    // Submit the form
    form.submit();
};

function validateForm() {
    var form = document.getElementById('predictionForm');
    var errorMessage = document.getElementById('errorMessage');
    var isValid = true;

    // Check if any input fields are empty
    var inputs = form.querySelectorAll('input[required]');
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].value.trim() === '') {
            isValid = false;
            break;
        }
    }

    // If validation fails, show error message and prevent form submission
    if (!isValid) {
        errorMessage.style.display = 'block';
        errorMessage.innerText = 'All fields are required.';
        return false; // Prevent form submission
    }

    // If validation passes, submit the form
    form.submit();
}
