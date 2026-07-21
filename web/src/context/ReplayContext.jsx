import React, { createContext, useContext, useState } from 'react';

const ReplayContext = createContext({
  isReplaying: false,
  playbackSpeed: 1,
  startReplay: () => {},
  stopReplay: () => {},
  setSpeed: () => {}
});

export function ReplayProvider({ children }) {
  const [isReplaying, setIsReplaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);

  const startReplay = () => setIsReplaying(true);
  const stopReplay = () => setIsReplaying(false);
  const setSpeed = (speed) => setPlaybackSpeed(speed);

  return (
    <ReplayContext.Provider value={{ isReplaying, playbackSpeed, startReplay, stopReplay, setSpeed }}>
      {children}
    </ReplayContext.Provider>
  );
}

export function useReplay() {
  return useContext(ReplayContext);
}
