import React, { Component } from "react";
import { render } from "react-dom";

class App extends Component {
    render() {
        return (
            <b>Hello, world!</b>
        );
    }
}

export default App;

const container = document.getElementById("app");
render(<App />, container);
