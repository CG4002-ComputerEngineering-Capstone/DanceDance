import React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Person from '@mui/icons-material/Person';

function Dancer({dancerNumber, currentMove}) {
  return (
    <Card sx={{ minWidth: 200 }}>
        <CardContent>
          <Person style={{fill: dancerNumber === 1 ? "red" : (dancerNumber === 2 ? 'green' : 'blue')}} /> 
          <Typography align="center">
            Dancer {dancerNumber}
          </Typography>
          <Typography align="center" variant="h5">
            {currentMove === '' ? "-" : currentMove}
          </Typography>
        </CardContent>
    </Card>
  )
}

export default Dancer;