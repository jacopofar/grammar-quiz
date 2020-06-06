import React from 'react'
import { Card } from './Quiz'

interface Props {
  card: Card
}

function ClozeCard(props: Props) {
  return (
    <div>
        <p>
        Here will show the UI to answer to a cloze card
        </p>

            {JSON.stringify(props.card)}
    </div>
  )
}

export default ClozeCard
