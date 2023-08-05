import React, { useEffect, useState } from "react";
import Navbar from "../Navbar";
import "./log.scss";

function Log() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [size, setSize] = useState({
    width: 0,
    height: 0,
  });
  useEffect(() => {
    const handleResize = () => {
      setSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };
    window.addEventListener("resize", handleResize);

    return () => window.removeEventListener("resize", handleResize);
  }, []);

  useEffect(() => {
    if (size.width > 768 && menuOpen) {
      setMenuOpen(false);
    }
  }, [size.width, menuOpen]);


  return (
    <header className="header">
      <div className="header__content">
        <Navbar />

      </div>
    </header>
  );
}

export default Log;