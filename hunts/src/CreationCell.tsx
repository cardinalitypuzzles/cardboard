import React from "react";
import ReactTimeAgo from "react-time-ago";
import { useTranslation } from "react-i18next";

function CreationCell({ value }: { value: string }) {
  const { i18n } = useTranslation();
  const date = new Date(Date.parse(value));
  const currentLocale = i18n.resolvedLanguage || "en-US";
  return <ReactTimeAgo date={date} locale={currentLocale} />;
}

export default CreationCell;
