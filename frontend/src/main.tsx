import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { useThemeStore } from "./stores/themeStore";
import "./index.css";

function Root() {
  const theme = useThemeStore((s) => s.theme);

  React.useEffect(() => {
    if (theme === "light") {
      document.documentElement.classList.add("light");
    } else {
      document.documentElement.classList.remove("light");
    }
  }, [theme]);

  return <App />;
}

ReactDOM.createRoot(document.getElementById("root")!).render(<Root />);
