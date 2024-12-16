interface CronometerProps {
  time: string;
}

export function Cronometer({ time }: CronometerProps) {
  return (
    <div className="absolute bottom-8 right-16 z-10 mb-8 w-fit rounded-lg bg-white px-2 py-4 shadow-lg">
      <span className="text-center font-mono text-xl">{time}</span>
    </div>
  );
}
