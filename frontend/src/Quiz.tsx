import React, { useState } from 'react'
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

  return (
    <div>
      <ClozeCard
        card={props.cards[cardIdx]}
      />
    </div>
  )
}

export default Quiz
