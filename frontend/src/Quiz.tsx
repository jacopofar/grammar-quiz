import React, { useState } from 'react'
import { Segment, Table } from 'semantic-ui-react'
import axios from 'axios'
import update from 'immutability-helper';

import ClozeCard from './ClozeCard'

export type Card = {
  fromLanguage: string
  toLanguage: string
  fromId: number
  toId: number
  fromTxt: string
  toTokens: string[]
}

type Answer = {
  fromTxt: string
  toTokens: string[]
  answers: string[]

}

interface Props {
  cards: Card[]
}

function Quiz(props: Props) {
  // the index of the card currently shown
  const [cardIdx, setCardIdx] = useState<number>(0)
  // the answers given so far
  const [answers, setAnswers] = useState<Answer[]>([])


  const handleAnswer = (expected: string[], given: string[], allCorrect: boolean) => {
    const card =  props.cards[cardIdx]
    axios.post('/register_answer', {
      from_id: card.fromId,
      to_id: card.toId,

      expected_answers: expected,
      given_answers: given,
      correct: allCorrect
    })
    setAnswers(update(answers, {$push: [{
      fromTxt: props.cards[cardIdx].fromTxt,
      toTokens: props.cards[cardIdx].toTokens,
      answers: given
    }]}))
  }
  if (cardIdx < props.cards.length){
    return(
    <div>
      <ClozeCard
        card={props.cards[cardIdx]}
        onAnswer={handleAnswer}
        onNextCard={() => {setCardIdx(cardIdx + 1)}}
      />
      <Segment>
          <p>Sentence {cardIdx + 1} of {props.cards.length}</p>
      </Segment>
    </div>
    )

  }
  else{
    return(
      <Table celled>
              <Table.Header>
                <Table.Row>
                  <Table.HeaderCell>Source sentence</Table.HeaderCell>
                  <Table.HeaderCell>Target sentence</Table.HeaderCell>
                  <Table.HeaderCell>Answers</Table.HeaderCell>

                </Table.Row>
              </Table.Header>

            <Table.Body>
              {answers.map(ans =>
              <Table.Row>
                <Table.Cell>{ans.fromTxt}</Table.Cell>
                <Table.Cell>{ans.toTokens.join(' ')}</Table.Cell>
                <Table.Cell>{ans.answers.join(', ')}</Table.Cell>
              </Table.Row>
              )}
            </Table.Body>
          </Table>
    )
  }
}

export default Quiz
