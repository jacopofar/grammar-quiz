import React, { useEffect, useState } from 'react'
import { Divider, Form, Header, Icon, Input, Label, Segment } from 'semantic-ui-react'
import update from 'immutability-helper';

import { Card } from './Quiz'
import './ClozeCard.css'

/**
 * Extract the answer part from a Cloze.
 * E.g. from '{{c1::Paris}}' gets 'Paris'
*/
const answerFromCloze = (cloze: string) => {
  const match = cloze.match(/^\{\{c\d+:.*:(.+)\}\}$/)
  if (!match) {
    throw Error(`Invalid cloze ${cloze}`)
  }
  else {
    return match[1]
  }
}

const isAnswerOK = (expected: string, answer: string) => {
  if (answer === expected) {
    return true
  }
  // tolerate an extra punctuation mark
  if (/['.,?!;。、？！']/.test(expected.slice(-1))){
    if (expected.slice(0, -1) === answer){
      return true
    }
  }
  // tolerate empty cloze as space
  if (expected === '-' && answer === ''){
    return true
  }
  return false
}

interface ClozeFieldProps {
  clozeContent: string
  showCorrect: boolean
  onAnswer: (answer: string) => void
  autoFocus: boolean
}


function ClozeField(props: ClozeFieldProps) {
  const [answer, setAnswer] = useState<string>('')
  const expectedAnswer = answerFromCloze(props.clozeContent)
  return (
    <span>
      <Input
        autoFocus={props.autoFocus}
        className="clozefield"
        onChange={(e) => {
            props.onAnswer(e.target.value)
            setAnswer(e.target.value)
          }}
      />
      {props.showCorrect &&
        <>{(isAnswerOK(expectedAnswer, answer) ?
          <Label basic color='green' pointing='left'><Icon name='check' /></Label>
        :
          <Label basic color='red' pointing='left'>{expectedAnswer}<span> </span></Label>
          )}
        </>
      }
      </span>
  )
}

interface CardProps {
  card: Card,
  onAnswer: (expected: string[], given: string [], allCorrect: boolean) => void
  onNextCard: () => void
}

function ClozeCard(props: CardProps) {
  const [clozes, setClozes] = useState<string[]>(['ERROR'])
  const [answers, setAnswers] = useState<string[]>(['ERROR'])
  const [showAnswers, setShowAnswers] = useState<boolean>(false)

  useEffect(() => {
    // when the changes, hide the tips and reset the previous answers
    setShowAnswers(false)
    const newClozes = props.card.toTokens.filter(t => t.startsWith('{{'))
    setClozes(newClozes)
    setAnswers(newClozes.map(e => ''))
  }, [props.card])

  const nextAction = () => {
    if (showAnswers){
      props.onNextCard()
    }
    else{
      setShowAnswers(true)
      props.onAnswer(clozes.map(answerFromCloze), answers, answers.filter((a, i) => {
        return !isAnswerOK(answerFromCloze(clozes[i]), a)
      }).length === 0)
    }
  }

  return (
    <div>
      <Segment>
        <Divider horizontal>{props.card.fromLanguage}</Divider>
        <Header size='medium'>{props.card.fromTxt}</Header>
        <Divider horizontal>{props.card.toLanguage}</Divider>
        <Form onSubmit={nextAction}>
          <Header size='medium'>{props.card.toTokens.map((e, i) => {
            const idx=clozes.indexOf(e)
            if (idx !== -1) {
              return <ClozeField
                  autoFocus={idx == 0}
                  key={`${props.card.toId}-${idx}`}
                  clozeContent={e}
                  showCorrect={showAnswers}
                  onAnswer={(ans) => setAnswers(update(answers, {[idx]: {$set: ans}}))}
                />
            }
            else {
              return <span key={i}>{e} </span>
            }
          })}
          </Header>
          {showAnswers ?
            <Form.Button primary type='submit'> Next card <Icon name='angle right' /></Form.Button>
          :
            <Form.Button type='submit' positive><Icon name='check' />Submit</Form.Button>
        }
        </Form>
      </Segment>
    </div>
  )
}

export default ClozeCard
