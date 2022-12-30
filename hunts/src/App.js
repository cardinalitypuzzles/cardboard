import React from "react";
import { render } from "react-dom";
import { Provider } from "react-redux";
import store from "./store";
import { HuntViewMain } from "./HuntViewMain";

const App = () => {
  return <HuntViewMain huntId={window.CURRENT_HUNT_ID} />;
};

export default App;

const container = document.getElementById("app");
render(
  <Provider store={store}>
    <App />
  </Provider>,
  container
);
