import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography'

function Fatigue({emg}) {
  return (
    <Card sx={{ minWidth: 200 }}>
      <CardContent>
        <Typography align="center" variant="h5">
          Estimated Fatigue
        </Typography>
        <Typography align="center" variant="h6">
          {(50 - emg[2]) * 2}%
        </Typography>
      </CardContent>
    </Card>
  )
}

export default Fatigue;