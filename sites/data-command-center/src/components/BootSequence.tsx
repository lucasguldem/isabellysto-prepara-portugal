import { motion } from 'framer-motion';
import type { CommandCenterSnapshot } from '../types';

type BootSequenceProps = {
  snapshot: CommandCenterSnapshot;
  onSkip: () => void;
};

export default function BootSequence({ snapshot, onSkip }: BootSequenceProps) {
  const lines = [
    'Mounting sanitized Level 2 snapshot',
    `Gold rows indexed: ${snapshot.metadata.source_rows}`,
    `Company graph deduplicated: ${snapshot.metadata.unique_companies}`,
    `Quality gate: ${snapshot.metadata.quality_decision ?? 'not reported'}`,
    'Command modules online: Market / ICP / Recommendation',
  ];

  return (
    <motion.div
      className="boot-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.35 }}
    >
      <div className="boot-core" />
      <div className="boot-panel">
        <p className="eyebrow">ISABELLYSTO DATA COMMAND CENTER</p>
        <h1>System Boot</h1>
        <div className="boot-lines">
          {lines.map((line, index) => (
            <motion.p
              key={line}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.22 }}
            >
              <span>SYS-{String(index + 1).padStart(2, '0')}</span>
              {line}
            </motion.p>
          ))}
        </div>
        <button className="primary-action" onClick={onSkip}>
          Enter Command Center
        </button>
      </div>
    </motion.div>
  );
}
