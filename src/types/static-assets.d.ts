declare module '*.png' {
  const src: string;
  export default src;
}

// Spline Viewer 类型定义
declare namespace JSX {
  interface IntrinsicElements {
    'spline-viewer': {
      url: string;
      style?: React.CSSProperties;
      [key: string]: any;
    };
    'hana-viewer': {
      url: string;
      style?: React.CSSProperties;
      [key: string]: any;
    };
  }
}







