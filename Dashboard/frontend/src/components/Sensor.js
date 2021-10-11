/* eslint-disable no-unused-vars */
import { Typography } from "@mui/material";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import { useCallback, useEffect } from "react";
import LineChart from "./LineChart";
import Queue from "./Queue";

const defaultSensorData = {
  accelerometer: [],
  gyroscope: []
}

var sensorData = defaultSensorData;

var accelerometer = new Queue();
var gyroscope = new Queue();

function Sensor({isPaused, dancerNum}) {
  const GetSensor = useCallback(async (collectionName) => {
    console.log(collectionName + " update");
    const response = await fetch("https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/GetSensor?collectionName=" + collectionName);
    if (response.status >= 200 && response.status <= 299) {
      const data = await response.json();
      if (data) {
        const formatted = (
          {
            accelerometer: data.accelerometer,
            gyroscope: data.gyroscope
          }
        );
        if (JSON.stringify(formatted) !== JSON.stringify(sensorData)) {
          formatted.accelerometer.forEach(element => accelerometer.enqueue(element));
          formatted.gyroscope.forEach(element => gyroscope.enqueue(element));
          sensorData = formatted;
        }
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
        GetSensor("Sensor" + dancerNum);
      }, 500);
    }
    return () => {
      clearInterval(interval);
    };
  }, [isPaused, dancerNum, GetSensor]);

  function GetLatestAccelerometer() {
    return accelerometer.dequeue();
  }

  function GetLatestGyroscope() {
    return gyroscope.dequeue();
  }

  return (
    <Container maxWidth='md'>
      <Typography align="center" variant="h5" gutterBottom={true}>
        Dancer {dancerNum}
      </Typography>
      <Grid
        container
        spacing={3}
      >
        <Grid item xs={8}>
          <Typography align="center">
            Accelerometer
          </Typography>
          <LineChart GetLatestData={GetLatestAccelerometer} />
        </Grid>
        <Grid item xs={8}>
          <Typography align="center">
            Gyroscope
          </Typography>
          <LineChart GetLatestData={GetLatestGyroscope} />
        </Grid>
      </Grid>
    </Container>
  )
}

export default Sensor;