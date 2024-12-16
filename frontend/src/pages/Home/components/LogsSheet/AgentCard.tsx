import {
  ChartGantt,
  ChevronDown,
  CircleCheck,
  CircleX,
  Clock,
  Computer,
  Cpu,
  Hash,
  MessageSquareMore,
  PanelTopOpen,
  SquareDashedBottomCode,
  SquareTerminal,
  User,
} from 'lucide-react';
import { Fragment, useState } from 'react';

import { AssistantIcon } from '@/components/AssistantIcon';
import { CodeSnippet } from '@/components/CodeSnippet';
import { cn } from '@/lib/utils';

import { Log } from '../../hooks/useLogs';

import { AgentCardItem } from './AgentCardItem';
import { AgentCardItemCollapsible } from './AgentCardItemCollapsible';

interface AgentCardProps {
  log: Log;
  color: number;
}

export function AgentCard({ log, color }: AgentCardProps) {
  const [isOpen, setIsOpen] = useState(false);

  function toggleOpen() {
    setIsOpen(!isOpen);
  }

  function formatDate(timestamp: string) {
    const date = new Date(timestamp);

    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return `${hours}:${minutes}:${seconds}`;
  }

  return (
    <div
      className={cn(
        'mx-auto w-full rounded-lg border-t-2 bg-white shadow-md',
        color === 1 ? 'border-green-600' : 'border-blue-600',
      )}
    >
      <div
        className="flex w-full cursor-pointer justify-between p-6"
        onClick={toggleOpen}
      >
        <span className="flex items-center gap-2 text-lg">
          <AssistantIcon size={28} />

          <span>{log.agentName}</span>
        </span>

        <div className="flex items-center gap-1">
          <span className="flex items-center gap-1 font-light text-gray-600">
            <Clock />

            {formatDate(log.timestamp)}
          </span>

          <ChevronDown />
        </div>
      </div>

      {isOpen && (
        <>
          <div className="mx-6 h-[1px] bg-[#C6C6C6]" />

          <div className="bg-gray-[#F6F6F6] w-full space-y-5 p-6">
            <AgentCardItem
              title="User Question"
              icon={<User />}
              content={log.userQuestion}
            />

            <AgentCardItemCollapsible
              title="Log IDs"
              icon={<Hash />}
              content={
                <div className="space-y-2">
                  <div>
                    <strong>MID: </strong> {log.messageId}
                  </div>
                  <div>
                    <strong>SID: </strong> {log.sessionId}
                  </div>
                  <div>
                    <strong>LID: </strong> {log.logId}
                  </div>
                </div>
              }
            />

            <AgentCardItemCollapsible
              title="Agent Prompt"
              icon={<SquareTerminal />}
              content={log.agentPromptContent}
            />

            <AgentCardItemCollapsible
              title="Conversation History"
              icon={<MessageSquareMore />}
              content={
                <div className="space-y-2">
                  {log.conversationHistory.map((item, index) => {
                    if (!item.content) {
                      return null;
                    }

                    return (
                      <p key={index}>
                        <strong className="font-semibold">{item?.role}:</strong>{' '}
                        {item.content}
                      </p>
                    );
                  })}
                </div>
              }
            />

            {log?.planning && (
              <AgentCardItemCollapsible
                title="Planning"
                icon={<ChartGantt />}
                content={
                  <div className="space-y-2">
                    {log?.planning.map((item, itemIndex) => (
                      <Fragment key={itemIndex}>
                        {Object.entries(item ?? {}).map((output, index) => (
                          <p key={index}>
                            <strong className="font-semibold">
                              {output[0].replace('_', ' ')}:
                            </strong>{' '}
                            {typeof output[1] === 'object'
                              ? JSON.stringify(output[1])
                              : output[1]}
                          </p>
                        ))}
                      </Fragment>
                    ))}
                  </div>
                }
              />
            )}

            {log?.agentDecision && (
              <AgentCardItem
                title="Agent Decision"
                icon={<Cpu />}
                content={log.agentDecision}
              />
            )}

            {log?.codeSnippet && (
              <AgentCardItemCollapsible
                title="Snippet"
                icon={<SquareDashedBottomCode />}
                content={
                  <CodeSnippet language="python" codeString={log.codeSnippet} />
                }
                contentSize="small"
              />
            )}

            {log?.agentOutput && (
              <AgentCardItemCollapsible
                title="Agent Output"
                icon={<PanelTopOpen />}
                content={
                  <div className="space-y-2">
                    {Object.entries(log?.agentOutput ?? {}).map(
                      (output, index) => (
                        <p key={index}>
                          <strong className="font-semibold">
                            {output[0]}:
                          </strong>{' '}
                          {output[1]}
                        </p>
                      ),
                    )}
                  </div>
                }
              />
            )}

            {log?.codeOutput && (
              <AgentCardItemCollapsible
                title={() => {
                  const isBiManager = log.agentName === 'BI Manager';

                  if (isBiManager && log?.codeOutput?.status === 'success') {
                    return (
                      <>
                        Code Output
                        <CircleCheck size={20} className="text-green-600" />
                      </>
                    );
                  }

                  if (isBiManager && log?.codeOutput?.status === 'error') {
                    return (
                      <>
                        Code Output
                        <CircleX size={20} className="text-red-600" />
                      </>
                    );
                  }

                  return 'Code Output';
                }}
                icon={<Computer />}
                content={
                  <div className="space-y-2">
                    {Object.entries(log?.codeOutput ?? {}).map(
                      (output, index) => (
                        <p key={index}>
                          <strong className="font-semibold">
                            {output[0]}:
                          </strong>{' '}
                          {JSON.stringify(output[1])}
                        </p>
                      ),
                    )}
                  </div>
                }
              />
            )}
          </div>
        </>
      )}
    </div>
  );
}
