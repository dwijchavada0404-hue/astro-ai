import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { LifeContextOnboarding } from "./life-context-onboarding";
import "./styles.css";
import "./backup.css";
import "./chart-viewer.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <LifeContextOnboarding>
      <App />
    </LifeContextOnboarding>
  </StrictMode>,
);
