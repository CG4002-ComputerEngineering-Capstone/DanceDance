import { useState } from 'react';
import { Link } from "react-router-dom";

import BottomNavigation from '@mui/material/BottomNavigation';
import BottomNavigationAction from '@mui/material/BottomNavigationAction';
import Paper from '@mui/material/Paper';

import Analytics from '@mui/icons-material/Analytics';
import PeopleIcon from '@mui/icons-material/People';
import Sensors from '@mui/icons-material/Sensors';



function NavigationMenu() {
  const [value, setValue] = useState(0);

  return (
    <Paper sx={{ position: 'fixed', bottom: 0, left: 0, right: 0 }} elevation={3}>
      <BottomNavigation
        showLabels
        value={value}
        onChange={(event, newValue) => {
          setValue(newValue);
        }}
      >
        <BottomNavigationAction component={Link} to={"/Overview"} label="Overview" icon={<PeopleIcon />} />
        <BottomNavigationAction component={Link} to={"/Sensor"} label="Sensor" icon={<Sensors />} />
        <BottomNavigationAction component={Link} to={"/Analytics"} label="Analytics" icon={<Analytics />} />
      </BottomNavigation>
    </Paper>
  )
}

export default NavigationMenu;