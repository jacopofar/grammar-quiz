import React, { useState } from 'react'
import { Segment } from 'semantic-ui-react'

import LanguageSelector from './LanguageSelector'
import Quiz from './Quiz'
import './App.css';

function App() {
  const [sourceTargetLanguage, setSourceTargetLanguage] = useState<{src: string[], tgt: string}>()

  return (
    <div className="App">
        <h2>
             Welcome to grammar-quiz!
        </h2>
        {sourceTargetLanguage ? null :
          <Segment>
            <LanguageSelector
              onSelected={(src, tgt) => setSourceTargetLanguage({src, tgt})}
            />
          </Segment>
        }

        <p>Insert here quiz once languages are selected. The Quiz will have props for the initial N questions and a prop for the answer callback</p>
         <Quiz />
    </div>
  );
}

export default App;
