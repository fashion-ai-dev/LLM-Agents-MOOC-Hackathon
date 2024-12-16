import { ThreadHubCard } from './ThreadHubCard';

const threadHubCardData = [
  {
    input: 'What are the top 5 best-selling products of this year?',
  },
  {
    input: 'Generate a graph with daily sales for September.',
  },
  {
    input:
      'Create a CSV file with top 100 customer by spending over the past 6 months.',
  },
];

export function ThreadHub() {
  return (
    <article className="space-y-8 pt-16 lg:pt-[130px]">
      <section className="max-w-[495px]">
        <p className="text-[50px] uppercase leading-[50px]">
          Let&apos;s{' '}
          <span className="gradient-textgradient-text gradient animate-gradient bg-gradient-text bg-400-percent bg-clip-text font-bold text-transparent">
            get started
          </span>{' '}
          with some data.
        </p>
      </section>

      <section className="flex flex-wrap gap-4">
        {threadHubCardData.map((data, index) => (
          <ThreadHubCard
            key={data.input}
            input={data.input}
            delay={index * 0.6}
          />
        ))}
      </section>
    </article>
  );
}
