import { StoreSlice } from '../Store';

type ConversationHistory = {
  threadId: string;
  firstMessage: string;
};

type SelectedUser = {
  id: number;
  customerId: number;
};

type ChatState = {
  isLogsOpen: boolean;
  hasConversation: boolean;
  conversationHistory: ConversationHistory[];
  selectedUser: SelectedUser | null;
};

type ChatActions = {
  setIsLogsOpen: (value: boolean) => void;
  setHasConversation: (value: boolean) => void;
  setConversationHistory: (value: ConversationHistory[]) => void;
  setSelectedUser: (value: SelectedUser | null) => void;
};

export type ChatSlice = ChatState & ChatActions;

export const createChatSlice: StoreSlice<ChatSlice> = (set) => ({
  isLogsOpen: false,
  hasConversation: false,
  conversationHistory: [],
  selectedUser: null,
  setIsLogsOpen: (value) =>
    set((state) => {
      state.chat.isLogsOpen = value;
    }),
  setHasConversation: (value) =>
    set((state) => {
      state.chat.hasConversation = value;
    }),
  setConversationHistory: (value) => {
    set((state) => {
      state.chat.conversationHistory = value;
    });
  },
  setSelectedUser: (value) => {
    set((state) => {
      state.chat.selectedUser = value;
    });
  },
});
