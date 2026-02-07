"use client";

import {
  createContext,
  useContext,
  useReducer,
  useCallback,
  useEffect,
  type ReactNode,
} from "react";
import type { Conversation } from "@/types";
import { api } from "@/lib/api/client";

interface ConversationState {
  conversations: Conversation[];
  activeId: string | null;
  isLoading: boolean;
  error: string | null;
}

type ConversationAction =
  | { type: "SET_CONVERSATIONS"; payload: Conversation[] }
  | { type: "ADD_CONVERSATION"; payload: Conversation }
  | { type: "UPDATE_CONVERSATION"; payload: Conversation }
  | { type: "DELETE_CONVERSATION"; payload: string }
  | { type: "SET_ACTIVE"; payload: string | null }
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_ERROR"; payload: string | null };

function conversationReducer(
  state: ConversationState,
  action: ConversationAction
): ConversationState {
  switch (action.type) {
    case "SET_CONVERSATIONS":
      return { ...state, conversations: action.payload, isLoading: false };
    case "ADD_CONVERSATION":
      return {
        ...state,
        conversations: [action.payload, ...state.conversations],
      };
    case "UPDATE_CONVERSATION":
      return {
        ...state,
        conversations: state.conversations.map((c) =>
          c.id === action.payload.id ? action.payload : c
        ),
      };
    case "DELETE_CONVERSATION":
      return {
        ...state,
        conversations: state.conversations.filter(
          (c) => c.id !== action.payload
        ),
        activeId:
          state.activeId === action.payload ? null : state.activeId,
      };
    case "SET_ACTIVE":
      return { ...state, activeId: action.payload };
    case "SET_LOADING":
      return { ...state, isLoading: action.payload };
    case "SET_ERROR":
      return { ...state, error: action.payload, isLoading: false };
    default:
      return state;
  }
}

interface ConversationContextValue extends ConversationState {
  loadConversations: () => Promise<void>;
  createConversation: () => Promise<Conversation>;
  renameConversation: (id: string, title: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  setActiveConversation: (id: string | null) => void;
}

const ConversationContext = createContext<ConversationContextValue | null>(null);

export function ConversationProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(conversationReducer, {
    conversations: [],
    activeId: null,
    isLoading: true,
    error: null,
  });

  const loadConversations = useCallback(async () => {
    dispatch({ type: "SET_LOADING", payload: true });
    try {
      const conversations = await api.getConversations();
      dispatch({ type: "SET_CONVERSATIONS", payload: conversations });
    } catch (err) {
      dispatch({
        type: "SET_ERROR",
        payload:
          err instanceof Error ? err.message : "Failed to load conversations",
      });
    }
  }, []);

  const createConversation = useCallback(async () => {
    const conversation = await api.createConversation();
    dispatch({ type: "ADD_CONVERSATION", payload: conversation });
    dispatch({ type: "SET_ACTIVE", payload: conversation.id });
    return conversation;
  }, []);

  const renameConversation = useCallback(
    async (id: string, title: string) => {
      const updated = await api.updateConversation(id, { title });
      dispatch({ type: "UPDATE_CONVERSATION", payload: updated });
    },
    []
  );

  const deleteConversation = useCallback(async (id: string) => {
    dispatch({ type: "DELETE_CONVERSATION", payload: id });
    try {
      await api.deleteConversation(id);
    } catch {
      // Reload on failure to re-sync
      loadConversations();
    }
  }, [loadConversations]);

  const setActiveConversation = useCallback((id: string | null) => {
    dispatch({ type: "SET_ACTIVE", payload: id });
  }, []);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  return (
    <ConversationContext.Provider
      value={{
        ...state,
        loadConversations,
        createConversation,
        renameConversation,
        deleteConversation,
        setActiveConversation,
      }}
    >
      {children}
    </ConversationContext.Provider>
  );
}

export function useConversations() {
  const context = useContext(ConversationContext);
  if (!context) {
    throw new Error(
      "useConversations must be used within a ConversationProvider"
    );
  }
  return context;
}
