import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useState,
} from 'react';
import { io } from 'socket.io-client';

import { env } from '@/config/env';
import { useStore } from '@/store';

import {
  Conversation,
  ConversationDto,
  useConversation,
} from '../hooks/useConversation';
import { Log, useLogs } from '../hooks/useLogs';

const SOCKET_URL = env.SOCKET_URL ?? '';

const socket = io(SOCKET_URL, {
  transports: ['websocket'],
  autoConnect: false,
  timeout: 320000,
});

export interface ChatContextValue {
  openAiKey: null | string;
  conversation: Conversation[];
  logs: Log[];
  isConnected: boolean;
  isLoading: boolean;
  isChatting: boolean;
  handleOpenAiKey: (key: string) => void;
  handleConversation: (dto: ConversationDto) => void;
  handleCancelConversation: () => void;
}

const ChatContext = createContext({} as ChatContextValue);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [openAiKey, setOpenAiKey] = useState<null | string>(null);
  const [isLoading, setIsLoading] = useState(false);

  const { isConnected, setIsConnected } = useStore((state) => state.socket);

  const handleOpenAiKey = useCallback((key: string) => {
    setOpenAiKey(key);
  }, []);

  const {
    conversation,
    isChatting,
    handleConversation,
    handleCancelConversation,
  } = useConversation(socket, isConnected, openAiKey, setIsLoading);

  const { logs } = useLogs(socket, isConnected);

  useEffect(() => {
    socket.connect();
  }, []);

  useEffect(() => {
    function onConnect() {
      setIsLoading(false);

      socket.emit(
        'register',
        JSON.stringify({
          id: 1,
          email: '',
          customer: 1,
          catalogToken: '',
        }),
      );
    }

    socket.on('connect', onConnect);

    return () => {
      socket.off('connect', onConnect);
    };
  }, []);

  useEffect(() => {
    function onRegisterSuccess() {
      setIsLoading(false);
      setIsConnected(true);
    }

    socket.on('register_success', onRegisterSuccess);

    return () => {
      socket.off('register_success', onRegisterSuccess);
    };
  }, [setIsConnected]);

  useEffect(() => {
    function onDisconnect() {
      setIsLoading(false);
      setIsConnected(false);
    }

    socket.on('disconnect', onDisconnect);

    return () => {
      socket.off('disconnect', onDisconnect);
    };
  }, [setIsConnected]);

  useEffect(() => {
    function onInvalidJwt() {}

    socket.on('invalid_jwt', onInvalidJwt);

    return () => {
      socket.off('invalid_jwt', onInvalidJwt);
    };
  }, []);

  const value: ChatContextValue = {
    openAiKey,
    conversation,
    logs,
    isConnected,
    isLoading,
    isChatting,
    handleOpenAiKey,
    handleConversation,
    handleCancelConversation,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat() {
  return useContext(ChatContext);
}
