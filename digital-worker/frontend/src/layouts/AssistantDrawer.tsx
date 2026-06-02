import React, { useEffect } from 'react';
import { Drawer } from 'antd';
import { useAssistantStore } from '@/stores/useAssistantStore';
import AIChatBox from '@/components/AIChatBox';

const AssistantDrawer: React.FC = () => {
  const { visible, setVisible, loadSessions } = useAssistantStore();

  useEffect(() => {
    if (visible) {
      loadSessions();
    }
  }, [visible, loadSessions]);

  return (
    <>
      {/* Floating trigger button */}
      {!visible && (
        <button
          className="assistant-float-btn"
          onClick={() => setVisible(true)}
          title="数字员工小智"
        >
          <span className="whale-bounce">
          <svg width="40" height="40" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#1677ff" />
                <stop offset="100%" stopColor="#4096ff" />
              </linearGradient>
              <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="2" stdDeviation="4" floodColor="rgba(0,0,0,0.15)" />
              </filter>
            </defs>

            {/* Background circle */}
            <circle cx="100" cy="100" r="96" fill="url(#bgGrad)" filter="url(#shadow)" />

            {/* Whale body */}
            <ellipse cx="108" cy="108" rx="42" ry="28" fill="white" />

            {/* Whale underside belly highlight */}
            <ellipse cx="108" cy="118" rx="34" ry="16" fill="rgba(22,119,255,0.06)" />

            {/* Tail */}
            <path d="M146 102 L175 88 L168 110 L188 118 L155 118 Z" fill="white" />

            {/* Dorsal fin */}
            <path d="M120 80 C125 72, 130 75, 135 82 Z" fill="white" opacity="0.9" />

            {/* Eye */}
            <circle cx="85" cy="100" r="4.5" fill="#1677ff" />
            <circle cx="86" cy="99" r="1.8" fill="white" />

            {/* Smile */}
            <path d="M75 114 Q88 124 108 119" stroke="#1677ff" strokeWidth="2.5" fill="none" strokeLinecap="round" />

            {/* Cheek blush */}
            <ellipse cx="80" cy="112" rx="7" ry="4" fill="#1677ff" opacity="0.08" />

            {/* Water spout */}
            <path d="M88 82 C82 66, 74 58, 66 52" stroke="rgba(255,255,255,0.7)" strokeWidth="2.5" fill="none" strokeLinecap="round" />
            <path d="M94 80 C92 64, 96 52, 96 44" stroke="rgba(255,255,255,0.5)" strokeWidth="2.5" fill="none" strokeLinecap="round" />
            <path d="M100 82 C106 68, 112 58, 118 54" stroke="rgba(255,255,255,0.6)" strokeWidth="2" fill="none" strokeLinecap="round" />

            {/* Water droplets */}
            <circle cx="64" cy="49" r="2.5" fill="rgba(255,255,255,0.6)" />
            <circle cx="96" cy="40" r="2.5" fill="rgba(255,255,255,0.5)" />
            <circle cx="120" cy="50" r="2" fill="rgba(255,255,255,0.4)" />
            <circle cx="82" cy="42" r="1.8" fill="rgba(255,255,255,0.3)" />
          </svg>
          </span>
        </button>
      )}

      <Drawer
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>💬</span>
            <span>数字员工小智</span>
          </div>
        }
        placement="right"
        width={480}
        open={visible}
        onClose={() => setVisible(false)}
        destroyOnClose
        styles={{
          body: {
            padding: 0,
            display: 'flex',
            flexDirection: 'column',
            height: 'calc(100% - 55px)',
          },
        }}
      >
        <AIChatBox onClose={() => setVisible(false)} />
      </Drawer>
    </>
  );
};

export default AssistantDrawer;
