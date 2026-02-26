'use client';

import { useEffect, useState } from 'react';

interface MorphingTextProps {
  texts: string[];
  className?: string;
}

export function MorphingText({ texts, className = '' }: MorphingTextProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % texts.length);
    }, 3000);

    return () => clearInterval(interval);
  }, [texts.length]);

  return (
    <span className={`inline-block transition-all duration-500 ${className}`}>
      {texts[currentIndex]}
    </span>
  );
}
