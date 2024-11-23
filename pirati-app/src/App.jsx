import './App.css'
import Logo from './components/Logo.jsx'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Menu from './components/Menu.jsx'
import Search from './components/Search.jsx'
import Upload from './components/Upload.jsx'
import ThemeContext from "./hooks/ThemeContext";
import {useContext} from "react";

function App() {
  const theme = useContext(ThemeContext)
  const style = {
    width: "100vw",
    height: "100vh",
    backgroundColor: theme === "light" ? "#ffffff" : "#121212",
    color: theme === "light" ? "#000000" : "#ffffff",
    transition: "background-color 0.5s ease, color 0.5s ease",
  };
  
  return (
    <div className={"app"} style={style}>
      <Logo />
      <BrowserRouter>
        <Routes>
          <Route index element={<Menu /> } />
          <Route path={"/search"} element={<Search />}></Route>
          <Route path={"/upload"} element={<Upload />}></Route>
        </Routes>
      </BrowserRouter>
    </div>
  )
}

export default App