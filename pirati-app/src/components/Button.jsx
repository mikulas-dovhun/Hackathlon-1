import './Button.css'
import {Link} from "react-router-dom";

function Button({children, to, handler}) {
  return (
    <div className={"button"} onClick={handler}>
      <Link to={to}>{children}</Link>
    </div>
  )
}

export default Button