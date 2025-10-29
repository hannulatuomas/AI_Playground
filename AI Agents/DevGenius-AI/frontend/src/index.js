import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";
import { Toaster } from "sonner";

// Global ResizeObserver error suppression
// This is a known issue with many UI libraries and doesn't affect functionality
const debounce = (callback, delay) => {
  let tid;
  return function (...args) {
    const ctx = self;
    tid && clearTimeout(tid);
    tid = setTimeout(() => {
      callback.apply(ctx, args);
    }, delay);
  };
};

const _ = window.ResizeObserver;
window.ResizeObserver = class ResizeObserver extends _ {
  constructor(callback) {
    callback = debounce(callback, 20);
    super(callback);
  }
};

// Also suppress console errors
const consoleError = console.error;
const consoleWarn = console.warn;

console.error = function filterErrors(msg, ...args) {
  const suppressedErrors = [
    'ResizeObserver',
    'ResizeObserver loop',
    'ResizeObserver loop limit exceeded',
    'ResizeObserver loop completed with undelivered notifications',
  ];
  
  if (typeof msg === 'string' && suppressedErrors.some(err => msg.includes(err))) {
    return;
  }
  
  consoleError(msg, ...args);
};

console.warn = function filterWarnings(msg, ...args) {
  const suppressedWarnings = ['ResizeObserver'];
  
  if (typeof msg === 'string' && suppressedWarnings.some(warn => msg.includes(warn))) {
    return;
  }
  
  consoleWarn(msg, ...args);
};

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
    <Toaster position="top-right" richColors />
  </React.StrictMode>,
);
