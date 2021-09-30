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

  const ToggleUpdate = () => {
    setIsPaused(!isPaused);
  }

  return (
    <Box sx={{ display: 'flex' }}>
      <Router>
        <CssBaseline />
        <NavigationBar
          isPaused={isPaused}
          ToggleUpdate={ToggleUpdate}
        />
        <NavigationMenu />
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          <Switch>
            <Route exact path="/" render={() => {return (<Redirect to="/Overview" />)}} />
            <Route path="/Overview" render={() => <Overview isPaused={isPaused} />} />
            <Route path="/Dancer1" render={() => <Sensor isPaused={isPaused} dancerNum={1} />} />
            <Route path="/Dancer2" render={() => <Sensor isPaused={isPaused} dancerNum={2} />} />
            <Route path="/Dancer3" render={() => <Sensor isPaused={isPaused} dancerNum={3} />} />
            <Route path="/Analytics" render={() => <Analytics />} />
          </Switch>
        </Box>
      </Router>
    </Box>
  )
}

export default Dashboard;