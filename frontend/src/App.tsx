import React, { useEffect, useState } from 'react'
import { Segment } from 'semantic-ui-react'
import axios from 'axios'

import LanguageSelector from './LanguageSelector'
import Quiz, { Card } from './Quiz'

function App() {
  const [sourceTargetLanguage, setSourceTargetLanguage] = useState<{src: string[], tgt: string}>()
  const [quizCards, setQuizCards] = useState<Card[]>()

  useEffect(() => {
    if (typeof sourceTargetLanguage === 'undefined'){
      return
    }
    async function getQuizCards() {
      const cards = (await axios.post('/draw_cards', {
        target_lang: sourceTargetLanguage?.tgt,
        source_langs: sourceTargetLanguage?.src
      })).data

      setQuizCards(cards)
    }
    getQuizCards()
  }, [sourceTargetLanguage])

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
        {quizCards ?
           <Quiz
            cards={quizCards}/>
          : null
        }
    </div>
  )
}

export default App
