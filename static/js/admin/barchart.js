document.addEventListener('DOMContentLoaded', function () {
    const barChartContainer = document.getElementById("bar-chart");
    const salesDealer = document.getElementById("sales-by-dealer");
    const salesStaff = document.getElementById("sales-by-employee");

    async function fetchData(apiEndpoint) {
        try {
            const response = await fetch(apiEndpoint, {
                headers: { 'Authorization': `Token ${userToken}`, 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error(`API Error: ${response.status}`);

            return response.json();
        } catch (error) {
            barChartContainer.innerHTML = `<p class='text-red-500'>${error.message}</p>`;
            return null;
        }
    }

    fetchData('/api/yearly_user_type_sales/')
        .then(data => {
            if (data === null) {
                barChartContainer.innerHTML = `<p class='text-red-500'>Failed to fetch data from the API.</p>`;
                return;
            }

            const yearData = data['2024'];
            if (!yearData) {
                barChartContainer.innerHTML = `<p class='text-red-500'>No data available for the year 2024.</p>`;
                return;
            }

            const totalSalesDealer = yearData.dealer.total_data.sales_revenue;
            const totalSalesEmployee = yearData.employee.total_data.sales_revenue;

            salesDealer.textContent = `₹${(totalSalesDealer || 0).toLocaleString()}`;
            salesStaff.textContent = `₹${(totalSalesEmployee || 0).toLocaleString()}`;

            const options2 = {
                series: [
                    {
                        name: "Dealers",
                        data: yearData.dealer.monthly_data.map(monthData => monthData.monthly_sales)
                    },
                    {
                        name: "Sales Staff",
                        data: yearData.employee.monthly_data.map(monthData => monthData.monthly_sales)
                    }
                ],
                chart: {
                    sparkline: {
                        enabled: false,
                    },
                    type: "bar",
                    width: "100%",
                    height: 420,
                    toolbar: {
                        show: false,
                    },
                },
                fill: {
                    opacity: 1,
                },
                plotOptions: {
                    bar: {
                        horizontal: true,
                        columnWidth: "100%",
                        borderRadiusApplication: "end",
                        borderRadius: 6,
                        dataLabels: {
                            position: "top",
                        },
                    },
                },
                legend: {
                    show: true,
                    position: "bottom",
                },
                dataLabels: {
                    enabled: false,
                },
                tooltip: {
                    y: {
                        formatter: function (val) {
                            return "₹" + val.toLocaleString();
                        }
                    },
                    shared: true, // Show tooltip for all series
                    intersect: false // Show tooltip for all bars
                },
                labels: {
                    show: true,
                    style: {
                        fontFamily: "Inter, sans-serif",
                        cssClass: "text-xs font-normal fill-gray-500 dark:fill-gray-400",
                    },
                    formatter: function (value) {
                        return "₹" + value;
                    },
                },
                xaxis: {
                    categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                },
                yaxis: {
                    labels: {
                        show: true,
                        style: {
                            fontFamily: "Inter, sans-serif",
                            cssClass: "text-xs font-normal fill-gray-500 dark:fill-gray-400",
                        },
                    },
                },
                axisTicks: {
                    show: false,
                },
                axisBorder: {
                    show: false,
                },
                grid: {
                    show: true,
                    strokeDashArray: 4,
                    padding: {
                        left: 2,
                        right: 2,
                        top: -20,
                    },
                },
                fill: {
                    opacity: 1,
                },
            };

            

            if (document.getElementById("bar-chart") && typeof ApexCharts !== "undefined") {
                const chart = new ApexCharts(document.getElementById("bar-chart"), options2);
                chart.render();
            } else {
                barChartContainer.innerHTML = `<p class='text-red-500'>Failed to render the chart.</p>`;
            }
        })
        .catch(error => {
            barChartContainer.innerHTML = `<p class='text-red-500'>${error.message}</p>`;
        });
});