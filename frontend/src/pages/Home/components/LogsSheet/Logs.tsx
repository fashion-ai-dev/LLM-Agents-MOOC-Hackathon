import { memo, useEffect, useRef } from 'react';

import { useChat } from '../../contexts/ChatContext';

import { AgentCard } from './AgentCard';

function Logs() {
  const { logs } = useChat();

  const logsEndRef = useRef<HTMLDivElement>(null);

  const currentColorRef = useRef(0);
  const lastMessageIdRef = useRef('');

  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  return (
    <div className="h-full space-y-4 overflow-scroll p-16 scrollbar-hide">
      {logs.map((log, index) => {
        if (log.messageId !== lastMessageIdRef.current) {
          currentColorRef.current = 1 - currentColorRef.current;
        }

        lastMessageIdRef.current = log.messageId;

        return (
          <AgentCard key={index} log={log} color={currentColorRef.current} />
        );
      })}

      <div ref={logsEndRef} />
    </div>
  );
}

export default memo(Logs);
