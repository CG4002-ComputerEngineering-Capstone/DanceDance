import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography'

function EMG({emg}) {
  return (
    <Card sx={{ minWidth: 200 }}>
      <CardContent>
        <Typography align="center">
          EMG
        </Typography>
        <Typography align="center" variant="h5">
          Amp 1: {emg[0]}
        </Typography>
        <Typography align="center" variant="h5">
          Amp 2: {emg[1]}
        </Typography>
        <Typography align="center" variant="h5">
          {emg[2]}mV
        </Typography>
      </CardContent>
    </Card>
  )
}

export default EMG;