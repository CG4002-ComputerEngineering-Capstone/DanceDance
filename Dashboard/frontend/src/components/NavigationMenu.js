import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Toolbar from '@mui/material/Toolbar';
import Analytics from '@mui/icons-material/Analytics';
import PeopleIcon from '@mui/icons-material/People';
import PersonIcon from '@mui/icons-material/Person';
import { Link } from "react-router-dom";

const drawerWidth = 240;

function NavigationMenu() {
  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
      }}
    >
      <Toolbar />
      <Box sx={{ display: 'flex' }}>
        <List>
          <ListItem >
            <ListItemButton component={Link} to={"/Overview"}>
              <ListItemIcon>
                <PeopleIcon />
              </ListItemIcon>
              <ListItemText primary={"Overview"} />
            </ListItemButton>
          </ListItem>
          <ListItem>
            <ListItemButton component={Link} to={"/Sensor"}>
              <ListItemIcon>
                <PersonIcon />
              </ListItemIcon>
              <ListItemText primary={"Sensor"} />
            </ListItemButton>
          </ListItem>
          <ListItem>
            <ListItemButton component={Link} to={"/Analytics"}>
              <ListItemIcon>
                <Analytics />
              </ListItemIcon>
              <ListItemText primary={"Analytics"} />
            </ListItemButton>
          </ListItem>
        </List>  
      </Box>
    </Drawer>
  )
}

export default NavigationMenu;