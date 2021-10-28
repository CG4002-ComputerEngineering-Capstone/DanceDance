import { useState } from "react";
import { Container, IconButton, MenuItem, Paper, Select, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";
import { Add, Delete, Insights } from "@mui/icons-material";
import AnalyticsDialog from "./AnalyticsDialog";

const possibleMoves = [
  "cowboy",
  "dab",
  "jamesbond",
  "mermaid",
  "pushback",
  "scarecrow",
  "snake",
  "window360"
];

const possiblePositions = [
  "123",
  "132",
  "213",
  "231",
  "312",
  "321"
]

const defaultEntry = {
  move: possibleMoves[0],
  position: possiblePositions[0],
  predictedMove: [possibleMoves[0], possibleMoves[0], possibleMoves[0]],
  predictedPosition: possiblePositions[0]
}

function Analytics() {
  const [entry, setEntry] = useState(defaultEntry);
  const [data, setData] = useState([]);
  const [open, setOpen] = useState(false);

  const handleFileChange = e => {
    const fileReader = new FileReader();
    try {
      fileReader.readAsText(e.target.files[0], "UTF-8");
      fileReader.onload = e => {
        setData(JSON.parse(e.target.result));
      };
    } catch (err) {
      console.log(err)
    }

  }

  const GetCurrentEntry = () => {
    return {
      move: entry.move,
      position: entry.position,
      predictedMove: entry.predictedMove,
      predictedPosition: entry.predictedPosition
    };
  } 

  const ChangeMove = (event) => {
    let updatedEntry = GetCurrentEntry();
    updatedEntry.move = event.target.value;
    setEntry(updatedEntry);
  }

  const ChangePosition = (event) => {
    let updatedEntry = GetCurrentEntry();
    updatedEntry.position = event.target.value;
    setEntry(updatedEntry);
  }

  const ChangeDancer1Move = (event) => {
    let updatedEntry = GetCurrentEntry();
    updatedEntry.predictedMove[0] = event.target.value;
    setEntry(updatedEntry);
  }

  const ChangeDancer2Move = (event) => {
    let updatedEntry = GetCurrentEntry();
    updatedEntry.predictedMove[1] = event.target.value;
    setEntry(updatedEntry);
  }

  const ChangeDancer3Move = (event) => {
    let updatedEntry = GetCurrentEntry();
    updatedEntry.predictedMove[2] = event.target.value;
    setEntry(updatedEntry);
  }

  const ChangePredictedPosition = (event) => {
    let updatedEntry = GetCurrentEntry();
    updatedEntry.predictedPosition = event.target.value;
    setEntry(updatedEntry);
  }

  const AddEntry = () => {
    const newData = {
      id: new Date().getTime(),
      move: entry.move,
      position: entry.position,
      predictedMove: entry.predictedMove,
      predictedPosition: entry.predictedPosition
    }
    setData(data => [...data, newData])
  }

  const OpenDialog = () => {
    if (data.length > 0) {
      setOpen(true);
    }

  }

  const CloseDialog = () => {
    setOpen(false);
  }

  const DeleteEntry = (id) => {
    setData(data.filter(element => element.id !== id));
  }

  return (
    <Container>
      <input type="file" onChange={handleFileChange} />
      <AnalyticsDialog CloseDialog={CloseDialog} data={data} open={open} />
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>Move</TableCell>
              <TableCell>Position</TableCell>
              <TableCell>Dancer 1 Move</TableCell>
              <TableCell>Dancer 2 Move</TableCell>
              <TableCell>Dancer 3 Move</TableCell>
              <TableCell>Predicted Position</TableCell>
              <TableCell><IconButton onClick={OpenDialog}><Insights></Insights></IconButton></TableCell>
              
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map(element =>
              <TableRow key={element.id}>
                <TableCell>{element.move}</TableCell>
                <TableCell>{element.position}</TableCell>
                <TableCell>{element.predictedMove[0]}</TableCell>
                <TableCell>{element.predictedMove[1]}</TableCell>
                <TableCell>{element.predictedMove[2]}</TableCell>
                <TableCell>{element.predictedPosition}</TableCell>
                <TableCell>
                  <IconButton onClick={() => DeleteEntry(element.id)}>
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            )}
            <TableRow>
              <TableCell>
                <Select
                  variant="standard"
                  onChange={ChangeMove}
                  value={entry.move}
                >
                  {possibleMoves.map(element =>
                    <MenuItem key={element} value={element}>{element}</MenuItem>
                  )}
                </Select>
              </TableCell>
              <TableCell>
                <Select
                  variant="standard"
                  onChange={ChangePosition}
                  value={entry.position}
                >
                  {possiblePositions.map(element => 
                    <MenuItem key={element} value={element}>{element}</MenuItem>
                  )}
                </Select>
              </TableCell>
              <TableCell>
                <Select
                  variant="standard"
                  onChange={ChangeDancer1Move}
                  value={entry.predictedMove[0]}
                >
                  {possibleMoves.map(element =>
                    <MenuItem key={element} value={element}>{element}</MenuItem>
                  )}
                </Select>
              </TableCell>
              <TableCell>
                <Select
                  variant="standard"
                  onChange={ChangeDancer2Move}
                  value={entry.predictedMove[1]}
                >
                  {possibleMoves.map(element =>
                    <MenuItem key={element} value={element}>{element}</MenuItem>
                  )}
                </Select>
              </TableCell>
              <TableCell>
                <Select
                  variant="standard"
                  onChange={ChangeDancer3Move}
                  value={entry.predictedMove[2]}
                >
                  {possibleMoves.map(element =>
                    <MenuItem key={element} value={element}>{element}</MenuItem>
                  )}
                </Select>
              </TableCell>
              <TableCell>
                <Select
                  variant="standard"
                  onChange={ChangePredictedPosition}
                  value={entry.predictedPosition}
                >
                  {possiblePositions.map(element => 
                    <MenuItem key={element} value={element}>{element}</MenuItem>
                  )}
                </Select>
              </TableCell>
              <TableCell>
                <IconButton onClick={AddEntry}>
                  <Add />
                </IconButton>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  )
}

export default Analytics;