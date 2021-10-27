import React, { useEffect, useState } from "react";
import Alert from "@mui/material/Alert";
import Collapse from "@mui/material/Collapse";
import Container from '@mui/material/Container';
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";

import Dancer from "./Dancer";
import EMG from "./EMG";
import SyncDelay from "./SyncDelay";

const defaultPredictionData = {
  move: ["-", "-", "-"],
  position: [1, 2, 3],
  syncDelay: 0,
  emg: [0, 0, 0]
}

function Overview({isPaused}) {
  const [predictionData, setPredictionData] = useState(defaultPredictionData);
  const [flag, setFlag] = useState("");
  const [open, setOpen] = useState(false);

  async function GetPrediction() {
    const response = await fetch("https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/GetPrediction");
    if (response.status >= 200 && response.status <= 299) {
      const data = await response.json();
      if (data) {
        try {
          setPredictionData(
            {
              move: data.move,
              position: JSON.parse(data.position),
              syncDelay: JSON.parse(data.syncDelay),
              emg: JSON.parse(data.emg)
            }
          );
          console.log("Prediction update");
          if (data.flag !== "") {
            setFlag(data.flag);
            setOpen(true);
          }
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

  useEffect(() => {
    setTimeout(() => {
      setOpen(false);
    }, 2500);
  }, [open]);

  useEffect(() => {
    let interval = null;
    if (isPaused) {
      clearInterval(interval);
    } else {
      interval = setInterval(() => {
        GetPrediction();
      }, 500);
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
          <Dancer dancerNumber={predictionData.position[0]} currentMove={predictionData.move[predictionData.position[0] - 1]} />
        </Grid>
        <Grid item xs={4}>
          <Dancer dancerNumber={predictionData.position[1]} currentMove={predictionData.move[predictionData.position[1] - 1]} />
        </Grid>
        <Grid item xs={4}>
          <Dancer dancerNumber={predictionData.position[2]} currentMove={predictionData.move[predictionData.position[2] - 1]} />
        </Grid>
        <Grid item xs={6}>
          <SyncDelay syncDelay={predictionData.syncDelay} />
        </Grid>
        <Grid item xs={6}>
          <EMG emg={predictionData.emg} />
        </Grid>
      </Grid>
      <Collapse in={open}>
        <div>
          <Alert severity="info">{flag}</Alert>
        </div>
      </Collapse>
    </Container>
  )
}

export default Overview;