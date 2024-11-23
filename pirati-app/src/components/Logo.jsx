import './Logo.css'
import Img from '../assets/logo.png'

function Logo() {
  return (
    <div className={"logo"}>
      <img src={Img} width={150} height={128} />
    </div>
  )
}

export default Logo