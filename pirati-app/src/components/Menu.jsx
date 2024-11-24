import './Menu.css'
import Button from './Button.jsx'
import {useEffect} from "react";

function Menu() {
  
  return (
    <div className={"menu"}>
      <Button to={"/search"}>Hľadaj</Button>
      <Button to={"/upload"}>Uploaduj dataset</Button>
    </div>
  )
}

export default Menu