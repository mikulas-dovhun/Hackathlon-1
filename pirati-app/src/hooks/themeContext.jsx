import React, { createContext, useState, useEffect } from "react";

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState("light");
  
  useEffect(() => {
    const updateThemeBasedOnTime = () => {
      const hour = new Date().getHours();
      const isDaytime = hour >= 6 && hour < 18;
      setTheme(isDaytime ? "light" : "dark");
    };
    
    updateThemeBasedOnTime();
    
    const interval = setInterval(updateThemeBasedOnTime, 60 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeContext;