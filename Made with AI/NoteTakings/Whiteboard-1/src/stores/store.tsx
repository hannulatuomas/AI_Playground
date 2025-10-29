import create from "zustand";
import { Tools } from "react-sketch";

const useStore = create((set: any) => ({
  selectedTool: Tools.Pencil,
  setTool: (tool: Tools) => set((state: any) => ({ selectedTool: tool }))
}));

export default useStore;
