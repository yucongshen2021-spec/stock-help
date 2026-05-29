import type { Message } from "../../stores/chatStore";
import MarkdownRenderer from "./MarkdownRenderer";

export default function MessageBubble({ message }: { message: Message }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div style={{
          maxWidth:"75%", borderRadius:16, padding:"14px 18px",
          background:"var(--bg-user-bubble)",
        }}>
          <p style={{fontSize:16, lineHeight:1.6, whiteSpace:"pre-wrap", color:"var(--text-primary)"}}>
            {message.content}
          </p>
        </div>
      </div>
    );
  }
  if (!message.content) return null;
  return <MarkdownRenderer content={message.content} />;
}
