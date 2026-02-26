'use client';

import React, { ReactNode } from 'react';

interface AuroraTextProps {
  children: ReactNode;
  className?: string;
}

export function AuroraText({ children, className = '' }: AuroraTextProps) {
  return (
    <span
      className={`inline-block bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent animate-pulse ${className}`}
    >
      {children}
    </span>
  );
}
