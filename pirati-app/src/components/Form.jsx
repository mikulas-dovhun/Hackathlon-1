import './Form.css';
import { useState } from "react";
import Button from './Button.jsx';
import Input from './Input.jsx';

function Form({ type, text }) {
  const [value, setValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isFinished, setIsFinished] = useState(false);
  
  const handleClick = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch("http://127.0.0.1:5000/api/openai/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json", // Backend expects JSON
        },
        body: JSON.stringify({ message: value }), // Replace "value" with the user's input
      });
      
      if (!response.ok) {
        throw new Error("Failed to communicate with the server");
      }
      
      const data = await response.json();
      console.log("Server response:", data);
      setIsFinished(true);
    } catch (error) {
      console.error("Error:", error);
      setError("An error occurred while communicating with the server.");
      setIsFinished(false);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="form">
      {/* Input and Button Section */}
      {!isFinished && (
        <>
          <Input
            type={type}
            value={value}
            setValue={setValue}
            disabled={loading} // Disable input during loading
          />
          <Button
            to={null}
            handler={handleClick}
            disabled={loading} // Disable button during loading
          >
            {loading ? <div className={"loading"}></div> : text}
          </Button>
        </>
      )}
      
      {/* Error Message */}
      {error && <div className="error">{error}</div>}
      
      {/* Success Message */}
      {isFinished && <div className="answer">Upload successful! Answer</div>}
    </div>
  );
}

export default Form;
