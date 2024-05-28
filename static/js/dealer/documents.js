function exportTableToExcel() {
    var wb = XLSX.utils.table_to_book(document.getElementById('documentsTable'), {sheet:"Sheet 1"});
    XLSX.writeFile(wb, 'documents.xlsx');
}

$(document).ready(function() {
    $('.delete-document-link').click(function(e) {
        e.preventDefault();
        var documentId = $(this).data('documentId');
        deleteDocument(documentId);
    });
});


function deleteDocument(documentId) {
    $.ajax({
        url: '/dealers/delete_document/' + documentId + '/',
        method: 'DELETE',
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        },
        success: function(response) {
            console.log('Document deleted successfully');
            alert('Document deleted successfully');
            $('tr[data-document-id="' + documentId + '"]').remove();
        },
        error: function(xhr, status, error) {
            console.error('Error deleting document:', error);
            alert('Error deleting document: ' + error);
        }
    });
}

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