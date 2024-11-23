import './Search.css'
import Button from './Button.jsx'
import Form from './Form.jsx'
import {useState} from "react";

function Search() {
  return (
    <div className={"search"}>
      <Form type={"text"} text={"Hľadaj"} action={""}></Form>
    </div>
  )
}

export default Search