import React, { useEffect, useRef } from 'react';

export function FloatingEye() {
  const leftEyeRef = useRef<HTMLDivElement>(null);
  const leftPupilRef = useRef<HTMLDivElement>(null);
  const rightEyeRef = useRef<HTMLDivElement>(null);
  const rightPupilRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      // 处理左眼
      if (leftEyeRef.current && leftPupilRef.current) {
        const eye = leftEyeRef.current;
        const pupil = leftPupilRef.current;
        
        const rect = eye.getBoundingClientRect();
        const eyeCenterX = rect.left + rect.width / 2;
        const eyeCenterY = rect.top + rect.height / 2;
        
        const deltaX = e.clientX - eyeCenterX;
        const deltaY = e.clientY - eyeCenterY;
        const angle = Math.atan2(deltaY, deltaX);
        
        const maxDistance = 6; // 小眼睛的瞳孔移动距离更小
        const distance = Math.min(
          Math.sqrt(deltaX * deltaX + deltaY * deltaY) / 5,
          maxDistance
        );
        
        const pupilX = Math.cos(angle) * distance;
        const pupilY = Math.sin(angle) * distance;
        
        pupil.style.transform = `translate(calc(-50% + ${pupilX}px), calc(-50% + ${pupilY}px))`;
      }

      // 处理右眼
      if (rightEyeRef.current && rightPupilRef.current) {
        const eye = rightEyeRef.current;
        const pupil = rightPupilRef.current;
        
        const rect = eye.getBoundingClientRect();
        const eyeCenterX = rect.left + rect.width / 2;
        const eyeCenterY = rect.top + rect.height / 2;
        
        const deltaX = e.clientX - eyeCenterX;
        const deltaY = e.clientY - eyeCenterY;
        const angle = Math.atan2(deltaY, deltaX);
        
        const maxDistance = 6;
        const distance = Math.min(
          Math.sqrt(deltaX * deltaX + deltaY * deltaY) / 5,
          maxDistance
        );
        
        const pupilX = Math.cos(angle) * distance;
        const pupilY = Math.sin(angle) * distance;
        
        pupil.style.transform = `translate(calc(-50% + ${pupilX}px), calc(-50% + ${pupilY}px))`;
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  // 渲染单个眼睛的函数
  const renderEye = (
    eyeRef: React.RefObject<HTMLDivElement>,
    pupilRef: React.RefObject<HTMLDivElement>
  ) => (
    <div
      ref={eyeRef}
      style={{
        position: 'relative',
        width: '28px',
        height: '28px',
      }}
    >
      {/* 眼白 */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          borderRadius: '50%',
          backgroundColor: '#FFFFFF',
          border: '1.5px solid #E9E4DD',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.06)',
        }}
      >
        {/* 瞳孔 */}
        <div
          ref={pupilRef}
          style={{
            position: 'absolute',
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: '#222222',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.2), inset 0 1px 2px rgba(255, 255, 255, 0.1)',
            transition: 'transform 0.2s ease-out',
          }}
        />
        {/* 高光点 */}
        <div
          style={{
            position: 'absolute',
            width: '3px',
            height: '3px',
            borderRadius: '50%',
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            top: '35%',
            left: '35%',
            pointerEvents: 'none',
          }}
        />
      </div>
    </div>
  );

  return (
    <div
      ref={containerRef}
      style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        display: 'flex',
        gap: '8px',
        alignItems: 'center',
        zIndex: 99999,
        pointerEvents: 'none',
      }}
    >
      {renderEye(leftEyeRef, leftPupilRef)}
      {renderEye(rightEyeRef, rightPupilRef)}
    </div>
  );
}

