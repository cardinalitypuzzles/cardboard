import React, { useEffect } from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import store from "./store";
import { HuntViewMain } from "./HuntViewMain";

const sendTokenToChromeExtension = ({
  extensionId,
  huntId,
}: {
  extensionId: string;
  huntId: string;
}) => {
  // @ts-expect-error
  if (typeof chrome !== "undefined" && chrome && chrome.runtime) {
    // @ts-expect-error
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
      huntId: CURRENT_HUNT_ID.toString(),
    });
  }, []);

  return <HuntViewMain huntId={CURRENT_HUNT_ID} />;
};

export default App;
