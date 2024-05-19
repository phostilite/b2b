document.getElementById('table-search').addEventListener('input', searchDealers);
  
function searchDealers() {
    const searchInput = document.getElementById('table-search').value.toLowerCase();
    const tableRows = document.getElementsByTagName('tr');

    for (let i = 1; i < tableRows.length; i++) {
    const row = tableRows[i];
    const dealerName = row.getElementsByTagName('th')[0].textContent.toLowerCase();
    const dealerPhone = row.getElementsByTagName('td')[1].textContent.toLowerCase();
    const dealerEmail = row.getElementsByTagName('td')[2].textContent.toLowerCase();

    if (dealerName.includes(searchInput) || dealerPhone.includes(searchInput) ||  dealerEmail.includes(searchInput)) {
        row.style.display = '';
    } else {
        row.style.display = 'none';
    }
    }
}


$(".delete-dealer-link").click(function (event) {
    event.preventDefault();
    var dealerId = $(this).data("dealerId");

    if (confirm("Are you sure you want to delete this dealer?")) {
        $.ajax({
            url: "/administration/dealer/delete/" + dealerId + "/",
            type: "POST",
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
            },
            success: function (data) {
                if (data.status === 'success') {
                    alert("Dealer deleted successfully!");
                    location.reload();
                } else {
                    alert("An error occurred: " + data.message);
                }
            },
            error: function (xhr, status, error) {
                alert("An error occurred while deleting the dealer: " + error);
            }
        });
    }
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function exportTableToExcel() {
    var wb = XLSX.utils.table_to_book(document.getElementById('dealersTable'), {sheet:"Sheet 1"});
    XLSX.writeFile(wb, 'dealers.xlsx');
}