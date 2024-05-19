document.getElementById('table-search').addEventListener('input', searchProducts);

function searchProducts() {
    const searchInput = document.getElementById('table-search').value.toLowerCase();
    const tableRows = document.getElementsByTagName('tr');

    for (let i = 1; i < tableRows.length; i++) {
        const row = tableRows[i];
        const productTitle = row.getElementsByTagName('td')[2].textContent.toLowerCase();
        const productDesignNumber = row.getElementsByTagName('td')[1].textContent.toLowerCase();

        if (productTitle.includes(searchInput) || productDesignNumber.includes(searchInput)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    }
}

$(".edit-product-link").click(function (event) {
    event.preventDefault();
    var productId = $(this).data("productId");
    console.log(productId);

    $.ajax({
        url: "/administration/product/" + productId + "/",
        dataType: "json",
        success: function (data) {
            $("#id_title").val(data.title);
            $("#id_description").val(data.description);
            $('#id_design_number').val(data.design_number);
            $('#id_type').val(data.type);
            $('#id_current_stock').val(data.current_stock);
            $('#id_mrp').val(data.mrp);
            $('#id_dealer_price').val(data.dealer_price);

            var sizeGroupsInput = $("#id_available_size_groups");
            sizeGroupsInput.empty(); 
            data.all_size_groups.forEach(function(sizeGroup) {
                var option = $('<option></option>').val(sizeGroup.name).text(sizeGroup.name);
                if (sizeGroup.selected) {
                    option.prop('selected', true);
                }
                sizeGroupsInput.append(option);
            });

            var colorsInput = $("#id_colors");
            colorsInput.empty();  
            data.all_colors.forEach(function(color) {
                var option = $('<option></option>').val(color.name).text(color.name);
                if (color.selected) {
                    option.prop('selected', true);
                }
                colorsInput.append(option);
            });

            $("#productUpdateForm").data("productId", productId);
            $("#editProductModal").modal("show");
        },
    });
});

$("#productUpdateForm").submit(function (event) {
    event.preventDefault();
    var productId = $(this).data("productId");

    var formData = {
        'title': $("#id_title").val(),
        'description': $("#id_description").val(),
        'design_number': $('#id_design_number').val(),
        'type': $('#id_type').val(),
        'current_stock': $('#id_current_stock').val(),
        'mrp': $('#id_mrp').val(),
        'dealer_price': $('#id_dealer_price').val(),
        'all_colors': $('#id_colors option:selected').map(function() {
            return $(this).val();
        }).get(),
        'all_size_groups': $('#id_available_size_groups option:selected').map(function() {
            return $(this).val();
        }).get()
    };

    $.ajax({
        url: "/administration/product/update/" + productId + "/",
        type: "POST",
        data: JSON.stringify(formData),
        contentType: "application/json",
        success: function (data) {
            alert("Product updated successfully!");
            location.reload();
            $("#editProductModal").modal("hide");
        },
        error: function (xhr, status, error) {
            console.error("Update failed:", error);
            alert("An error occurred while updating the product: " + error);
        }
    });
});

function exportTableToExcel() {
    var wb = XLSX.utils.table_to_book(document.getElementById('productsTable'), {sheet:"Sheet 1"});
    XLSX.writeFile(wb, 'products.xlsx');
}


$(".delete-product-link").click(function (event) {
    event.preventDefault();
    var productId = $(this).data("productId");

    if (confirm("Are you sure you want to delete this product?")) {
        $.ajax({
            url: "/administration/product/delete/" + productId + "/",
            type: "POST",
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
            },
            success: function (data) {
                alert("Product deleted successfully!");
                location.reload();
            },
            error: function (xhr, status, error) {
                alert("An error occurred while deleting the product: " + error);
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