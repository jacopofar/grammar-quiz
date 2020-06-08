import React, { useState } from 'react'
import { Button, Icon, Segment } from 'semantic-ui-react'
import axios from 'axios'

import ClozeCard from './ClozeCard'

export type Card = {
  from_language: string
  to_language: string
  from_id: number
  to_id: number
  from_txt: string
  to_tokens: string[]
}

interface Props {
  cards: Card[]
}

function Quiz(props: Props) {
  const [cardIdx, setCardIdx] = useState<number>(0)
  // is the user ready to go to the next card?
  const [readyToContinue, setReadyToContinue] = useState<boolean>(false)

  const handleAnswer = (expected: string[], given: string[], allCorrect: boolean) => {
    const card =  props.cards[cardIdx]
    axios.post('/register_answer', {
      from_id: card.from_id,
      to_id: card.to_id,
      expected_answers: expected,
      given_answers: given,
      correct: allCorrect
    })
    // TODO here should also keep track of the answers for an end summary
    setReadyToContinue(true)
  }

  return (
    <div>
      <ClozeCard
        card={props.cards[cardIdx]}
        onAnswer={handleAnswer}
      />
      <Segment>
      <p>Sentence {cardIdx + 1} of {props.cards.length}</p>
        {readyToContinue &&
          <Button
            primary
            onClick={() => {
              //TODO here check whether it was the last, and if so handle the quiz end
              setCardIdx(cardIdx + 1)
              setReadyToContinue(false)
            }}
          > Next card <Icon name='angle right' /></Button>
        }
      </Segment>

    </div>
  )
}

export default Quiz
