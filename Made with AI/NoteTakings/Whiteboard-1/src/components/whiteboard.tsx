import { ReactElement, useState } from "react";
import { SketchField, Tools } from "react-sketch";
import useStore from "../stores/store";

var sketch: SketchField;

export function Whiteboard(props: {}): ReactElement {
  const [value] = useState<any>();
  const tool: Tools = useStore((state) => state.selectedTool);

  return (
    <SketchField
      ref={(c: SketchField) => (sketch = c)}
      value={value}
      width="1200px"
      height="800px"
      tool={tool}
      lineColor="black"
      lineWidth={3}
      undoSteps={20}
      backgroundColor="white"
      imageFormat="png"
      border
    />
  );
}

export const undoStep = () => {
  if (sketch) {
    sketch.undo();
  }
};

export const redoStep = () => {
  if (sketch) {
    sketch.redo();
  }
};

export const download = () => {
  if (sketch) {
    console.log("sketch", sketch.toJSON());
    // let link = document.createElement("a");
    // link.href = sketch.toDataURL();
    // link.download = "toPNG.png";
    // link.click();
  }
};
