import { Card, Container, Dialog, Grid, Typography } from "@mui/material";

function AnalyticsDialog({CloseDialog, data, open}) {
  let dancer1Correct = 0;
  let dancer2Correct = 0;
  let dancer3Correct = 0;
  let positionCorrect = 0;
  const total = data.length;
  data.forEach(e => {
    if (e.move === e.predictedMove[0]) {
      ++dancer1Correct;
    }
    if (e.move === e.predictedMove[1]) {
      ++dancer2Correct;
    }
    if (e.move === e.predictedMove[2]) {
      ++dancer3Correct;
    }
    for (let i = 0; i < 3; ++ i) {
      if (e.position[i] === e.predictedPosition[i]) {
        ++positionCorrect;
      }
    }
  });

  return (
    <Dialog 
      fullWidth={true}
      maxWidth='md'
      onBackdropClick={CloseDialog}
      open={open}
    >
      <Container>
        <Grid container>
          <Grid item xs={3}>
            <Card>
              <Typography align="center">
                Dancer 1 Accuracy
              </Typography>
              <Typography align="center" variant="h5">
                {Math.floor((dancer1Correct * 100)/total)}%
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={3}>
            <Card>
              <Typography align="center">
                Dancer 2 Accuracy
                </Typography>
                <Typography align="center" variant="h5">
                  {Math.floor((dancer2Correct * 100)/total)}%
                </Typography>
            </Card>            
          </Grid>
          <Grid item xs={3}>
            <Card>
              <Typography align="center">
                Dancer 3 Accuracy
              </Typography>
              <Typography align="center" variant="h5">
                {Math.floor((dancer3Correct * 100)/total)}%
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={3}>
            <Card>
              <Typography align="center">
                Position Accuracy
              </Typography>
              <Typography align="center" variant="h5">
                {Math.floor((positionCorrect * 100)/(total * 3))}%
              </Typography>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Dialog>
  );
}

export default AnalyticsDialog;