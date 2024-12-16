import { ReactNode } from 'react';

interface AgentCardItemProps {
  title: string;
  content: string;
  icon: ReactNode;
}

export function AgentCardItem({ content, icon, title }: AgentCardItemProps) {
  return (
    <div className="flex items-start gap-1">
      <div>{icon}</div> {title}: {content}
    </div>
  );
}
