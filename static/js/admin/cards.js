
var userToken = "{{ user.auth_token.key }}";

function fetchData(apiEndpoint) {
    fetch(apiEndpoint, {
        method: 'GET',
        headers: {
            'Authorization': 'Token ' + userToken,
            'Content-Type': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-orders').textContent = data.total_orders;
            document.getElementById('todays-orders').textContent = data.todays_orders;
            document.getElementById('total-sales').textContent = '₹' + data.total_sales;
            document.getElementById('pending-orders').textContent = data.pending_orders;
            document.getElementById('approved-orders').textContent = data.approved_orders;
            document.getElementById('canceled-orders').textContent = data.canceled_orders;

            var approvedPercentage = (data.approved_orders / data.total_orders) * 100;
            var canceledPercentage = (data.canceled_orders / data.total_orders) * 100;

            document.querySelector('.approved-progress').style.width = approvedPercentage + '%';
            document.querySelector('.canceled-progress').style.width = canceledPercentage + '%';
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}
fetchData('/api/orders-summary/');


function fetchTopSellingProducts(apiEndpoint) {
    fetch(apiEndpoint, {
        method: 'GET',
        headers: {
            'Authorization': 'Token ' + userToken,
            'Content-Type': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            const topProductsList = document.querySelector('.top-products-list');
            topProductsList.innerHTML = ''; // Clear previous products

            // Check if data is an object with a message property
            if (typeof data === 'object' && data.hasOwnProperty('message')) {
                topProductsList.textContent = data.message;
                return;
            }

            data.slice(0, 4).forEach(product => {
                const listItem = document.createElement('li');
                listItem.classList.add('flex', 'items-center', 'justify-between', 'py-2');

                const productDetails = document.createElement('div');
                productDetails.classList.add('flex', 'items-center');

                const productImage = document.createElement('img');
                productImage.src = product.image_url || 'https://via.placeholder.com/50';
                productImage.alt = 'Product Image';
                productImage.classList.add('top-product-image', 'w-10', 'h-10', 'rounded-md', 'mr-3');

                const productName = document.createElement('span');
                productName.textContent = product.name;
                productName.classList.add('text-gray-800', 'dark:text-white');

                const salesCount = document.createElement('span');
                salesCount.textContent = `${product.sales_count} Sold`;
                salesCount.classList.add('text-gray-500', 'dark:text-gray-400');

                productDetails.appendChild(productImage);
                productDetails.appendChild(productName);
                listItem.appendChild(productDetails);
                listItem.appendChild(salesCount);
                topProductsList.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error('Error fetching top-selling products:', error);
        });
}

// Call the function with the API endpoint URL
fetchTopSellingProducts('/api/top-selling-products/');


function fetchLowStockProducts(apiEndpoint) {
    fetch(apiEndpoint, {
        method: 'GET',
        headers: {
            'Authorization': 'Token ' + userToken,
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        var lowStockList = document.querySelector('.low-stock-list');
        lowStockList.innerHTML = ''; // Clear the list

        data.forEach(product => {
            var listItem = document.createElement('li');
            listItem.className = 'flex items-center justify-between py-2';

            var productNameDiv = document.createElement('div');
            productNameDiv.className = 'flex items-center';
            var productNameSpan = document.createElement('span');
            productNameSpan.className = 'text-gray-800 dark:text-white';
            productNameSpan.textContent = product.title;
            productNameDiv.appendChild(productNameSpan);

            var productStockDiv = document.createElement('div');
            productStockDiv.className = 'flex items-center';
            var productStockSpan = document.createElement('span');
            productStockSpan.className = 'text-gray-500 dark:text-gray-400';
            productStockSpan.textContent = product.current_stock + ' units';
            productStockDiv.appendChild(productStockSpan);

            listItem.appendChild(productNameDiv);
            listItem.appendChild(productStockDiv);

            lowStockList.appendChild(listItem);
        });
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

fetchLowStockProducts('/api/low-stock-alert/');