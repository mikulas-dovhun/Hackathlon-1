import './Menu.css'
import Button from './Button.jsx'
import Text from './Text.jsx'

function Menu() {
  return (
    <div className={"menu"}>
      <Button to={"/search"}>Hľadaj</Button>
      <Text>Alebo</Text>
      <Button to={"/upload"}>Uploaduj súbor</Button>
    </div>
  )
}

export default Menu