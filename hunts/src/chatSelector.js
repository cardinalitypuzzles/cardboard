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
    <div className="">
      <div>Chat Version</div>
      <div className="form-check">
        <input
          className="form-check-input"
          id="chat-version-app-radio"
          type="radio"
          checked={version === CHAT_VERSION_OPTIONS.APP}
          onChange={(evt) => {
            if (evt.target.checked) {
              dispatch(updateChatVersion(CHAT_VERSION_OPTIONS.APP));
            }
          }}
        />
        <label htmlFor="chat-version-app-radio" className="form-check-label">
          App
        </label>
      </div>
      <div className="form-check">
        <input
          className="form-check-input"
          id="chat-version-web-radio"
          type="radio"
          checked={version === CHAT_VERSION_OPTIONS.WEB}
          onChange={(evt) => {
            if (evt.target.checked) {
              dispatch(updateChatVersion(CHAT_VERSION_OPTIONS.WEB));
            }
          }}
        />
        <label htmlFor="chat-version-web-radio" className="form-check-label">
          Web
        </label>
      </div>
    </div>
  );
};
