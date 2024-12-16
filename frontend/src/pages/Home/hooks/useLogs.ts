import { produce } from 'immer';
import { useEffect, useState } from 'react';
import { Socket } from 'socket.io-client';

import { useThreadParams } from '@/hooks/useThreadParams';
import { useStore } from '@/store';

export interface Log {
  agentName: string;
  agentPrompt: string;
  agentPromptContent: string;
  agentResponse: string;
  agentDecision: string;
  agentOutput: {
    [key: string]: string;
  };
  codeOutput: {
    [key: string]: string;
  };
  conversationHistory: {
    role: string;
    content: string;
  }[];
  codeSnippet: string;
  completionTokens: number;
  logId: string;
  messageId: string;
  outputToken: number;
  planning: {
    [key: string]: string;
  }[];
  promptToken: number;
  sessionId: string;
  timestamp: string;
  userQuestion: string;
}

export function useLogs(socket: Socket, isConnected: boolean) {
  const [logs, setLogs] = useState<Log[]>([]);

  const { params, selectedUser } = useThreadParams();

  const { hasConversation } = useStore((state) => state.chat);

  useEffect(() => {
    if (!hasConversation) {
      setLogs([]);
    }
  }, [hasConversation]);

  useEffect(() => {
    function onConversationLogs(conversationLogs: any) {
      const formattedConversationLogs: Log = {
        agentName: conversationLogs.agent_name,
        agentPrompt: conversationLogs.agent_prompt,
        agentPromptContent: conversationLogs.agent_prompt_content,
        agentResponse: conversationLogs.agent_response,
        agentDecision: conversationLogs.agent_decision,
        agentOutput: conversationLogs.agent_output,
        codeOutput: conversationLogs.code_output,
        conversationHistory: conversationLogs.conversation_history,
        codeSnippet: conversationLogs.code_snippet,
        completionTokens: conversationLogs.completion_tokens,
        logId: conversationLogs.log_id,
        messageId: conversationLogs.message_id,
        outputToken: conversationLogs.output_token,
        planning: conversationLogs.planning,
        promptToken: conversationLogs.prompt_token,
        sessionId: conversationLogs.session_id,
        timestamp: conversationLogs.timestamp,
        userQuestion: conversationLogs.user_question,
      };

      setLogs(
        produce((draft) => {
          const hasLogIndex = draft.findIndex(
            (draftItem) => draftItem.logId === conversationLogs.log_id,
          );

          if (hasLogIndex >= 0) {
            draft[hasLogIndex] = { ...formattedConversationLogs };
            return;
          }

          draft.push(formattedConversationLogs);
        }),
      );
    }

    socket.on('conversation_logs', onConversationLogs);

    return () => {
      socket.off('conversation_logs', onConversationLogs);
    };
  }, [socket]);

  useEffect(() => {
    if (!isConnected || !selectedUser || !params.threadId) {
      return;
    }

    socket.emit(
      'get_log_list_by_user_and_customer',
      JSON.stringify({
        user_id: selectedUser.id,
        customer_id: selectedUser.customerId,
        thread_id: params.threadId,
      }),
    );
  }, [socket, isConnected, selectedUser, params]);

  useEffect(() => {
    function onGetLogListByUserAndCustomerSuccess(data: any[]) {
      const mappedLogs = data.map((conversationLog) => ({
        agentName: conversationLog.agent_name,
        agentPrompt: conversationLog.agent_prompt,
        agentPromptContent: conversationLog.agent_prompt_content,
        agentResponse: conversationLog.agent_response,
        agentDecision: conversationLog.agent_decision,
        agentOutput: conversationLog.agent_output,
        codeOutput: conversationLog.code_output,
        conversationHistory: conversationLog.conversation_history,
        codeSnippet: conversationLog.code_snippet,
        completionTokens: conversationLog.completion_tokens,
        logId: conversationLog.log_id,
        messageId: conversationLog.message_id,
        outputToken: conversationLog.output_token,
        planning: conversationLog.planning,
        promptToken: conversationLog.prompt_token,
        sessionId: conversationLog.session_id,
        timestamp: conversationLog.timestamp,
        userQuestion: conversationLog.user_question,
      }));

      setLogs(mappedLogs);
    }

    socket.on(
      'get_log_list_by_user_and_customer_success',
      onGetLogListByUserAndCustomerSuccess,
    );

    return () => {
      socket.off(
        'get_log_list_by_user_and_customer_success',
        onGetLogListByUserAndCustomerSuccess,
      );
    };
  }, [socket]);

  return { logs };
}
