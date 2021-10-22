/* eslint-disable no-unused-vars */
import { Typography } from "@mui/material";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import { useCallback, useEffect } from "react";
import LineChart from "./LineChart";
import Queue from "./Queue";

const defaultSensorData = [
  {
    accelerometer: new Queue(),
    gyroscope: new Queue()
  },
  {
    accelerometer: new Queue(),
    gyroscope: new Queue()
  },
  {
    accelerometer: new Queue(),
    gyroscope: new Queue()
  }
]

var sensorData = defaultSensorData;

function Sensor({isPaused}) {
  const GetSensor = useCallback(async (dancerId) => {
    console.log("Sensor" + dancerId + " update");
    const response = await fetch("https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/GetSensor?dancerId=" + dancerId);
    if (response.status >= 200 && response.status <= 299) {
      const data = await response.json();
      if (data) {
        const formatted = (
          {
            accelerometer: data.accelerometer,
            gyroscope: data.gyroscope
          }
        );
        formatted.accelerometer.forEach(element => sensorData[dancerId - 1].accelerometer.enqueue(element));
        formatted.gyroscope.forEach(element => sensorData[dancerId - 1].gyroscope.enqueue(element));
      }
      return;
    } else {
      // Handle errors
      console.log(response.status, response.statusText);
    }
  }, []);

  useEffect(() => {
    let interval = null;
    if (isPaused) {
      clearInterval(interval);
    } else {
      interval = setInterval(() => {
        GetSensor("1");
        GetSensor("2");
        GetSensor("3");
      }, 1000);
    }
    return () => {
      clearInterval(interval);
    };
  }, [isPaused, GetSensor]);

  function GetLatestAccelerometer(dancerId) {
    return sensorData[dancerId - 1].accelerometer.dequeue();
  }

  function GetLatestGyroscope(dancerId) {
    return sensorData[dancerId - 1].gyroscope.dequeue();
  }

  return (
    <Container maxWidth='md'>
      <Typography align="center" variant="h5" gutterBottom={true}>
        Dancer 1
      </Typography>
      <Grid
        container
        spacing={3}
      >
        <Grid item xs={6}>
          <Typography align="center">
            Accelerometer
          </Typography>
          <LineChart dancerId={1} GetLatestData={GetLatestAccelerometer} />
        </Grid>
        <Grid item xs={6}>
          <Typography align="center">
            Gyroscope
          </Typography>
          <LineChart dancerId={1} GetLatestData={GetLatestGyroscope} />
        </Grid>
      </Grid>
      <Typography align="center" variant="h5" gutterBottom={true}>
        Dancer 2
      </Typography>
      <Grid
        container
        spacing={3}
      >
        <Grid item xs={6}>
          <Typography align="center">
            Accelerometer
          </Typography>
          <LineChart dancerId={2} GetLatestData={GetLatestAccelerometer} />
        </Grid>
        <Grid item xs={6}>
          <Typography align="center">
            Gyroscope
          </Typography>
          <LineChart dancerId={2} GetLatestData={GetLatestGyroscope} />
        </Grid>
      </Grid>
      <Typography align="center" variant="h5" gutterBottom={true}>
        Dancer 3
      </Typography>
      <Grid
        container
        spacing={3}
      >
        <Grid item xs={6}>
          <Typography align="center">
            Accelerometer
          </Typography>
          <LineChart dancerId={3} GetLatestData={GetLatestAccelerometer} />
        </Grid>
        <Grid item xs={6}>
          <Typography align="center">
            Gyroscope
          </Typography>
          <LineChart dancerId={3} GetLatestData={GetLatestGyroscope} />
        </Grid>
      </Grid>
    </Container>
  )
}

export default Sensor;