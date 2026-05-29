import { useEffect } from "react";
import AppLayout from "./components/Layout/AppLayout";
import ChatWindow from "./components/Chat/ChatWindow";
import StockPanel from "./components/Stock/StockPanel";
import { runtimePing, runtimeShutdown } from "./utils/api";

export default function App() {
  useEffect(() => {
    void runtimePing().catch(() => undefined);
    const timer = setInterval(() => {
      void runtimePing().catch(() => undefined);
    }, 15000);

    const onBeforeUnload = () => {
      runtimeShutdown();
    };
    window.addEventListener("beforeunload", onBeforeUnload);

    return () => {
      clearInterval(timer);
      window.removeEventListener("beforeunload", onBeforeUnload);
    };
  }, []);

  return (
    <AppLayout rightPanel={<StockPanel />}>
      <ChatWindow />
    </AppLayout>
  );
}
