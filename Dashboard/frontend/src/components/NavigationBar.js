import AppBar from '@mui/material/AppBar';
import Button from '@mui/material/Button';
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography';

function NavigationBar({isPaused, TogglePaused}) {
  async function ResetDatabase() {
    const response = await fetch("https://ap-southeast-1.aws.webhooks.mongodb-realm.com/api/client/v2.0/app/cg4002-nkzcm/service/CG4002/incoming_webhook/ResetDatabase", {method: 'DELETE'});
    console.log(response);
    return;
  }

  return (
    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1}}>
      <Toolbar>
        <Typography variant="h5" style={{ flex: 1 }}>
          CG4002 Team 12
        </Typography>
        <Button
          variant="contained"
          onClick={TogglePaused}
        >
          {
            isPaused === true ? "Start" : "Stop"
          }
        </Button>
        <Button
          variant="contained"
          onClick={ResetDatabase}
        >
          Reset Database
        </Button>
      </Toolbar>
    </AppBar>
  )
}

export default NavigationBar;