import './App.css';
import Logo from './components/Logo.jsx';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Menu from './components/Menu.jsx';
import Search from './components/Search.jsx';
import Upload from './components/Upload.jsx';
import ThemeContext from "./hooks/ThemeContext";
import { useContext } from "react";
import bgDayVideo from './assets/day.mp4';
import bgNightVideo from './assets/night.mp4';

function App() {
  const theme = useContext(ThemeContext);
  
  return (
    <div className="app">
      <video
        className="background-video"
        autoPlay
        muted
        loop
        playsInline
      >
        <source src={theme === "day" ? bgDayVideo : bgNightVideo} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      
      <Logo />
      <BrowserRouter>
        <Routes>
          <Route index element={<Menu />} />
          <Route path="/search" element={<Search />} />
          <Route path="/upload" element={<Upload />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
