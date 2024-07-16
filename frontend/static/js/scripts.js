document.addEventListener('DOMContentLoaded', function() {
    // Function to retrieve CSRF token from cookies
    function getCSRFToken() {
        const cookieValue = document.cookie.match(/csrftoken=([^ ;]+)/)[1];
        return cookieValue;
    }

    // Generate Bills
    document.querySelectorAll('.generate-bills-btn').forEach(button => {
        button.addEventListener('click', function() {
            const investorId = this.getAttribute('data-investor-id');
            generateBills(investorId);
        });
    });

    // Update Capital Call Status
    document.querySelectorAll('.update-status-btn').forEach(button => {
        button.addEventListener('click', function() {
            const capitalCallId = this.getAttribute('data-capital-call-id');
            updateCapitalCallStatus(capitalCallId);
        });
    });

    // Create Capital Call
    document.getElementById('create-capital-call-btn').addEventListener('click', createCapitalCall);

    function generateBills(investorId) {
        fetch(`/api/investors/${investorId}/generate_bills/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(), // Include CSRF token here
            },
            body: JSON.stringify({ fee_percentage: 0.01 }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                alert(data.message);
                location.reload();
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    }

    function createCapitalCall() {
        const investorId = prompt("Enter Investor ID:");
        const billIds = prompt("Enter Bill IDs (comma-separated):").split(',').map(id => parseInt(id.trim()));
        const iban = prompt("Enter IBAN:");

        fetch('/api/capital-calls/create_for_investor/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(), // Include CSRF token here
            },
            body: JSON.stringify({ 
                investor_id: parseInt(investorId),
                bill_ids: billIds,
                iban: iban
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                alert("Capital Call created successfully");
                location.reload();
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    }

    function updateCapitalCallStatus(capitalCallId) {
        const newStatus = prompt("Enter new status (validated/sent/paid/overdue):");

        fetch(`/api/capital-calls/${capitalCallId}/update_status/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(), // Include CSRF token here
            },
            body: JSON.stringify({ status: newStatus }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                alert("Capital Call status updated successfully");
                location.reload();
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
