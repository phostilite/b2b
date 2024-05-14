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


            // Populate colors
            var colorsInput = $("#id_colors");
            var colors = data.colors.join(", ");
            colorsInput.val(colors);

            // Populate size groups
            var sizeGroupsInput = $("#id_size_groups");
            var sizeGroupsText = [];

            data.size_groups.forEach(function(sizeGroup) {
                var groupText = sizeGroup.name + ": " + sizeGroup.sizes.join(", ");
                sizeGroupsText.push(groupText);
            });

            sizeGroupsInput.val(sizeGroupsText.join(" | "));

            // Populate images
            var imagesContainer = $("#images-container");
            imagesContainer.empty();
            data.images.forEach(function(imageUrl) {
                imagesContainer.append("<div class='relative'><img src='" + imageUrl + "' alt='Product Image' class='w-full h-auto'></div>");
            });

            $("#productUpdateForm").data("productId", productId);
            $("#editProductModal").modal("show");
            },
    });
});

$("#productUpdateForm").submit(function (event) {
    event.preventDefault();
    var formData = new FormData(this);
    var productId = $(this).data("id");

    $.ajax({
        url: "/administration/update_product/" + productId + "/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        beforeSend: function (xhr) {
            xhr.setRequestHeader(
                "X-CSRFToken",
                $("input[name=csrfmiddlewaretoken]").val()
            );
        },
        success: function (data) {
            if (data.success) {
                var modal = document.querySelector("#editProductModal");
                modal.classList.add("hidden");
                modal.setAttribute("aria-hidden", "true");

                alert("Product updated successfully!");
                location.reload();
            } else {
                var errors = data.errors;
                for (var field in errors) {
                    var errorMessages = errors[field];
                    alert("Error in " + field + ": " + errorMessages.join(", "));
                }
            }
        },
    });
});
