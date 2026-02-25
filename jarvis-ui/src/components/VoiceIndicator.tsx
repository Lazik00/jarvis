import clsx from 'clsx';
import { Mic } from 'lucide-react';
import { JarvisStatus } from '@/hooks/useJarvisState';

interface Props {
  status: JarvisStatus;
  listening: boolean;
  onPushToTalk: () => void;
}

const statusClasses: Record<JarvisStatus, string> = {
  idle: 'border-slate-500/50 bg-slate-700/40',
  listening: 'border-neon shadow-glow bg-cyan-500/20',
  thinking: 'border-purple shadow-purple bg-purple-500/20',
  speaking: 'border-success shadow-success bg-emerald-500/20',
};

export default function VoiceIndicator({ status, listening, onPushToTalk }: Props) {
  return (
    <div className="relative flex items-center justify-center">
      {listening && <div className="absolute h-20 w-20 rounded-full border border-cyan-400/60 animate-pulseRing" />}
      <button
        onClick={onPushToTalk}
        className={clsx(
          'relative z-10 flex h-16 w-16 items-center justify-center rounded-full border transition-all duration-300',
          statusClasses[status]
        )}
      >
        <Mic className="h-7 w-7 text-white" />
      </button>
    </div>
  );
}
