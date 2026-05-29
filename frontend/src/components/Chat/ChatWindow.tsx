import { useRef, useEffect, useCallback } from "react";
import { useChatStore } from "../../stores/chatStore";
import { streamChat } from "../../utils/api";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";
import { IoBarChartOutline } from "react-icons/io5";

export default function ChatWindow() {
  const conversations = useChatStore((s) => s.conversations);
  const activeId = useChatStore((s) => s.activeConversationId);
  const isStreaming = useChatStore((s) => s.isStreaming);
  const createConversation = useChatStore((s) => s.createConversation);
  const addMessage = useChatStore((s) => s.addMessage);
  const appendToLastAssistant = useChatStore((s) => s.appendToLastAssistantMessage);
  const setStreaming = useChatStore((s) => s.setStreaming);
  const bottomRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const activeConv = conversations.find((c) => c.id === activeId);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [activeConv?.messages]);

  const handleSend = useCallback(async (text: string) => {
    let convId = activeId; if (!convId) convId = createConversation();
    addMessage(convId, { id: Math.random().toString(36).substring(2, 10), role: "user", content: text, timestamp: Date.now() });
    addMessage(convId, { id: Math.random().toString(36).substring(2, 10), role: "assistant", content: "", timestamp: Date.now() });
    setStreaming(true);
    try {
      const conv = useChatStore.getState().conversations.find((c) => c.id === convId);
      const msgs = (conv?.messages || []).filter((m) => m.content).map((m) => ({ role: m.role, content: m.content }));
      let acc = ""; let last = Date.now();
      for await (const chunk of streamChat(msgs)) {
        acc += chunk;
        if (Date.now() - last > 80) { appendToLastAssistant(convId, acc); acc = ""; last = Date.now(); }
      }
      if (acc) appendToLastAssistant(convId, acc);
    } catch (err) {
      appendToLastAssistant(convId, `\n\n> 错误: ${err instanceof Error ? err.message : "请求失败"}`);
    } finally { setStreaming(false); }
  }, [activeId, createConversation, addMessage, appendToLastAssistant, setStreaming]);

  return (
    <div className="flex-1 flex flex-col min-w-0 min-h-0 relative">
      {!activeConv ? (
        <div className="flex-1 flex items-center justify-center" style={{paddingBottom:"12%"}}>
          <div className="text-center" style={{width:"100%", maxWidth:760, padding:"0 32px"}}>
            <div style={{marginBottom:32}}>
              <div style={{
                width:48, height:48, borderRadius:12,
                background:"var(--bg-surface-hover)",
                display:"flex", alignItems:"center", justifyContent:"center",
                margin:"0 auto",
              }}>
                <IoBarChartOutline size={24} style={{color:"var(--text-tertiary)"}} />
              </div>
            </div>

            <h1 style={{
              fontSize:42, fontWeight:650, color:"var(--text-primary)",
              lineHeight:1.1, letterSpacing:-0.5, marginBottom:12,
            }}>
              今天想分析哪支股票？
            </h1>

            <p style={{
              fontSize:15, color:"var(--text-secondary)", marginBottom:0,
            }}>
              输入股票代码或问题，获取智能分析
            </p>
          </div>
        </div>
      ) : (
        <div ref={scrollContainerRef} className="flex-1 overflow-y-auto">
          <div style={{maxWidth:760, margin:"0 auto", padding:"24px 32px"}} className="space-y-8">
            {activeConv.messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)}
            {isStreaming && (
              <div className="flex items-center gap-1.5 py-1">
                <span className="w-2 h-2 rounded-full animate-bounce" style={{background:"var(--text-muted)",animationDuration:"0.6s"}} />
                <span className="w-2 h-2 rounded-full animate-bounce" style={{background:"var(--text-muted)",animationDuration:"0.6s",animationDelay:"0.15s"}} />
                <span className="w-2 h-2 rounded-full animate-bounce" style={{background:"var(--text-muted)",animationDuration:"0.6s",animationDelay:"0.3s"}} />
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>
      )}
      <ChatInput onSend={handleSend} disabled={isStreaming} />
    </div>
  );
}
