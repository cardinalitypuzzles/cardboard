import React from "react";
import { useTranslation } from "react-i18next";
import Form from "react-bootstrap/Form";
import { SUPPORTED_LANGUAGES } from "./i18n";

export const LanguageSelector = () => {
  const { i18n, t } = useTranslation();
  const rawLang = i18n.resolvedLanguage || i18n.language || "en";
  const currentLang = rawLang.startsWith("zh")
    ? "zh-Hans"
    : rawLang.startsWith("es")
    ? "es"
    : rawLang;

  return (
    <Form.Select
      id="language-select"
      aria-label={t("select-language")}
      value={currentLang}
      onChange={(e) => {
        i18n.changeLanguage(e.target.value);
      }}
      size="sm"
    >
      {SUPPORTED_LANGUAGES.map((lang) => (
        <option key={lang.code} value={lang.code}>
          {lang.name}
        </option>
      ))}
    </Form.Select>
  );
};
