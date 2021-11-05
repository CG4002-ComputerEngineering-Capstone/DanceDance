import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography'

function EMG({emg}) {
  return (
    <Card sx={{ minWidth: 200 }}>
      <CardContent>
        <Typography align="center" variant="h5">
          EMG Data
        </Typography>
        <Typography align="center">
          Root mean square: {emg[0]}
        </Typography>
        <Typography align="center">
          Mean absolute value: {emg[1]}
        </Typography>
        <Typography align="center">
          Zero-crossing rate: {emg[2]}
        </Typography>
      </CardContent>
    </Card>
  )
}

export default EMG;