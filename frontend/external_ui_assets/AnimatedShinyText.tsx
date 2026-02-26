'use client';

import React, { CSSProperties, ReactNode } from 'react';

export function AnimatedShinyText({
  children,
  className = '',
  shimmerWidth = 100,
}: {
  children: ReactNode;
  className?: string;
  shimmerWidth?: number;
}) {
  return (
    <p
      style={
        {
          '--shimmer-width': `${shimmerWidth}px`,
        } as CSSProperties
      }
      className={`mx-auto max-w-md text-neutral-600/70 dark:text-neutral-400/70 ${className}`}
    >
      {children}
    </p>
  );
}
