// import { CopilotIndicator } from './CopilotIndicator';
import { OpenAiForm } from './OpenAiForm';

export function Sidebar() {
  return (
    <aside className="hidden w-[282px] lg:block">
      <div className="sticky left-0 top-0 flex h-dvh w-[282px] flex-col overflow-scroll px-6 py-10 scrollbar-hide">
        {/* <CopilotIndicator /> */}
        <OpenAiForm />
      </div>
    </aside>
  );
}
