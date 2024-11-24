import './Logo.css'
import Img from '../assets/logo.png'

function Logo() {
  const root = document.getElementsByClassName("app")
  
  
  return (
    <div className={"logo"}>
      <img src={Img} />
      <h1 id={"logo-heading"}>Sky Check</h1>
    </div>
  )
}

export default Logo