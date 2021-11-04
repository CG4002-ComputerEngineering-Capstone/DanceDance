import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography'

function EMG({emg}) {
  return (
    <Card sx={{ minWidth: 200 }}>
      <CardContent>
        <Typography align="center" variant="h5">
          EMG (rms | mav | zcr)
        </Typography>
        <Typography align="center" variant="h6">
          {emg[0]} | {emg[1]} | {emg[2]}
        </Typography>
      </CardContent>
    </Card>
  )
}

export default EMG;