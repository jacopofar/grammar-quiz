import axios from 'axios'
import React, { useEffect, useState } from 'react'
import { Header, Segment, Table } from 'semantic-ui-react'
import update from 'immutability-helper';

import ClozeCard from './ClozeCard'

export type Card = {
  fromLanguage: string
  toLanguage: string
  fromId: number
  toId: number
  fromTxt: string
  toTxt: string
  toTokens: string[]
  repetition: boolean,
  fromLanguageCode: string
  toLanguageCode: string
  hint: string
  explanation: string
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
  // the answers given so far
  const [cards, setCards] = useState<Card[]>([])
  useEffect(() => {
    // ensure the state is initialized to the cards in the props when they change
    setCards(props.cards.map((c) => c))
    setAnswers([])
    setCardIdx(0)
  }, [props.cards])


  const handleAnswer = (expected: string[], given: string[], allCorrect: boolean) => {
    const card =  cards[cardIdx]
    axios.post('/register_answer', {
      from_id: card.fromId,
      to_id: card.toId,
      expected_answers: expected,
      given_answers: given,
      correct: allCorrect,
      repetition: card.repetition
    })
    setAnswers(update(answers, {$push: [{
      fromTxt: cards[cardIdx].fromTxt,
      toTokens: cards[cardIdx].toTokens,
      answers: given
    }]}))
    if (!allCorrect) {
      //not correct, put a copy back in the queue but with repetition = true
      setCards(update(cards, {$push: [{
        ...card,
        repetition: true
      }]}))
    }
  }

  /**
   * Handle an issue report. It represents some problem the user found on the current
   * card. It is sent to the backend to keep track of it and also the card is removed
   * from the state so the user doesn't see it again in this session.
   * (It is also removed from future sessions, but that logic is in the backend)
  */
  const handleWrongCard = (card: Card, issueType: string, issueDescription: string) => {
    axios.post('/report_issue', {
      from_id: card.fromId,
      to_id: card.toId,
      issue_type: issueType,
      description: issueDescription
    })
    // if a reported card was also wrong (likely), it has to be removed
    if (cards.length > 0
        && cards[cards.length - 1].fromId === card.fromId
        && cards[cards.length - 1].toId === card.toId) {
          // bleah
          setCards(update(cards, {$splice: [[cards.length - 1, 1]]}))
    }
    setCardIdx(cardIdx + 1)
  }

  /**
   * Signals to the backend the free-form notes an user took about a card.
   */
  const takeNote = (card: Card, hint: string, explanation: string) => {
    if (card.hint === hint && card.explanation === explanation) {
      // nothing to change
      return
    }
    axios.post('/take_note', {
      from_id: card.fromId,
      to_id: card.toId,
      hint,
      explanation
    })
    // TODO how does this play with the fact it is not reactive?
    card.hint = hint
    card.explanation = explanation
  }

  if (cardIdx < cards.length){
    return(
    <div>
      <ClozeCard
        card={cards[cardIdx]}
        onAnswer={handleAnswer}
        onNextCard={() => {setCardIdx(cardIdx + 1)}}
        onTrouble={handleWrongCard}
        onNoteTaking={takeNote}
      />
      <Segment>
        <p>Sentence {cardIdx + 1} of {cards.length}, including repetitions</p>
      </Segment>
    </div>
    )

  }
  else{
    return(
      <Segment>
        <Header>Test results</Header>
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
      </Segment>
    )
  }
}

export default Quiz
