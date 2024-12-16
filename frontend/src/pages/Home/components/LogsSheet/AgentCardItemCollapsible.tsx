import { ChevronDown } from 'lucide-react';
import { ReactNode, useState } from 'react';

import { cn } from '@/lib/utils';

interface AgentCardCollapsibleProps {
  title: string | ReactNode | (() => ReactNode);
  icon: ReactNode;
  content: string | ReactNode | (() => ReactNode);
  contentSize?: 'normal' | 'small';
}

export function AgentCardItemCollapsible({
  content,
  title,
  icon,
  contentSize = 'normal',
}: AgentCardCollapsibleProps) {
  const [isOpen, setIsOpen] = useState(false);

  function toggleOpen() {
    setIsOpen(!isOpen);
  }

  return (
    <div className="overflow-hidden">
      <div
        className="flex w-full cursor-pointer justify-between"
        onClick={toggleOpen}
      >
        <div className="flex flex-wrap items-center gap-1">
          {icon}
          {typeof title === 'function' ? title() : title}
        </div>

        <ChevronDown />
      </div>

      {isOpen && (
        <div
          className={cn('mt-2 w-full', contentSize === 'small' && 'text-xs')}
        >
          {typeof content === 'function' ? content() : content}
        </div>
      )}
    </div>
  );
}
