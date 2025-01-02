/*global chrome*/

import React, {useEffect} from "react";
import { render } from "react-dom";
import { Provider } from "react-redux";
import store from "./store";
import { HuntViewMain } from "./HuntViewMain";

const sendTokenToChromeExtension = ({ extensionId, huntId }) => {
  chrome.runtime.sendMessage(extensionId, { huntId }, response => {
    if (!response.success) {
      console.log('error sending message', response);
      return response;
    }
    console.log('Sucesss ::: ', response.message)
  });
}

const App = () => {
  useEffect(() => {
    sendTokenToChromeExtension({ extensionId: 'fhldkjfidcbfienegpehemncionolmfa', huntId: window.CURRENT_HUNT_ID })
  }, [])
  
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
