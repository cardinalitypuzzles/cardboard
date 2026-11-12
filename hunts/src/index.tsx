import "regenerator-runtime/runtime";
import React from "react";
import { createRoot } from "react-dom/client";
import TimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en.json";
import es from "javascript-time-ago/locale/es.json";
import zh from "javascript-time-ago/locale/zh.json";

import "./i18n";
import App from "./App";

TimeAgo.addLocale(en);
TimeAgo.addLocale(es);
TimeAgo.addLocale(zh);

const container = document.getElementById("app")!;
const root = createRoot(container);
root.render(<App />);
