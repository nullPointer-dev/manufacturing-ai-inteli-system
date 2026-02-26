'use client';

import React, { useEffect, useState } from 'react';

const CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';

export interface ShuffleProps {
  text: string;
  className?: string;
  tag?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'p' | 'span';
  shuffleTimes?: number;
  duration?: number;
}

const Shuffle: React.FC<ShuffleProps> = ({
  text,
  className = '',
  tag = 'h1',
  shuffleTimes = 3,
  duration = 50
}) => {
  const [displayText, setDisplayText] = useState(text);
  const [isAnimating, setIsAnimating] = useState(true);

  useEffect(() => {
    let frame = 0;
    const totalFrames = text.length * shuffleTimes;
    
    const animate = () => {
      if (frame < totalFrames) {
        const newText = text
          .split('')
          .map((char, index) => {
            if (char === ' ') return ' ';
            
            const charProgress = frame - (index * shuffleTimes);
            
            if (charProgress >= shuffleTimes) {
              return char;
            } else if (charProgress > 0) {
              return CHARS[Math.floor(Math.random() * CHARS.length)];
            } else {
              return CHARS[Math.floor(Math.random() * CHARS.length)];
            }
          })
          .join('');
        
        setDisplayText(newText);
        frame++;
        setTimeout(animate, duration);
      } else {
        setDisplayText(text);
        setIsAnimating(false);
      }
    };

    setTimeout(animate, 100);
  }, [text, shuffleTimes, duration]);

  const Tag = tag as keyof JSX.IntrinsicElements;

  return (
    <Tag className={className}>
      {displayText}
    </Tag>
  );
};

export default Shuffle;
