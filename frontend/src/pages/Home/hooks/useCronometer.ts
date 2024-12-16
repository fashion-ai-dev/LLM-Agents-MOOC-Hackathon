import { produce } from 'immer';
import { useEffect, useState } from 'react';

import { useStore } from '@/store';

const timeInitialState = { current: 0, previous: 0 };

export function useCronometer(isRunning: boolean) {
  const [time, setTime] = useState(timeInitialState);

  const { hasConversation } = useStore((state) => state.chat);

  useEffect(() => {
    if (!hasConversation) {
      setTime(timeInitialState);
    }
  }, [hasConversation]);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    if (isRunning) {
      intervalId = setInterval(() => {
        setTime(
          produce((draft) => {
            draft.current = draft.current + 10;
          }),
        );
      }, 10);
    }

    return () => {
      clearInterval(intervalId);
    };
  }, [isRunning]);

  function formatTime(ms: number) {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    const milliseconds = Math.floor((ms % 1000) / 10);
    return `${minutes.toString().padStart(2, '0')}:${seconds
      .toString()
      .padStart(2, '0')}.${milliseconds.toString().padStart(2, '0')}`;
  }

  useEffect(() => {
    if (!isRunning) {
      setTime(
        produce((draft) => {
          draft.previous = draft.current;
          draft.current = 0;
        }),
      );
    }
  }, [isRunning]);

  return {
    time: formatTime(time.current),
    previousTime: formatTime(time.previous),
  };
}
