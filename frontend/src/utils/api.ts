const BASE = "";

export async function runtimePing() {
  const res = await fetch(`${BASE}/api/runtime/ping`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: "{}",
    keepalive: true,
  });
  return res.ok;
}

export function runtimeShutdown() {
  const url = `${BASE}/api/runtime/shutdown`;
  const payload = new Blob(["{}"], { type: "application/json" });
  navigator.sendBeacon(url, payload);
}

export async function fetchStockSearch(q: string) {
  const res = await fetch(`${BASE}/api/stock/search?q=${encodeURIComponent(q)}`);
  if (!res.ok) throw new Error("搜索失败");
  const json = await res.json();
  return json.data as { code: string; name: string }[];
}

export async function fetchStockQuote(code: string) {
  const res = await fetch(`${BASE}/api/stock/quote/${code}`);
  if (!res.ok) throw new Error("获取行情失败");
  const json = await res.json();
  return json.data;
}

export async function fetchKLine(
  code: string,
  period = "daily",
  count = 120
) {
  const res = await fetch(
    `${BASE}/api/stock/kline/${code}?period=${period}&count=${count}`
  );
  if (!res.ok) throw new Error("获取K线失败");
  const json = await res.json();
  return json.data;
}

export async function fetchIndicators(code: string, count = 120) {
  const res = await fetch(
    `${BASE}/api/stock/indicators/${code}?count=${count}`
  );
  if (!res.ok) throw new Error("获取指标失败");
  const json = await res.json();
  return json.data;
}

export async function fetchAnalysis(code: string) {
  const res = await fetch(`${BASE}/api/stock/analysis/${code}`);
  if (!res.ok) throw new Error("获取技术分析失败");
  const json = await res.json();
  return json.data;
}

export async function fetchStockNews(code: string, count = 10) {
  const res = await fetch(
    `${BASE}/api/stock/news/${code}?count=${count}`
  );
  if (!res.ok) throw new Error("获取新闻失败");
  const json = await res.json();
  return json.data as {
    title: string;
    content: string;
    time: string;
    source: string;
    url: string;
    error?: string;
  }[];
}

export interface ChatRequestMessage {
  role: "user" | "assistant";
  content: string;
}

export async function* streamChat(messages: ChatRequestMessage[]) {
  const res = await fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });

  if (!res.ok) {
    throw new Error(`请求失败: ${res.status}`);
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error("无法读取响应流");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || !trimmed.startsWith("data: ")) continue;
      const payload = trimmed.slice(6);
      if (payload === "[DONE]") return;
      try {
        const parsed = JSON.parse(payload);
        if (parsed.error) throw new Error(parsed.error);
        if (parsed.content) yield parsed.content;
      } catch (e) {
        if (e instanceof SyntaxError) continue;
        throw e;
      }
    }
  }
}
