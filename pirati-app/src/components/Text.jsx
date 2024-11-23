import './Text.css'

function Text({children}) {
  return (
    <div className={"text"}>
      <p>{children}</p>
    </div>
  )
}

export default Text