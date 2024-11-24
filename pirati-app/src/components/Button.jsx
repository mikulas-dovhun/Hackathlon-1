import './Button.css'
import {Link} from "react-router-dom";

function Button({children, to, handler}) {
  const element = to == null ? <button>{children}</button> : <Link to={to}>{children}</Link>
  
  return (
    <div className={"button"} onClick={handler}>
      {element}
    </div>
  )
}

export default Button