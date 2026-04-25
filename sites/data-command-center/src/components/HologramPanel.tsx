import type { PropsWithChildren } from 'react';

type HologramPanelProps = PropsWithChildren<{
  className?: string;
  title?: string;
  eyebrow?: string;
}>;

export default function HologramPanel({ children, className = '', title, eyebrow }: HologramPanelProps) {
  return (
    <section className={`holo-panel ${className}`}>
      {eyebrow && <p className="eyebrow">{eyebrow}</p>}
      {title && <h2>{title}</h2>}
      {children}
    </section>
  );
}
