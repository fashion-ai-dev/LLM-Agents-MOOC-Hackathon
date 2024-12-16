import { useEffect, useRef } from 'react';

import { useChat } from '../../contexts/ChatContext';

import { ThreadHub } from './ThreadHub';
import { ThreadMessage } from './ThreadMessage';

export function Thread() {
  const { conversation, isLoading } = useChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversation]);

  if (isLoading) {
    return null;
  }

  if (conversation.length === 0) {
    return <ThreadHub />;
  }

  return (
    <div className="flex flex-col gap-[60px] pt-16">
      {conversation.map((data) => (
        <ThreadMessage key={data.id} conversation={data} />
      ))}

      <div ref={messagesEndRef} />
    </div>
  );
}
