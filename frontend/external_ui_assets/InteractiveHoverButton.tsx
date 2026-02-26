'use client';

import React, { ReactNode } from 'react';

interface InteractiveHoverButtonProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}

export function InteractiveHoverButton({
  children,
  className = '',
  onClick,
}: InteractiveHoverButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`group relative inline-flex items-center justify-center overflow-hidden rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 px-8 py-3 font-bold text-white shadow-2xl transition-all duration-300 hover:scale-105 hover:shadow-cyan-500/50 ${className}`}
    >
      <span className="relative z-10">{children}</span>
      <div className="absolute inset-0 -z-10 bg-gradient-to-r from-cyan-400 to-blue-500 opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
    </button>
  );
}
