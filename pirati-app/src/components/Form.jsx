import './Form.css'
import {useState} from "react"
import Button from './Button.jsx'
import Input from './Input.jsx'

function Form({type, text, action}) {
  const [value, setValue] = useState("");
  
  const handleClick = async (e) => {
    e.preventDefault();
    
    const isFileType = type === "file";
    const formData = new FormData();
    
    if (isFileType && value) {
      formData.append("file", value);
    } else if (!isFileType && value) {
      formData.append("value", value);
    }
    
    try {
      const response = await fetch(action, {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error("Failed to upload");
      }
      
      const data = await response.json();
      console.log("Upload successful:", data);
    } catch (error) {
      console.error("Error uploading:", error);
    }
  };
  
  return (
    <div className={"button"}>
      <Input type={type} value={value} setValue={setValue} />
      <Button to={"/result"} handler={handleClick}>{text}</Button>
    </div>
  )
}

export default Form