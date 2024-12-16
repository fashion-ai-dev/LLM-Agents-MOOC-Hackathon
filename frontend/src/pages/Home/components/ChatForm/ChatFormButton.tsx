import { ArrowUp, Square } from 'lucide-react';

import { cn } from '@/lib/utils';

interface ChatFormButtonProps {
  type: 'start' | 'stop';
  disabled?: boolean;
  hidden?: boolean;
  action?: () => void;
}

export function ChatFormButton({
  type,
  disabled,
  hidden,
  action,
}: ChatFormButtonProps) {
  return (
    <button
      type={type === 'start' ? 'submit' : 'button'}
      className={cn(
        'absolute right-3 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-[20px] bg-black text-white disabled:cursor-not-allowed disabled:opacity-30',
        hidden && 'hidden',
      )}
      disabled={disabled}
      onClick={action}
    >
      {type === 'start' && <ArrowUp size={16} />}
      {type === 'stop' && <Square size={16} />}
    </button>
  );
}
