import { useState } from 'react';
import { Link } from "react-router-dom";

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

const drawerWidth = 240;

function NavigationMenu() {
  const [selectedIndex, setSelectedIndex] = useState(1);

  const handleListItemClick = (event, index) => {
    setSelectedIndex(index);
  }

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
      <Box sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}>
        <List component="nav">
          <ListItem disablePadding>
            <ListItemButton
              selected={selectedIndex === 0}
              onClick={(event) => handleListItemClick(event, 0)}
              component={Link}
              to={"/Overview"}
            >
              <ListItemIcon>
                <PeopleIcon />
              </ListItemIcon>
              <ListItemText primary={"Overview"} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton
              selected={selectedIndex === 1}
              onClick={(event) => handleListItemClick(event, 1)}
              component={Link}
              to={"/Sensor"}
            >
              <ListItemIcon>
                <PersonIcon />
              </ListItemIcon>
              <ListItemText primary={"Sensor"} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton
              selected={selectedIndex === 2}
              onClick={(event) => handleListItemClick(event, 2)}
              component={Link}
              to={"/Analytics"}
            >
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