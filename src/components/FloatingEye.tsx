import React, { useEffect, useRef, useState } from 'react';

export function FloatingEye() {
  const leftEyeRef = useRef<HTMLDivElement>(null);
  const leftPupilRef = useRef<HTMLDivElement>(null);
  const rightEyeRef = useRef<HTMLDivElement>(null);
  const rightPupilRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // 从 localStorage 读取保存的位置，如果没有则使用默认位置
  const getInitialPosition = () => {
    const saved = localStorage.getItem('floatingEyePosition');
    if (saved) {
      try {
        const { x, y } = JSON.parse(saved);
        return { x, y };
      } catch (e) {
        // 如果解析失败，使用默认值
      }
    }
    return { x: null, y: null }; // 使用 bottom 和 right 作为默认
  };

  const [position, setPosition] = useState(getInitialPosition);
  const [isDragging, setIsDragging] = useState(false);
  const dragOffsetRef = useRef({ x: 0, y: 0 });
  const positionRef = useRef(position);
  
  // 同步 positionRef 和 position state
  useEffect(() => {
    positionRef.current = position;
  }, [position]);

  // 拖动处理
  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    
    const rect = containerRef.current.getBoundingClientRect();
    const offsetX = e.clientX - rect.left;
    const offsetY = e.clientY - rect.top;
    
    dragOffsetRef.current = { x: offsetX, y: offsetY };
    setIsDragging(true);
    e.preventDefault(); // 防止文本选择
  };

  // 鼠标移动和眼睛跟随处理
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging && containerRef.current) {
        const newX = e.clientX - dragOffsetRef.current.x;
        const newY = e.clientY - dragOffsetRef.current.y;
        
        // 限制在视窗内
        const maxX = window.innerWidth - (containerRef.current.offsetWidth || 64);
        const maxY = window.innerHeight - (containerRef.current.offsetHeight || 28);
        
        const clampedX = Math.max(0, Math.min(newX, maxX));
        const clampedY = Math.max(0, Math.min(newY, maxY));
        
        const newPosition = { x: clampedX, y: clampedY };
        setPosition(newPosition);
        positionRef.current = newPosition;
      } else {
        // 处理眼睛跟随鼠标（仅在非拖动状态）
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
      }
    };

    const handleMouseUp = () => {
      if (isDragging) {
        setIsDragging(false);
        // 保存位置到 localStorage
        const currentPos = positionRef.current;
        if (currentPos.x !== null && currentPos.y !== null) {
          localStorage.setItem('floatingEyePosition', JSON.stringify(currentPos));
        }
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

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

  // 计算容器样式
  const containerStyle: React.CSSProperties = {
    position: 'fixed',
    display: 'flex',
    gap: '8px',
    alignItems: 'center',
    zIndex: 99999,
    cursor: isDragging ? 'grabbing' : 'grab',
    userSelect: 'none',
    transition: isDragging ? 'none' : 'opacity 0.2s ease-out',
    ...(position.x !== null && position.y !== null
      ? {
          left: `${position.x}px`,
          top: `${position.y}px`,
          bottom: 'auto',
          right: 'auto',
        }
      : {
          bottom: '20px',
          right: '20px',
        }),
    ...(isDragging && {
      opacity: 0.85,
    }),
  };

  return (
    <div
      ref={containerRef}
      onMouseDown={handleMouseDown}
      style={containerStyle}
    >
      {renderEye(leftEyeRef, leftPupilRef)}
      {renderEye(rightEyeRef, rightPupilRef)}
    </div>
  );
}

