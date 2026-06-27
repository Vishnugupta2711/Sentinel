import { useEffect } from 'react';
import { useJudgeStore } from '../store/judgeStore';

export const useJudgeShortcuts = () => {
  const { toggleJudgeMode, nextStep, prevStep, resetDemo } = useJudgeStore();

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Don't trigger if user is typing in an input
      if (
        document.activeElement?.tagName === 'INPUT' ||
        document.activeElement?.tagName === 'TEXTAREA'
      ) {
        return;
      }

      const key = event.key.toLowerCase();
      
      if (key === 'j') {
        toggleJudgeMode();
      } else if (key === 'n') {
        nextStep();
      } else if (key === 'p') {
        prevStep();
      } else if (key === 'r') {
        resetDemo();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [toggleJudgeMode, nextStep, prevStep, resetDemo]);
};
