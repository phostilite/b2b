document.addEventListener('DOMContentLoaded', function () {
    // 1. Get references and set the fixed year:
    const userToken = "{{ user.auth_token.key }}";
    const lineChartContainer = document.getElementById("line-chart");
    const yearToFilter = 2023;  // Hardcoded year for filtering
    const salesRevenueElement = document.getElementById("sales-revenue");
    const orderCountsElement = document.getElementById("order-counts");


    // 2. ApexCharts configuration (options1):
    const options1 = {
        chart: { 
            height: "100%",
            maxWidth: "100%",
            type: "line",
            fontFamily: "Inter, sans-serif",
            dropShadow: { enabled: false },
            toolbar: { show: false },
        },
        tooltip: { // Tooltip configuration (displays values when hovering)
            enabled: true,
            x: { show: false },
            y: {
                formatter: function(value, { series, seriesIndex, dataPointIndex, w }) {
                    if (seriesIndex === 0) {
                        return `₹${value.toFixed(2)}`;
                    } else {
                        return value;
                    }
                },
            },
        },
        dataLabels: { enabled: false }, // Disable data labels on the lines
        stroke: { width: 4, curve: 'smooth' }, // Slightly thinner line, smooth curve
        grid: { show: true, strokeDashArray: 4, padding: { left: 2, right: 2, top: -26 } }, // Styling for the grid
        series: [],  // This will be populated with data later
        legend: { show: true },  // Show the legend (series names)
        xaxis: {
            categories: [], // Month categories (Jan, Feb, ...)
            labels: {
                show: true,
                style: { fontFamily: "Inter, sans-serif", cssClass: 'text-xs font-normal fill-gray-500 dark:fill-gray-400' } // Styling
            },
            axisBorder: { show: false },
            axisTicks: { show: false },
        },
        yaxis: [ // Two y-axes for different scales
            { // First y-axis for sales revenue
                id: 'sales-axis',
                show: true,
                title: { text: 'Sales Revenue (₹)', style: { fontFamily: "Inter, sans-serif", fontSize: '12px', fontWeight: 600, cssClass: 'fill-gray-500 dark:fill-gray-400' } },
                labels: { formatter: (value) => `₹${value}` }
            },
            { // Second y-axis for order counts (modified)
                id: 'order-axis',
                show: true,
                opposite: true,
                title: { 
                  text: 'Order Counts', 
                  style: { 
                    fontFamily: "Inter, sans-serif", 
                    fontSize: '12px', 
                    fontWeight: 600, 
                    cssClass: 'fill-gray-500 dark:fill-gray-400' 
                  } 
                },
                tickAmount: 5, // Set a fixed number of ticks for better control
                min: 0, // Make sure the axis starts at zero
                forceNiceScale: true // Force whole number labels
              }
        
        ]
    };


    // 3. Fetch data function (with authentication and error handling):
    async function fetchData(apiEndpoint) {
        try {
            const response = await fetch(apiEndpoint, {
                headers: { 'Authorization': `Token ${userToken}`, 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error(`API Error: ${response.status}`);
            return response.json();
        } catch (error) {
            lineChartContainer.innerHTML = `<p class='text-red-500'>${error.message}</p>`;
            return null; 
        }
    }

    const fetchChartData = () => fetchData('/api/line-chart-data/');

    // 4. Update and render chart function (filtered by year):
    function updateChart(year) {
        fetchChartData().then(allChartData => {
            if (!allChartData) return; // Handle API error
            if (yearToFilter && !allChartData[yearToFilter]) {
                // Display an error message for the specific year
                lineChartContainer.innerHTML = `<p class='text-red-500'>No data found for the year ${yearToFilter}.</p>`;
                return;
            }
            const chartData = allChartData[yearToFilter].monthly_data || []; 
            const totalSalesRevenue = allChartData[yearToFilter].total_data.sales_revenue;
            const totalOrdersReceived = allChartData[yearToFilter].total_data.orders_received;

            salesRevenueElement.textContent = `₹${(totalSalesRevenue || 0).toLocaleString()}`;
            orderCountsElement.textContent = `${(totalOrdersReceived || 0).toLocaleString()}`;

            // Prepare series data (only for the filtered year)
            const seriesData = [
                { name: `Sales Revenue`, data: chartData.map(item => item.sales_revenue), yAxisID: 'sales-axis' },
                { name: `Orders Received`, data: chartData.map(item => item.orders_received), yAxisID: 'order-axis' },
                { name: `Orders Processed`, data: chartData.map(item => item.orders_processed), yAxisID: 'order-axis' },
                { name: `Orders Delivered`, data: chartData.map(item => item.orders_delivered), yAxisID: 'order-axis' }
            ];

            // Update chart options with new data
            options1.series = seriesData;
            options1.xaxis.categories = chartData.map(item => item.month);

            // Render the chart
            if (typeof ApexCharts !== 'undefined') {
                const chart = new ApexCharts(lineChartContainer, options1);
                chart.render();
            } else {
                console.error("ApexCharts library not found.");
            }
        });
    }

    // 5. Initial chart rendering for the specified year:
    updateChart(yearToFilter); // Call the updateChart function with the filtered year
});
