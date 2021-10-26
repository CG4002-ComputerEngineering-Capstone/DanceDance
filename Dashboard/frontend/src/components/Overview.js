import React, { useEffect, useState } from "react";
import Container from '@mui/material/Container';
import Grid from "@mui/material/Grid"

import Dancer from "./Dancer";
import EMG from "./EMG";
import SyncDelay from "./SyncDelay";
import { Typography } from "@mui/material";

const defaultPredictionData = {
  move: ["-", "-", "-"],
  position: [1, 2, 3],
  syncDelay: 0
}

const defaultEMGData = {
  emg: [0, 0, 0]
}

function Overview({isPaused}) {
  const [predictionData, setPredictionData] = useState(defaultPredictionData);
  const [emgData, setEMGData] = useState(defaultEMGData);

  async function GetPrediction() {
    console.log("Prediction update");
    const response = await fetch("https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/GetPrediction");
    if (response.status >= 200 && response.status <= 299) {
      const data = await response.json();
      if (data) {
        try {
          setPredictionData(
            {
              move: data.move,
              position: JSON.parse(data.position),
              syncDelay: JSON.parse(data.syncDelay)
            }
          );
        } catch (err) {
          console.log(err);
        }
      } else {
        setPredictionData(defaultPredictionData);
      }
      return;
    } else {
      // Handle errors
      console.log(response.status, response.statusText);
    }
    return;
  }

  async function GetEMG() {
    console.log("EMG update");
    const response = await fetch("https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/GetEMG");
    if (response.status >= 200 && response.status <= 299) {
      const data = await response.json();
      if (data) {
        try {
          setEMGData({emg: JSON.parse(data.emg)});
        } catch (err) {
          console.log(err);
        }
      } else {
        setEMGData(defaultEMGData);
      }
      return;
    } else {
      // Handle errors
      console.log(response.status, response.statusText);
    }
    return;
  }

  useEffect(() => {
    let predictionInterval = null;
    let emgInterval = null
    if (isPaused) {
      clearInterval(predictionInterval);
      clearInterval(emgInterval);
    } else {
      predictionInterval = setInterval(() => {
        GetPrediction();
      }, 1000);
      emgInterval = setInterval(() => {
        GetEMG();
      }, 500);
    }
    return () => {
      clearInterval(predictionInterval);
      clearInterval(emgInterval);
    };
  }, [isPaused]);

  return (
    <Container maxWidth='md'>
      <Typography align="center" variant="h5" gutterBottom={true}>
        Overview
      </Typography>
      <Grid
        container
        spacing={3}
      >
        <Grid item xs={4}>
          <Dancer dancerNumber={predictionData.position[0]} currentMove={predictionData.move[0]} />
        </Grid>
        <Grid item xs={4}>
          <Dancer dancerNumber={predictionData.position[1]} currentMove={predictionData.move[1]} />
        </Grid>
        <Grid item xs={4}>
          <Dancer dancerNumber={predictionData.position[2]} currentMove={predictionData.move[2]} />
        </Grid>
        <Grid item xs={6}>
          <SyncDelay syncDelay={predictionData.syncDelay} />
        </Grid>
        <Grid item xs={6}>
          <EMG emg={emgData.emg} />
        </Grid>
      </Grid>
    </Container>
  )
}

export default Overview;