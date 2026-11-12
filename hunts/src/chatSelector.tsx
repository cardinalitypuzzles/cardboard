import React from "react";
import { useTranslation } from "react-i18next";

import { useStore } from "./store";
import { CHAT_VERSION_OPTIONS } from "./chatSlice";

export const ChatVersionSelector = () => {
  const { version, setChatVersion } = useStore((state) => state.chatSlice);
  const { t } = useTranslation();

  return (
    <div className="">
      <div>{t("chat-version")}</div>
      <div className="form-check">
        <input
          className="form-check-input"
          id="chat-version-app-radio"
          type="radio"
          checked={version === CHAT_VERSION_OPTIONS.APP}
          onChange={(evt) => {
            if (evt.target.checked) {
              setChatVersion(CHAT_VERSION_OPTIONS.APP);
            }
          }}
        />
        <label htmlFor="chat-version-app-radio" className="form-check-label">
          {t("app")}
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
              setChatVersion(CHAT_VERSION_OPTIONS.WEB);
            }
          }}
        />
        <label htmlFor="chat-version-web-radio" className="form-check-label">
          {t("web")}
        </label>
      </div>
    </div>
  );
};
