import React, { useState } from 'react';
import Box from '@mui/material/Box';
import CssBaseline from '@mui/material/CssBaseline';
import Toolbar from '@mui/material/Toolbar';

import {
  BrowserRouter as Router,
  Redirect,
  Route,
  Switch
} from "react-router-dom";

import Analytics from './Analytics';
import NavigationBar from './NavigationBar';
import NavigationMenu from './NavigationMenu';
import Overview from './Overview';
import Sensor from './Sensor';

function Dashboard() {
  const [isPaused, setIsPaused] = useState(true);

  const TogglePaused = () => {
    setIsPaused(!isPaused);
  }

  return (
    <Box sx={{ display: 'flex' }}>
      <Router>
        <CssBaseline />
        <NavigationBar
          isPaused={isPaused}
          TogglePaused={TogglePaused}
        />
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          <Switch>
            <Route exact path="/" render={() => {return (<Redirect to="/Overview" />)}} />
            <Route path="/Overview" render={() => <Overview isPaused={isPaused} />} />
            <Route path="/Sensor" render={() => <Sensor isPaused={isPaused} />} />
            <Route path="/Analytics" render={() => <Analytics />} />
          </Switch>
        </Box>
        <NavigationMenu />
      </Router>
    </Box>
  )
}

export default Dashboard;