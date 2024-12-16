import { motion } from 'framer-motion';
import { ChartArea } from 'lucide-react';
import { useState } from 'react';

import { cn } from '@/lib/utils';

import { useChat } from '../../contexts/ChatContext';

interface ThreadHubCardProps {
  input: string;
  delay?: number;
}

export function ThreadHubCard({ input, delay = 0 }: ThreadHubCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  const { isConnected, handleConversation } = useChat();

  function handleMouseEnter() {
    if (!isConnected) {
      return;
    }

    setIsHovered(true);
  }

  function handleMouseLeave() {
    setIsHovered(false);
  }

  function handleClick() {
    if (!isConnected) {
      return;
    }

    handleConversation({ message: input, image: null });
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut', delay }}
      className={cn(
        'flex h-[150px] w-full cursor-pointer flex-col justify-between rounded-lg border border-solid bg-gradient-to-l from-[#F6F6F6] to-[#FCFCFC] p-4 sm:w-[244px]',
        isHovered ? 'border-black' : 'border-[#E8E8E8]',
      )}
      onClick={handleClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div className="text-sm">{input}</div>

      <div className="flex justify-end">
        <div
          className={cn(
            'flex h-10 w-10 items-center justify-center rounded-full bg-black text-white',
            !isHovered && 'opacity-30 transition-opacity',
          )}
        >
          <ChartArea size={20} />
        </div>
      </div>
    </motion.div>
  );
}
