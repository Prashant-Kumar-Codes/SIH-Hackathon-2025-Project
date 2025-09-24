// Simple Line Chart using Chart.js
const ctx = document.getElementById('lineChart').getContext('2d');
new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Oct','Nov','Dec','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep'],
    datasets: [{
      label: 'Active Users',
      data: [3,4,3.5,4,5,6,5.5,7,6.5,7.5,8,9],
      borderColor: '#00b4d8',
      backgroundColor: 'transparent',
      tension: 0.3
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { x: { ticks:{color:'#fff'}}, y:{ticks:{color:'#fff'}} }
  }
});
