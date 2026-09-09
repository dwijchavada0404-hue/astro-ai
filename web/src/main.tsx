import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { AnswerLanguageExperience } from "./answer-language";
import { LifeContextOnboarding } from "./life-context-onboarding";
import { NaturalThinkingExperience } from "./natural-thinking-experience";
import "./styles.css";
import "./backup.css";
import "./chart-viewer.css";
import "./reading-progress.css";
import "./answer-language.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <LifeContextOnboarding>
      <AnswerLanguageExperience>
        <NaturalThinkingExperience>
          <App />
        </NaturalThinkingExperience>
      </AnswerLanguageExperience>
    </LifeContextOnboarding>
  </StrictMode>,
);
