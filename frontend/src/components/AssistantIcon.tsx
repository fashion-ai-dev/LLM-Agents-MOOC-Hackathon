import { Bot, LucideProps } from 'lucide-react';
import { RefAttributes } from 'react';

interface AssistantIconProps
  extends Omit<LucideProps, 'ref'>,
    RefAttributes<SVGSVGElement> {}

export function AssistantIcon(props: AssistantIconProps) {
  return <Bot {...props} />;
}
