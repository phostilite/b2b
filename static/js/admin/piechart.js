
window.onload = function () {
    var userToken = "{{ user.auth_token.key }}"; // Replace with your actual token

    function fetchData(apiEndpoint) {
        return fetch(apiEndpoint, {
            method: 'GET',
            headers: {
                'Authorization': 'Token ' + userToken,
                'Content-Type': 'application/json',
            }
        })
            .then(response => response.json())
            .catch(error => {
                console.error('Error fetching data:', error);
                return null;
            });
    }

    const fetchCategorySalesData = async () => {
        const data = await fetchData('/api/category-sales/');
        return data;
    };

    const getUniqueColor = (name) => {
        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }

        const hue = hash % 360;
        return `hsl(${hue}, 80%, 60%)`;
    };


    const getChartOptions = (categories) => {
        const chartData = categories.map(category => ({
            name: category.name,
            data: [category.revenue]
        }));

        const colors = categories.map(category => getUniqueColor(category.name));

        return {
            series: chartData.map(item => item.data[0]),
            colors: colors,
            chart: {
                height: 420,
                width: "100%",
                type: "pie",
            },
            stroke: {
                colors: ["white"],
                lineCap: "",
            },
            plotOptions: {
                pie: {
                    labels: {
                        show: true,
                    },
                    size: "100%",
                    dataLabels: {
                        offset: -25
                    },
                },
            },
            labels: categories.map(category => category.name),
            dataLabels: {
                enabled: true,
                style: {
                    fontFamily: "Inter, sans-serif",
                },
            },
            legend: {
                position: "bottom",
                fontFamily: "Inter, sans-serif",
            },
            yaxis: {
                labels: {
                    formatter: function (value) {
                        return value.toFixed(2);
                    },
                },
            },
        };
    };

    const categorySalesContainer = document.getElementById("categorySalesContainer");

    const renderCategorySales = (categories) => {
        categorySalesContainer.innerHTML = ""; // Clear previous content

        categories.forEach(category => {
            const salesItem = document.createElement("dl");
            salesItem.innerHTML = `
                <dt class="text-base font-normal text-gray-500 dark:text-gray-400 pb-1">Sales by ${category.name}</dt>
                <dd class="leading-none text-xl font-bold text-gray-900 dark:text-green-400">₹${category.revenue.toFixed(2)}</dd>
            `;
            categorySalesContainer.appendChild(salesItem);
        });
    };

    const renderChart = async () => {
        const categorySalesData = await fetchCategorySalesData();
        if (categorySalesData && categorySalesData.categories) {
            renderCategorySales(categorySalesData.categories);
            const chartOptions = getChartOptions(categorySalesData.categories);
            const chart = new ApexCharts(document.getElementById("pie-chart"), chartOptions);
            chart.render();
        }
    };

    renderChart();
}
