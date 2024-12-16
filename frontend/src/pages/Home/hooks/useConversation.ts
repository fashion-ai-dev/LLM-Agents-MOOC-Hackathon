import {
  Dispatch,
  SetStateAction,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { Socket } from 'socket.io-client';

import { useThreadParams } from '@/hooks/useThreadParams';
import { useStore } from '@/store';

export interface ConversationDto {
  message: string;
  image: null;
}

export interface Conversation {
  id: string;
  fileUrl: string;
  message: string;
  assistant: boolean;
  evaluation:
    | undefined
    | {
        rating: number | undefined;
        explanation: string | undefined;
      };
}

export interface ConversationHistory {
  threadId: string;
  firstMessage: string;
}

export function useConversation(
  socket: Socket,
  isConnected: boolean,
  openAiKey: null | string,
  setIsLoading: Dispatch<SetStateAction<boolean>>,
) {
  const [conversation, setConversation] = useState<Conversation[]>([]);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [isChatting, setIsChatting] = useState(false);

  const { params, selectedUser, setSelectedUser, clearThreadParams } =
    useThreadParams();

  const { conversationHistory, setHasConversation, setConversationHistory } =
    useStore((state) => state.chat);

  const filteredConversation = useMemo(() => {
    return isChatting
      ? conversation.concat([
          {
            id: '1',
            message: '',
            fileUrl: '',
            evaluation: undefined,
            assistant: true,
          },
        ])
      : conversation.filter((conversation) => conversation.id !== '1');
  }, [conversation, isChatting]);

  const handleConversation = useCallback(
    ({ message, image }: ConversationDto) => {
      setConversation((state) => [
        ...state,
        {
          id: String(Math.random()),
          message,
          fileUrl: '',
          assistant: false,
          evaluation: undefined,
        },
      ]);

      setIsChatting(true);

      socket.emit('conversation', {
        open_ai_key: openAiKey,
        thread_id: threadId,
        message: {
          userInput: message,
        },
        image,
      });
    },
    [openAiKey, socket, threadId],
  );

  const handleCancelConversation = useCallback(() => {
    socket.emit('cancel_conversation');
    setIsChatting(false);
  }, [socket]);

  useEffect(() => {
    conversation.length > 0
      ? setHasConversation(true)
      : setHasConversation(false);
  }, [conversation, setHasConversation]);

  useEffect(() => {
    setSelectedUser({
      id: 1,
      customerId: 1,
    });
  }, [setSelectedUser]);

  useEffect(() => {
    function onConversation() {
      clearThreadParams();
      handleCancelConversation();
      setConversation([]);
      setThreadId(null);
    }

    document.addEventListener('conversation', onConversation);

    return () => {
      document.removeEventListener('conversation', onConversation);
    };
  }, [socket, handleCancelConversation, clearThreadParams]);

  useEffect(() => {
    function onConversationSuccess(data: any) {
      setConversation((state) => [
        ...state,
        {
          id: data.message.id,
          message: data.message.response,
          fileUrl: data.file_url,
          assistant: true,
          evaluation: undefined,
        },
      ]);
      setThreadId(data.thread_id);
      setIsChatting(false);
    }

    socket.on('conversation_success', onConversationSuccess);

    return () => {
      socket.off('conversation_success', onConversationSuccess);
    };
  }, [socket, setConversation, setThreadId]);

  useEffect(() => {
    function onConversationError() {
      setIsChatting(false);
    }

    socket.on('conversation_error', onConversationError);

    return () => {
      socket.off('conversation_error', onConversationError);
    };
  }, [socket]);

  useEffect(() => {
    function onConversationHistory(data: any[]) {
      const slicedArray = data?.slice(-30) ?? [];

      const mappedHistory: ConversationHistory[] = slicedArray
        .map((history) => ({
          threadId: history?.thread_id,
          firstMessage: history?.first_message,
        }))
        .reverse();

      setConversationHistory(mappedHistory);
    }

    socket.on('conversation_history', onConversationHistory);

    return () => {
      socket.off('conversation_history', onConversationHistory);
    };
  }, [socket, setConversationHistory]);

  useEffect(() => {
    if (
      conversationHistory.length > 0 &&
      params.threadId &&
      params.customerId
    ) {
      handleCancelConversation();
      setIsLoading(true);
      setConversation([]);
      setThreadId(null);

      socket.emit(
        'get_thread',
        JSON.stringify({
          thread_id: params.threadId,
          customer_id: params.customerId,
        }),
      );
    }
  }, [
    conversationHistory,
    params,
    socket,
    setIsLoading,
    handleCancelConversation,
  ]);

  useEffect(() => {
    function onGetThreadSuccess(
      data: null | { messages: any[]; thread_id: string },
    ) {
      try {
        if (!data || !data.thread_id || data.messages?.length === 0) {
          clearThreadParams();
        }

        const filteredMessages = data?.messages?.filter(
          (message) =>
            message?.content &&
            (message?.role === 'user' || message?.role === 'assistant'),
        );

        const mappedMessages: Conversation[] | undefined =
          filteredMessages?.map((message) => ({
            id: message?.id,
            assistant: message?.role === 'assistant',
            message: message?.content,
            fileUrl: '',
            evaluation: message?.evaluation,
          }));

        if (mappedMessages && data?.thread_id) {
          setConversation(mappedMessages);
          setThreadId(data.thread_id);
        }
      } catch {
        //
      } finally {
        setIsLoading(false);
      }
    }

    socket.on('get_thread_success', onGetThreadSuccess);

    return () => {
      socket.off('get_thread_success', onGetThreadSuccess);
    };
  }, [socket, setIsLoading, clearThreadParams]);

  useEffect(() => {
    if (!selectedUser || !isConnected) {
      return;
    }

    socket.emit(
      'get_thread_list_by_user_and_customer',
      JSON.stringify({
        user_id: selectedUser.id,
        customer_id: selectedUser.customerId,
      }),
    );
  }, [socket, isConnected, selectedUser]);

  useEffect(() => {
    function onGetThreadListByUserAndCustomerSuccess(data: any[]) {
      const slicedArray = data?.slice(-30) ?? [];

      const mappedHistory: ConversationHistory[] = slicedArray
        .map((history) => ({
          threadId: history?.thread_id,
          firstMessage: history?.first_message,
        }))
        .reverse();

      setConversationHistory(mappedHistory);
    }

    socket.on(
      'get_thread_list_by_user_and_customer_success',
      onGetThreadListByUserAndCustomerSuccess,
    );

    return () => {
      socket.off(
        'get_thread_list_by_user_and_customer_success',
        onGetThreadListByUserAndCustomerSuccess,
      );
    };
  }, [socket, setConversationHistory]);

  return {
    conversation: filteredConversation,
    isChatting,
    handleConversation,
    handleCancelConversation,
  };
}
