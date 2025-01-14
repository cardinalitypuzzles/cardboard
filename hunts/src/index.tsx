import "regenerator-runtime/runtime";
import React from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import TimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en.json";

import App from "./App";
import store from "./store";

TimeAgo.addLocale(en);

const container = document.getElementById("app")!;
const root = createRoot(container);
root.render(
  <Provider store={store}>
    <App />
  </Provider>
);
