import React from "react";
import { render } from "react-dom";
import { Provider } from "react-redux";
import store from "./store";
import { HuntViewMain } from "./HuntViewMain";
import {useEffect} from "react";

const sendTokenToChromeExtension = ({ extensionId, jwt}) => {
  chrome.runtime.sendMessage(extensionId, { jwt }, response => {
    if (!response.success) {
      console.log('error sending message', response);
      return response;
    }
    console.log('Sucesss ::: ', response.message)
  });
}

const App = () => {
  useEffect(() => {
    sendTokenToChromeExtension({ extensionId: 'kkfnehbkmjbnilgiapifghldidjidjne', jwt: 'xxxxx.yyyyy.zzzzz'})
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
