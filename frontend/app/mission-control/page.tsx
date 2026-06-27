"use client";

import React, { useEffect } from 'react';
import { ThreeColumnLayout } from './../../components/layouts/ThreeColumnLayout';
import { TopBar } from './../../components/layouts/TopBar';
import { LeftPanel } from './../../components/layouts/LeftPanel';
import { RightPanel } from './../../components/layouts/RightPanel';
import { BottomPanel } from './../../components/layouts/BottomPanel';
import { InteractivePlantView } from './../../components/plant/InteractivePlantView';
import { useWorldStateStore } from './../../store/worldState';
import { useIntelligenceStore } from './../../store/intelligence';
import { useDemoStore } from './../../store/demo';

export default function MissionControlPage() {
  const wsConnect = useWorldStateStore(state => state.connect);
  const wsDisconnect = useWorldStateStore(state => state.disconnect);
  
  const intelConnect = useIntelligenceStore(state => state.connect);
  const intelDisconnect = useIntelligenceStore(state => state.disconnect);

  const demoConnect = useDemoStore(state => state.connect);
  const demoDisconnect = useDemoStore(state => state.disconnect);

  useEffect(() => {
    console.log("MissionControlPage mounted!");
    console.log("WS_BASE is", process.env.NEXT_PUBLIC_WS_URL);
    // Initiate connections when Mission Control mounts
    wsConnect();
    intelConnect();
    demoConnect();

    return () => {
      // Cleanup on unmount
      wsDisconnect();
      intelDisconnect();
      demoDisconnect();
    };
  }, [wsConnect, wsDisconnect, intelConnect, intelDisconnect, demoConnect, demoDisconnect]);

  console.log("MissionControlPage RENDERED ON CLIENT/SERVER! wsConnect is:", typeof wsConnect);

  return (
    <ThreeColumnLayout
      topBar={<TopBar />}
      leftPanel={<LeftPanel />}
      centerPanel={<InteractivePlantView />}
      rightPanel={<RightPanel />}
      bottomPanel={<BottomPanel />}
    />
  );
}
