import { useState } from 'react';

import { Button } from '@/components/ui/Button';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/Popover';
import { cn } from '@/lib/utils';
import { useStore } from '@/store';

export function CopilotIndicator() {
  const [isPopoverOpen, setIsPopoverOpen] = useState(false);

  const socketState = useStore((state) => state.socket);

  function handleOpenPopover() {
    setIsPopoverOpen(true);
  }

  function handleClosePopover() {
    setIsPopoverOpen(false);
  }
  return (
    <Popover open={isPopoverOpen}>
      <Button className="relative mb-4" asChild>
        <PopoverTrigger
          onClick={handleOpenPopover}
          onMouseEnter={handleOpenPopover}
          onMouseLeave={handleClosePopover}
        >
          Copilot
          <div
            className={cn(
              'absolute right-8 top-1/2 h-[6px] w-[6px] -translate-y-1/2 cursor-default rounded-full',
              socketState.isConnected
                ? 'animate-pulse bg-[#28A745]'
                : 'bg-[#FFA78D]',
            )}
          />
        </PopoverTrigger>
      </Button>

      <PopoverContent sideOffset={10} className="w-fit">
        <p>
          {socketState.isConnected
            ? 'Copilot conectado'
            : 'Copilot desconectado'}
        </p>
      </PopoverContent>
    </Popover>
  );
}
