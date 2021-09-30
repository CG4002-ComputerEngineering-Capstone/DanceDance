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
          {emg}mV
        </Typography>
      </CardContent>
    </Card>
  )
}

export default EMG;