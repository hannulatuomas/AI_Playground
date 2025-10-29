import { FormControl, Grid, IconButton, InputLabel } from "@mui/material";
import {
  download,
  redoStep,
  undoStep,
  Whiteboard
} from "./components/whiteboard";
import "./styles.css";
import Select from "@mui/material/Select";
import { Tools } from "react-sketch";
import MenuItem from "@mui/material/MenuItem";
import useStore from "./stores/store";
import UndoIcon from "@mui/icons-material/Undo";
import RedoIcon from "@mui/icons-material/Redo";
import SaveAltIcon from "@mui/icons-material/SaveAlt";

export default function App(): JSX.Element {
  const setTool = useStore((state) => state.setTool);
  const tool: Tools = useStore((state) => state.selectedTool);
  const keys = Object.keys(Tools);

  const undo = () => {
    undoStep();
  };

  const redo = () => {
    redoStep();
  };

  const saveSketch = () => {
    download();
  };

  return (
    <div className="App" style={{ backgroundColor: "grey", padding: "10px" }}>
      <Grid container>
        <Grid item>
          <IconButton onClick={undo}>
            <UndoIcon />
          </IconButton>
          <IconButton onClick={redo}>
            <RedoIcon />
          </IconButton>
          <FormControl variant="standard" sx={{ m: 1, minWidth: 120 }}>
            <InputLabel id="demo-simple-select-standard-label">Tool</InputLabel>
            <Select
              labelId="demo-simple-select-standard-label"
              id="demo-simple-select-standard"
              value={tool}
              onChange={(e) => setTool(e.target.value)}
              label="Tool"
            >
              {keys.map((key) => (
                <MenuItem value={Tools[key]}>{key}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <IconButton onClick={saveSketch}>
            <SaveAltIcon />
          </IconButton>{" "}
          *
        </Grid>
        <Whiteboard />
        <Grid item></Grid>
      </Grid>
    </div>
  );
}
