import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography'

function SyncDelay({syncDelay}) {
  return (
    <Card sx={{ minWidth: 200 }}>
      <CardContent>
        <Typography align="center" variant="h5">
          Sync Delay
        </Typography>
        <Typography align="center" variant="h6">
          {syncDelay}ms
        </Typography>
      </CardContent>
    </Card>
  )
}

export default SyncDelay;