// Based on https://codepen.io/inlet/pen/yLVmPWv.
// Copyright (c) 2018 Patrick Brouwer, distributed under the MIT license.

import { Application } from 'pixi.js';
import { MutableRefObject, ReactNode, useEffect } from 'react';

export type ViewportLike = {
  toWorld(x: number, y: number): { x: number; y: number };
  animate(options: { position?: { x: number; y: number }; scale?: number }): void;
};

export type ViewportProps = {
  app: Application;
  viewportRef?: MutableRefObject<ViewportLike | undefined>;

  screenWidth: number;
  screenHeight: number;
  worldWidth: number;
  worldHeight: number;
  children?: ReactNode;
};

// https://davidfig.github.io/pixi-viewport/jsdoc/Viewport.html
export default function PixiViewport(props: ViewportProps) {
  const { viewportRef, children } = props;

  useEffect(() => {
    if (!viewportRef) {
      return;
    }

    const viewport: ViewportLike = {
      toWorld: (x, y) => ({ x, y }),
      animate: () => {},
    };

    viewportRef.current = viewport;

    return () => {
      if (viewportRef.current === viewport) {
        viewportRef.current = undefined;
      }
    };
  }, [viewportRef]);

  return <>{children}</>;
}
