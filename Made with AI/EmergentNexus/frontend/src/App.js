import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { WorkspaceProvider } from "./contexts/WorkspaceContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import Layout from "./components/Layout";
import "@/App.css";

function App() {
  return (
    <div className="App">
      <ThemeProvider>
        <WorkspaceProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/*" element={<Layout />} />
            </Routes>
          </BrowserRouter>
          <Toaster />
        </WorkspaceProvider>
      </ThemeProvider>
    </div>
  );
}

export default App;