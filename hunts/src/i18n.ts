import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import en from "./locales/en.json";
import es from "./locales/es.json";
import zhHans from "./locales/zh-hans.json";

export const resources = {
  en: {
    translation: en,
  },
  es: {
    translation: es,
  },
  "zh-Hans": {
    translation: zhHans,
  },
  zh: {
    translation: zhHans,
  },
} as const;

export const SUPPORTED_LANGUAGES = [
  { code: "en", name: "English" },
  { code: "es", name: "Español" },
  { code: "zh-Hans", name: "中文" },
];

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: "en",
    supportedLngs: ["en", "es", "zh-Hans", "zh"],
    nonExplicitSupportedLngs: true,
    keySeparator: false,
    detection: {
      order: ["localStorage", "navigator", "htmlTag"],
      lookupLocalStorage: "cardboard-language",
      caches: ["localStorage"],
    },
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
