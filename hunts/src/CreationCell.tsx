import React from "react";

import { SafeReactTimeAgo } from "./types";

function CreationCell({ value }: { value: string }) {
  const date = new Date(Date.parse(value));
  return <SafeReactTimeAgo date={date} locale="en-US" />;
}

export default CreationCell;
