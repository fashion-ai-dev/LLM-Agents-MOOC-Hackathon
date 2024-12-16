import { ReactNode } from 'react';

import { cn } from '@/lib/utils';

interface FormGroupProps {
  className?: string;
  error?: {
    message: string | undefined;
    font?: 'xs' | 'sm' | 'base';
    align?: 'left' | 'center' | 'right';
  };
  children: ReactNode;
}

export function FormGroup({
  className,
  error = { message: undefined, font: 'base', align: 'left' },
  children,
}: FormGroupProps) {
  return (
    <div className={cn(className ?? 'flex flex-col gap-1')}>
      {children}
      {error.message && (
        <span
          className={cn(
            'block text-[#EC4D4D]',
            error.font === 'xs' && 'text-xs',
            error.font === 'sm' && 'text-sm',
            error.font === 'base' && 'text-base',
            error.align === 'left' && 'text-left',
            error.align === 'center' && 'text-center',
            error.align === 'right' && 'text-right',
          )}
        >
          {error.message}
        </span>
      )}
    </div>
  );
}
