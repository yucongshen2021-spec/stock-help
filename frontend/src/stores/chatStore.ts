import { create } from "zustand";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
}

interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  isStreaming: boolean;

  createConversation: () => string;
  setActiveConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  addMessage: (conversationId: string, message: Message) => void;
  updateLastAssistantMessage: (conversationId: string, content: string) => void;
  appendToLastAssistantMessage: (conversationId: string, chunk: string) => void;
  setStreaming: (streaming: boolean) => void;
  getActiveConversation: () => Conversation | undefined;
}

const genId = () => Math.random().toString(36).substring(2, 10);
const CHAT_STORAGE_KEY = "chat_state_v1";

interface PersistedChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
}

const loadChatState = (): PersistedChatState => {
  const raw = localStorage.getItem(CHAT_STORAGE_KEY);
  if (!raw) {
    return { conversations: [], activeConversationId: null };
  }
  const parsed = JSON.parse(raw) as PersistedChatState;
  return {
    conversations: Array.isArray(parsed.conversations) ? parsed.conversations : [],
    activeConversationId:
      typeof parsed.activeConversationId === "string" ? parsed.activeConversationId : null,
  };
};

const saveChatState = (state: PersistedChatState) => {
  localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(state));
};

const initial = loadChatState();

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: initial.conversations,
  activeConversationId: initial.activeConversationId,
  isStreaming: false,

  createConversation: () => {
    const id = genId();
    const conv: Conversation = {
      id,
      title: "新对话",
      messages: [],
      createdAt: Date.now(),
    };
    set((s) => ({
      conversations: (() => {
        const next = [conv, ...s.conversations];
        saveChatState({ conversations: next, activeConversationId: id });
        return next;
      })(),
      activeConversationId: id,
    }));
    return id;
  },

  setActiveConversation: (id) =>
    set((s) => {
      saveChatState({ conversations: s.conversations, activeConversationId: id });
      return { activeConversationId: id };
    }),

  deleteConversation: (id) =>
    set((s) => {
      const remaining = s.conversations.filter((c) => c.id !== id);
      const activeConversationId =
        s.activeConversationId === id ? remaining[0]?.id ?? null : s.activeConversationId;
      saveChatState({ conversations: remaining, activeConversationId });
      return {
        conversations: remaining,
        activeConversationId,
      };
    }),

  addMessage: (conversationId, message) =>
    set((s) => {
      const conversations = s.conversations.map((c) => {
        if (c.id !== conversationId) return c;
        const updated = { ...c, messages: [...c.messages, message] };
        if (message.role === "user" && c.messages.length === 0) {
          updated.title =
            message.content.length > 20
              ? message.content.slice(0, 20) + "..."
              : message.content;
        }
        return updated;
      });
      saveChatState({ conversations, activeConversationId: s.activeConversationId });
      return { conversations };
    }),

  updateLastAssistantMessage: (conversationId, content) =>
    set((s) => {
      const conversations = s.conversations.map((c) => {
        if (c.id !== conversationId) return c;
        const msgs = [...c.messages];
        const last = msgs[msgs.length - 1];
        if (last?.role === "assistant") {
          msgs[msgs.length - 1] = { ...last, content };
        }
        return { ...c, messages: msgs };
      });
      saveChatState({ conversations, activeConversationId: s.activeConversationId });
      return { conversations };
    }),

  appendToLastAssistantMessage: (conversationId, chunk) =>
    set((s) => {
      const conversations = s.conversations.map((c) => {
        if (c.id !== conversationId) return c;
        const msgs = [...c.messages];
        const last = msgs[msgs.length - 1];
        if (last?.role === "assistant") {
          msgs[msgs.length - 1] = {
            ...last,
            content: last.content + chunk,
          };
        }
        return { ...c, messages: msgs };
      });
      saveChatState({ conversations, activeConversationId: s.activeConversationId });
      return { conversations };
    }),

  setStreaming: (streaming) => set({ isStreaming: streaming }),

  getActiveConversation: () => {
    const s = get();
    return s.conversations.find((c) => c.id === s.activeConversationId);
  },
}));
