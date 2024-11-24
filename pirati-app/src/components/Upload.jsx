import './Upload.css'
import Form from './Form.jsx'
import Text from './Text.jsx'

function Upload() {
  return (
    <div className={"search"}>
      <Form type={"file"} text={"Uploadni dataset"} action={""}></Form>
    </div>
  )
}

export default Upload