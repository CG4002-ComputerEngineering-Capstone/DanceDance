/* eslint-disable no-unused-vars */
import { Typography } from "@mui/material";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import { useCallback, useEffect } from "react";
import LineChart from "./LineChart";
import Queue from "./Queue";

const defaultSensorData = {
  accelLeft: [],
  accelRight: [],
  gyroLeft: [],
  gyroRight: []
}

var sensorData = defaultSensorData;

var accelLeft = new Queue();
var accelRight = new Queue();
var gyroLeft = new Queue();
var gyroRight = new Queue();

function Sensor({isPaused, dancerNum}) {
  const GetSensor = useCallback(async (collectionName) => {
    console.log(collectionName + " update");
    const response = await fetch("https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/GetSensor?collectionName=" + collectionName);
    if (response.status >= 200 && response.status <= 299) {
      const data = await response.json();
      if (data) {
        const formatted = (
          {
            accelLeft: data.accelLeft,
            accelRight: data.accelRight,
            gyroLeft: data.gyroLeft,
            gyroRight: data.gyroRight
          }
        ); 
        if (JSON.stringify(formatted) !== JSON.stringify(sensorData)) {
          formatted.accelLeft.forEach(element => accelLeft.enqueue(element));
          formatted.accelRight.forEach(element => accelRight.enqueue(element));
          formatted.gyroLeft.forEach(element => gyroLeft.enqueue(element));
          formatted.gyroRight.forEach(element => gyroRight.enqueue(element));
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
      }, 1000);
    }
    return () => {
      clearInterval(interval);
    };
  }, [isPaused, dancerNum, GetSensor]);

  function getLatestAccelLeft() {
    return accelLeft.dequeue();
  }

  function getLatestAccelRight() {
    return accelRight.dequeue();
  }

  function getLatestGyroLeft() {
    return gyroLeft.dequeue();
  }

  function getLatestGyroRight() {
    return gyroRight.dequeue();
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
        <Grid item xs={6}>
          <Typography align="center">
            Left Accelerometer
          </Typography>
          <LineChart getLatestData={getLatestAccelLeft} />
        </Grid>
        <Grid item xs={6}>
          <Typography align="center">
            Right Accelerometer
          </Typography>
          <LineChart getLatestData={getLatestAccelRight} />
        </Grid>
        <Grid item xs={6}>
          <Typography align="center">
            Left Gyroscope
          </Typography>
          <LineChart getLatestData={getLatestGyroLeft} />
        </Grid>
        <Grid item xs={6}>
          <Typography align="center">
            Right Gyroscope
          </Typography>
          <LineChart getLatestData={getLatestGyroRight} />
        </Grid>
      </Grid>
    </Container>
  )
}

export default Sensor;