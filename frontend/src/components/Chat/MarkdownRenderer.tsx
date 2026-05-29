import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function MarkdownRenderer({ content }: { content: string }) {
  return (
    <div style={{lineHeight:1.6, color:"var(--text-primary)"}}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={{
        h1: ({ children }) => <h1 style={{fontSize:22,fontWeight:600,color:"var(--text-primary)",marginTop:24,marginBottom:12,letterSpacing:-0.3}}>{children}</h1>,
        h2: ({ children }) => <h2 style={{fontSize:19,fontWeight:600,color:"var(--text-primary)",marginTop:20,marginBottom:10,letterSpacing:-0.2}}>{children}</h2>,
        h3: ({ children }) => <h3 style={{fontSize:17,fontWeight:600,color:"var(--text-primary)",marginTop:16,marginBottom:8}}>{children}</h3>,
        p: ({ children }) => <p style={{marginBottom:12,fontSize:16,lineHeight:1.6}}>{children}</p>,
        ul: ({ children }) => <ul style={{listStyle:"disc",paddingLeft:20,marginBottom:12}}>{children}</ul>,
        ol: ({ children }) => <ol style={{listStyle:"decimal",paddingLeft:20,marginBottom:12}}>{children}</ol>,
        li: ({ children }) => <li style={{fontSize:16,lineHeight:1.6,paddingLeft:2}}>{children}</li>,
        strong: ({ children }) => <strong style={{fontWeight:600,color:"var(--text-primary)"}}>{children}</strong>,
        a: ({ href, children }) => <a href={href} style={{color:"var(--color-link)"}} target="_blank" rel="noopener noreferrer">{children}</a>,
        code: ({ className, children }) => {
          if (className?.includes("language-")) return (
            <pre style={{borderRadius:14,margin:"12px 0",overflowX:"auto",background:"var(--bg-code)",border:"1px solid var(--border-card)"}}>
              <code className={className} style={{fontSize:14,display:"block",padding:"14px 16px"}}>{children}</code>
            </pre>
          );
          return <code style={{padding:"2px 6px",borderRadius:6,fontSize:14,background:"var(--bg-icon)"}}>{children}</code>;
        },
        table: ({ children }) => <div style={{overflowX:"auto",margin:"12px 0",borderRadius:14,border:"1px solid var(--border-card)"}}><table style={{width:"100%",fontSize:14}}>{children}</table></div>,
        th: ({ children }) => <th style={{padding:"10px 16px",textAlign:"left",fontWeight:600,borderBottom:"1px solid var(--border-card)",color:"var(--text-primary)",background:"var(--bg-surface)"}}>{children}</th>,
        td: ({ children }) => <td style={{padding:"10px 16px",borderBottom:"1px solid var(--border-subtle)"}}>{children}</td>,
        blockquote: ({ children }) => <blockquote style={{paddingLeft:16,margin:"12px 0",borderLeft:"2px solid var(--bg-surface-hover)",color:"var(--text-secondary)"}}>{children}</blockquote>,
        hr: () => <hr style={{margin:"20px 0",borderColor:"var(--border-card)"}} />,
      }}>{content}</ReactMarkdown>
    </div>
  );
}
