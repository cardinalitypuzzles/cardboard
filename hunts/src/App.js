import React, { useEffect } from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import store from "./store";
import { HuntViewMain } from "./HuntViewMain";

const sendTokenToChromeExtension = ({ extensionId, huntId }) => {
  if (typeof chrome !== "undefined" && chrome && chrome.runtime) {
    chrome.runtime.sendMessage(extensionId, { huntId }, (response) => {
      if (!response.success) {
        console.log("Error sending message: ", response);
        return response;
      }
    });
  }
};

const App = () => {
  useEffect(() => {
    sendTokenToChromeExtension({
      extensionId: "fhldkjfidcbfienegpehemncionolmfa",
      huntId: window.CURRENT_HUNT_ID,
    });
  }, []);

  return <HuntViewMain huntId={window.CURRENT_HUNT_ID} />;
};

export default App;

const container = document.getElementById("app");
const root = createRoot(container);
root.render(
  <Provider store={store}>
    <App />
  </Provider>
);
