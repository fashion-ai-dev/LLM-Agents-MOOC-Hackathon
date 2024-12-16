import { ChatForm } from './components/ChatForm';
import { LogsSheet } from './components/LogsSheet';
import { Sidebar } from './components/Sidebar';
import { Thread } from './components/Thread';
import { ChatProvider } from './contexts/ChatContext';

export function Home() {
  return (
    <ChatProvider>
      <div className="flex">
        <Sidebar />

        <main className="w-full px-6 lg:px-[60px]">
          <div className="flex h-dvh flex-col">
            <h1 className="sr-only">Copilot</h1>

            <section className="flex w-full flex-1 flex-col items-center overflow-scroll scrollbar-hide">
              <div className="w-full max-w-[1024px]">
                <Thread />
              </div>
            </section>

            <section className="mt-12 flex justify-center pb-[10px]">
              <div className="w-full max-w-[1024px]">
                <ChatForm />
              </div>
            </section>
          </div>

          <LogsSheet />
        </main>
      </div>
    </ChatProvider>
  );
}
