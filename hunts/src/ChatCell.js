import React from "react";
import { useSelector } from "react-redux";
import { CHAT_PLATFORM } from "./constants";
import { getChatVersion, CHAT_VERSION_OPTIONS } from "./chatSlice";

export default function ChatCell({ row, value }) {
  const version = useSelector(getChatVersion);
  return (
    <>
      {row.original.chat_room &&
      row.original.chat_room.text_channel_url.length > 0 ? (
        <a
          href={
            version == CHAT_VERSION_OPTIONS.APP
              ? row.original.chat_room.text_channel_url.replace(
                  "https",
                  CHAT_PLATFORM
                )
              : row.original.chat_room.text_channel_url
          }
          target="_blank"
        >
          Channel
        </a>
      ) : null}
    </>
  );
}
