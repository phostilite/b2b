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


$(".update-product-images").click(function (event) {
    event.preventDefault();
    var productId = $(this).data("productId");
    console.log(productId);

    $("#file-input").val('');

    $.ajax({
        url: "/administration/product/" + productId + "/",
        dataType: "json",
        success: function (data) {
            var imagesContainer = $("#images-container");
            imagesContainer.empty();
            data.images.forEach(function(image) {
                var imageContainer = $("<div>", { class: "relative" });
                var imageLink = $("<a>", {
                    href: image.url,
                    target: "_blank"
                });
                var imageElement = $("<img>", {
                    src: image.url,
                    alt: 'Product Image',
                    class: 'w-full h-auto'
                });
                var deleteButton = $("<button>", {
                    type: "button",
                    class: "absolute top-2 right-2 hover:bg-red-500 hover:bg-opacity-20 rounded-full p-1",
                    "data-image-id": image.id,
                    "data-product-id": productId
                }).html(`
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 48 48">
                        <path fill="#f44336" d="M44,24c0,11.045-8.955,20-20,20S4,35.045,4,24S12.955,4,24,4S44,12.955,44,24z"></path>
                        <path fill="#fff" d="M29.656,15.516l2.828,2.828l-14.14,14.14l-2.828-2.828L29.656,15.516z"></path>
                        <path fill="#fff" d="M32.484,29.656l-2.828,2.828l-14.14-14.14l2.828-2.828L32.484,29.656z"></path>
                    </svg>
                `);

                imageLink.append(imageElement);
                imageContainer.append(imageLink, deleteButton);
                imagesContainer.append(imageContainer);
            });
            $("#product-images-modal").modal("show");
        },
    });
});

$("#images-container").on("click", "button", function() {
    var imageId = $(this).data("imageId");
    var productId = $(this).data("productId");
    console.log(productId, imageId);
    var confirmation = confirm("Are you sure you want to delete this image?");

    if (confirmation) {
        deleteImage(productId, imageId);
    }
});


function deleteImage(productId, imageId) {
    $.ajax({
        url: window.location.pathname + productId + "/delete-image/" + imageId + "/", // Update the URL here
        method: "POST",
        data: {
            product_id: productId,
            image_id: imageId
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        },
        success: function(data) {
            if (data.success) {
                alert("Product image deleted successfully!");
                location.reload();
            } else {
                alert(data.error);
            }
        },
        error: function() {
            alert("An error occurred while deleting the image.");
        }
    });
}


$("#upload-images-button").click(function() {
    var fileInput = $("#file-input")[0];
    var files = fileInput.files;
    var formData = new FormData();
    var productId = $(".update-product-images").data("productId");

    for (var i = 0; i < files.length; i++) {
        formData.append('images', files[i]);
    }

    $.ajax({
        url: window.location.pathname + productId + "/upload-images/",
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        },
        success: function(data) {
            if (data.success) {
                alert("Product image uploaded successfully!");
                location.reload();
            } else {
                alert(data.error);
            }
        },
        error: function() {
            alert("An error occurred while uploading the images.");
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