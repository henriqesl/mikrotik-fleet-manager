import {
  useMemo,
  useState,
} from "react";

import { I18nContext } from "./context";
import { messages } from "./messages";


const DEFAULT_LANGUAGE = "pt-BR";
const STORAGE_KEY = "argos-language";


function getInitialLanguage() {
  const storedLanguage =
    localStorage.getItem(STORAGE_KEY);

  return storedLanguage === "en"
    ? "en"
    : DEFAULT_LANGUAGE;
}


export function I18nProvider({ children }) {
  const [language, setLanguageState] = useState(
    getInitialLanguage,
  );

  function setLanguage(nextLanguage) {
    const normalizedLanguage =
      nextLanguage === "en"
        ? "en"
        : DEFAULT_LANGUAGE;

    localStorage.setItem(
      STORAGE_KEY,
      normalizedLanguage,
    );

    setLanguageState(normalizedLanguage);
  }

  const value = useMemo(() => {
    function t(key) {
      return (
        messages[language]?.[key]
        ?? messages[DEFAULT_LANGUAGE]?.[key]
        ?? key
      );
    }

    return {
      language,
      locale:
        language === "en"
          ? "en-US"
          : "pt-BR",
      setLanguage,
      t,
    };
  }, [language]);

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
}