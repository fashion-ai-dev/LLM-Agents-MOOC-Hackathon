import Chart from 'chart.js/auto';
import { useEffect } from 'react';

import { AssistantIcon } from '@/components/AssistantIcon';
import { cn } from '@/lib/utils';

import { Conversation } from '../../hooks/useConversation';

interface ThreadMessageProps {
  conversation: Conversation;
}

export function ThreadMessage({ conversation }: ThreadMessageProps) {
  useEffect(() => {
    if (!conversation.fileUrl) {
      return;
    }
    const controller = new AbortController();

    async function loadChart() {
      try {
        const response = await fetch(conversation.fileUrl, {
          signal: controller.signal,
        });
        const data = await response.json();

        data.options.plugins.tooltip.callbacks.label = eval(
          '(' + data.options.plugins.tooltip.callbacks.label + ')',
        );

        const allChartElements = document.querySelectorAll('.chart-content');
        const currentChartElement =
          allChartElements[allChartElements.length - 1];

        if (currentChartElement) {
          let canvas = currentChartElement.querySelector('canvas') as
            | (HTMLCanvasElement & { __chartInstance?: Chart })
            | undefined;

          if (!canvas) {
            canvas = document.createElement('canvas');
            currentChartElement.appendChild(canvas);
          }

          if (canvas.__chartInstance) {
            canvas.__chartInstance.destroy();
          }

          const ctx = canvas.getContext('2d');

          if (ctx) {
            canvas.__chartInstance = new Chart(ctx, data);
          }
        }
      } catch (error: any) {
        if (error.name === 'AbortError') {
          return;
        }

        console.error(error);
      }
    }

    loadChart();

    return () => {
      controller.abort();
    };
  }, [conversation.fileUrl]);

  if (!conversation.assistant) {
    return (
      <div className="flex justify-end" data-role="user">
        <div className="max-w-[535px] rounded-xl bg-[#F8F8F8] p-[15px] font-light">
          {conversation.message}
        </div>
      </div>
    );
  }

  return (
    <div className="relative flex gap-3 lg:gap-[34px]" data-role="assistant">
      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-black text-white">
        <AssistantIcon size={22} />
      </div>

      {conversation.id === '1' && (
        <div className="flex items-center gap-2">
          <span className="font-normal">Thinking</span>

          <div className="flex gap-1">
            <div
              className={cn(
                'h-2 w-2 rounded-full bg-black opacity-80',
                'animate-bounce-1',
              )}
            />
            <div
              className={cn(
                'h-2 w-2 rounded-full bg-black opacity-80',
                'animate-bounce-2',
              )}
            />
            <div
              className={cn(
                'h-2 w-2 rounded-full bg-black opacity-80',
                'animate-bounce-3',
              )}
            />
          </div>
        </div>
      )}

      {conversation.id !== '1' && (
        <div
          className="flex-1 font-light"
          dangerouslySetInnerHTML={{ __html: conversation.message }}
        />
      )}
    </div>
  );
}
