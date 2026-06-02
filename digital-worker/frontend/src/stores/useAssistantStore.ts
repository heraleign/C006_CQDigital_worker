import { create } from 'zustand';
import type { ChatMessage, ChatSession } from '@/types';
import { assistantApi } from '@/services/assistant';

interface TaskContext {
  task_name: string;
  task_id: string;
  status: string;
}

interface AssistantState {
  visible: boolean;
  sessions: ChatSession[];
  currentSession: ChatSession | null;
  messages: ChatMessage[];
  loading: boolean;
  sending: boolean;
  taskContext: TaskContext | null;

  toggleVisible: () => void;
  setVisible: (v: boolean) => void;
  loadSessions: () => Promise<void>;
  selectSession: (session: ChatSession) => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  createNewSession: () => Promise<void>;
  setTaskContext: (ctx: TaskContext | null) => void;
}

export const useAssistantStore = create<AssistantState>((set, get) => ({
  visible: false,
  sessions: [],
  currentSession: null,
  messages: [],
  loading: false,
  sending: false,
  taskContext: null,

  toggleVisible: () => set((s) => ({ visible: !s.visible })),
  setVisible: (v) => set({ visible: v }),

  loadSessions: async () => {
    set({ loading: true });
    try {
      const res: any = await assistantApi.getSessions();
      const sessions = res.data?.items || res?.items || [];
      set({ sessions, loading: false });
      if (sessions.length > 0 && !get().currentSession) {
        get().selectSession(sessions[0]);
      }
    } catch {
      set({ loading: false });
    }
  },

  selectSession: async (session: ChatSession) => {
    set({ currentSession: session, messages: [] });
    try {
      const res: any = await assistantApi.getMessages({ session_id: session.session_id });
      const messages = res.data?.items || res?.items || [];
      set({ messages });
    } catch {
      // ignore
    }
  },

  sendMessage: async (content: string) => {
    const { currentSession, messages } = get();
    const sessionId = currentSession?.session_id || 'SESS_0001';

    // Add user message
    const userMsg: ChatMessage = {
      message_id: 'MSG_' + Date.now(),
      session_id: sessionId,
      role: 'user',
      content,
      message_type: 'text',
      created_at: new Date().toISOString(),
    };

    set({ messages: [...messages, userMsg], sending: true });

    try {
      const res: any = await assistantApi.sendMessage({ session_id: sessionId, message: content });
      const reply = res.data?.reply || res?.reply || '您好！我是数字员工小智，有什么可以帮您的？';

      const assistantMsg: ChatMessage = {
        message_id: 'MSG_' + (Date.now() + 1),
        session_id: sessionId,
        role: 'assistant',
        content: reply,
        message_type: 'text',
        created_at: new Date().toISOString(),
      };

      set({ messages: [...get().messages, assistantMsg], sending: false });
    } catch {
      set({ sending: false });
    }
  },

  createNewSession: async () => {
    try {
      const res: any = await assistantApi.createSession({ title: '新对话' });
      const session = res.data || res;
      set({ currentSession: session, messages: [] });
      get().loadSessions();
    } catch {
      // ignore
    }
  },

  setTaskContext: (ctx) => set({ taskContext: ctx }),
}));
