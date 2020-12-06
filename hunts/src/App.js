import React, { Component } from "react";
import { render } from "react-dom";
import { HuntViewMain } from "./HuntViewMain";

class App extends Component {
  render() {
    return <HuntViewMain huntId={window.CURRENT_HUNT_ID} />;
  }
}

export default App;

const container = document.getElementById("app");
render(<App />, container);
