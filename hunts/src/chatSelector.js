import React from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  getChatVersion,
  CHAT_VERSION_OPTIONS,
  updateChatVersion,
} from "./chatSlice";

export const ChatVersionSelector = () => {
  const version = useSelector(getChatVersion);
  const dispatch = useDispatch();
  return (
    <>
      <span>Chat Version:</span>
      <label>
        <input
          style={{ margin: "0 5px 0 10px" }}
          type="radio"
          checked={version === CHAT_VERSION_OPTIONS.APP}
          onChange={(evt) => {
            if (evt.target.checked) {
              dispatch(updateChatVersion(CHAT_VERSION_OPTIONS.APP));
            }
          }}
        ></input>
        App
      </label>
      <label>
        <input
          style={{ margin: "0 5px 0 10px" }}
          type="radio"
          checked={version === CHAT_VERSION_OPTIONS.WEB}
          onChange={(evt) => {
            if (evt.target.checked) {
              dispatch(updateChatVersion(CHAT_VERSION_OPTIONS.WEB));
            }
          }}
        ></input>
        Web
      </label>
    </>
  );
};
