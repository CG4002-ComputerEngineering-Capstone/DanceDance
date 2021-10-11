import React, { useEffect, useState } from "react";
import Container from '@mui/material/Container';
import Grid from "@mui/material/Grid"

import Dancer from "./Dancer";
import EMG from "./EMG";
import SyncDelay from "./SyncDelay";
import { Typography } from "@mui/material";

const defaultPredictionData = [
  {
    position: [1, 2, 3],
    move: ["-", "-", "-"],
    syncDelay: 0
  }
];

const defaultEMGData = {
  emg: 0
}

function Overview({isPaused}) {
  const [predictionData, setPredictionData] = useState(defaultPredictionData);
  const [emgData, setEMGData] = useState(defaultEMGData);

  async function GetPrediction() {
    console.log("Prediction update");
    const response = await fetch("https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/GetPrediction");
    if (response.status >= 200 && response.status <= 299) {
      const data = await response.json();
      if (data.length > 0) {
        const formatted = [];
        data.forEach(element =>
          formatted.push(
            {
              position: JSON.parse(element.position),
              move: element.move,
              syncDelay: JSON.parse(element.syncDelay)
            }
          )
        );
        setPredictionData(formatted);
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
        setEMGData(
          {
            emg: data.emg
          }
        );
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
    let interval = null;
    if (isPaused) {
      clearInterval(interval);
    } else {
      interval = setInterval(() => {
        GetPrediction();
        GetEMG();
      }, 2000);
    }
    return () => {
      clearInterval(interval);
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
          <Dancer dancerNumber={predictionData[predictionData.length - 1].position[0]} currentMove={predictionData[predictionData.length - 1].move[0]} />
        </Grid>
        <Grid item xs={4}>
          <Dancer dancerNumber={predictionData[predictionData.length - 1].position[1]} currentMove={predictionData[predictionData.length - 1].move[1]} />
        </Grid>
        <Grid item xs={4}>
          <Dancer dancerNumber={predictionData[predictionData.length - 1].position[2]} currentMove={predictionData[predictionData.length - 1].move[2]} />
        </Grid>
        <Grid item xs={6}>
          <SyncDelay syncDelay={predictionData[predictionData.length - 1].syncDelay} />
        </Grid>
        <Grid item xs={6}>
          <EMG emg={emgData.emg} />
        </Grid>
      </Grid>
    </Container>
  )
}

export default Overview;