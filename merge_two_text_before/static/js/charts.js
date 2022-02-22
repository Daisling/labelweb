  var getData = $.get('/data');

  getData.done(function(results){


      var ctx = document.getElementById('myChart').getContext('2d');
      var chart = new Chart(ctx, {
          // The type of chart we want to create
          type: 'line',

          // The data for our dataset
          data: {
              labels: results.count,
              datasets: [{
                  label: "损失",
                  //backgroundColor: 'rgb(0, 99, 132)',
                  borderColor: 'rgb(0, 99, 132)',
                  data: results.accuracy,
              },{
                  label: "单标签准确度",
                  //backgroundColor: 'rgb(0, 200, 0)',
                  borderColor: 'rgb(0, 200, 0)',
                  data: results.single_lable,
              },{
                  label: "双标签准确度",
                  //backgroundColor: 'rgb(200, 0, 0)',
                  borderColor: 'rgb(200, 0, 0)',
                  data: results.double_lable,
              },{
                  label: "三标签准确度",
                  //backgroundColor: 'rgb(0, 0, 200)',
                  borderColor: 'rgb(255, 255, 0)',
                  data: results.three_lable,
              }
            ]
          },

          // Configuration options go here
          options: {}
      });
 });