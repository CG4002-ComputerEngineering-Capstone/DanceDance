import React from 'react';
import { Line, Chart } from 'react-chartjs-2';
import 'chartjs-adapter-luxon';
import StreamingPlugin from 'chartjs-plugin-streaming';
import { DateTime } from 'luxon';

Chart.register(StreamingPlugin);

function LineChart({dancerId, GetLatestData}) {
  return (
    <Line
      data={{
        datasets: [{
          backgroundColor: 'rgba(255, 0, 0, 0.2)',
          borderColor: 'rgb(255, 0, 0)',
          borderWidth: 1,
          cubicInterpolationMode: 'default',
          data: [],
          fill: false,
          label: 'x',
          pointBorderWidth: 1,
          pointRadius: 1,
          tension: 0.1
        }, {
          backgroundColor: 'rgba(0, 255, 0, 0.2)',
          borderColor: 'rgb(0, 255, 0)',
          borderWidth: 1,
          cubicInterpolationMode: 'default',
          data: [],
          fill: false,
          label: 'y',
          pointBorderWidth: 1,
          pointRadius: 1,
          tension: 0.1
        }, {
          backgroundColor: 'rgba(0, 0, 255, 0.2)',
          borderColor: 'rgb(0, 0, 255)',
          borderWidth: 1,
          cubicInterpolationMode: 'default',
          data: [],
          fill: false,
          label: 'z',
          pointBorderWidth: 1,
          pointRadius: 1,
          tension: 0.1
        }
      ]
      }}
      options={{
        responsive: true,
        scales: {
          x: {
            type: 'realtime',
            realtime: {
              duration: 8000,
              refresh: 50,
              delay: 1000,
              pause: false,
              ttl: undefined,
              frameRate: 30,
              onRefresh: chart => {
                var data = GetLatestData(dancerId);
                if (data) {
                  chart.data.datasets[0].data.push({x: DateTime.now(), y: parseInt(data.x)});
                  chart.data.datasets[1].data.push({x: DateTime.now(), y: parseInt(data.y)});
                  chart.data.datasets[2].data.push({x: DateTime.now(), y: parseInt(data.z)});
                }
              }
            }
          },
          y: {
            suggestedMax: 1,
            suggestedMin: -1
          }
        }
      }}
    />
  );
}

export default LineChart;