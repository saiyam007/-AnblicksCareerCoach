import React from "react";
import { createRoot } from "react-dom/client";
import Loader from "../components/Loader";

const useLoader = () => {
  let root:any = null;

  const showMainLoader = () => {
    const container = document.getElementById("global-loader");
    if (!container) return;

    // If not already created, create a new root
    if (!root) {
      root = createRoot(container);
    }

    root.render(<Loader />);
  };

  const hideMainLoader = () => {
    const container = document.getElementById("global-loader");
    if (container && root) {
      root.unmount();
      root = null;
    }
  };

  return [showMainLoader, hideMainLoader];
};

export default useLoader;
