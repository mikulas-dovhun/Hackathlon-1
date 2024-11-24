import {useState} from "react";
import './Input.css'

function Input({value, setValue, type}) {
  const handleChange = (e) => {
    if (type === "file") {
      setValue(e.target.files[0]);
    } else {
      setValue(e.target.value);
    }
  }
  
  return (
    <div className={"input"}>
      <input type={type} value={type === "file" ? undefined : value} onChange={handleChange}/>
    </div>
  )
}

export default Input