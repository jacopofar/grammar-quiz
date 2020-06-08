import React, { useState } from 'react'
import { Button, Icon, Segment } from 'semantic-ui-react'

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

  return (
    <div>
      <p>Sentence {cardIdx + 1} of {props.cards.length}</p>
      <ClozeCard
        card={props.cards[cardIdx]}
        onAnswer={(expected, given) => {
          // TODO here send the result to the server, and keep track of it for the end summary
          setReadyToContinue(true)
          console.log({expected, given})
        }}
      />
      {readyToContinue &&
        <Segment>
          <Button
            primary
            onClick={() => {
              //TODO here check whether it was the last, and if so handle the quiz end
              setCardIdx(cardIdx + 1)
              setReadyToContinue(false)
            }}
          > Next card <Icon name='angle right' /></Button>
        </Segment>
      }

    </div>
  )
}

export default Quiz
