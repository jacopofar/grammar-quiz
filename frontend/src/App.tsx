import React, { useEffect, useState } from 'react'
import { Grid, Segment } from 'semantic-ui-react'
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

      setQuizCards(cards.map((c: any) => ({
        fromId: c.from_id,
        fromLanguage: c.from_language,
        fromTxt: c.from_txt,
        toId: c.to_id,
        toLanguage: c.to_language,
        toTokens: c.to_tokens
      })))
    }
    getQuizCards()
  }, [sourceTargetLanguage])

  return (
    <Grid padded>
      <Grid.Column width={2}></Grid.Column>
      <Grid.Column width={12}>
        <h2>
             Grammar quiz, test your grammar with sentences from Tatoeba
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
      </Grid.Column>
      <Grid.Column width={2}></Grid.Column>

    </Grid>
  )
}

export default App
