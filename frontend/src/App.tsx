import React, { useState } from 'react'
import axios from 'axios'
import { Button } from 'semantic-ui-react'

import './App.css';

function App() {
  const [time, setTime] = useState<string>()
  const getTime = async () => {
    const time = await axios.get('/current_time')
    setTime(time.data)
  }
  return (
    <div className="App">
        <p>
             Welcome to grammar-quiz!
        </p>
        <Button primary onClick={getTime}>Click me</Button>
         <p>{time}</p>
    </div>
  );
}

export default App;
