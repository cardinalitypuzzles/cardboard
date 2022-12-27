import React from "react";
import ReactTimeAgo from "react-time-ago";

function CreationCell({ value }) {
  const date = new Date(Date.parse(value));
  return <ReactTimeAgo date={date} locale="en-US" />;
}

export default CreationCell;
