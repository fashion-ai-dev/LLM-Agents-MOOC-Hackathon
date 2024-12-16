import { ChevronLeft } from 'lucide-react';
import { useEffect } from 'react';

import { Button } from '@/components/ui/Button';
import { useStore } from '@/store';

export function Trigger() {
  const { isLogsOpen, setIsLogsOpen } = useStore((state) => state.chat);

  useEffect(() => {
    function onKeydown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key === '.') {
        setIsLogsOpen(!isLogsOpen);
      }

      if (event.key === 'Escape') {
        setIsLogsOpen(false);
      }
    }

    window.addEventListener('keydown', onKeydown);

    return () => {
      window.removeEventListener('keydown', onKeydown);
    };
  }, [isLogsOpen, setIsLogsOpen]);

  return (
    <Button
      className="fixed right-0 top-1/2 -translate-y-1/2 p-2"
      variant="outline"
      onClick={() => setIsLogsOpen(!isLogsOpen)}
    >
      <ChevronLeft />
    </Button>
  );
}
