import "regenerator-runtime/runtime";
import React from "react";
import { createRoot } from "react-dom/client";
import TimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en.json";

import App from "./App";

TimeAgo.addLocale(en);

const container = document.getElementById("app")!;
const root = createRoot(container);
root.render(<App />);
