import React, { useState } from 'react'
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
{/* Example ClozeCard
       <ClozeCard
        card={{
          from_language: 'Italian',
          to_language: 'English',
          from_id: 1,
          to_id: 23,
          from_txt: 'Mangio la mela ora',
          to_tokens: ['{{c1::I}}', 'eat', '{{c2::the}}', 'apple', '{{c3::now}}']
        }}
      /> */}

interface ClozeFieldProps {
  clozeContent: string
  showCorrect: boolean
  onAnswer: (answer: string) => void
}


function ClozeField(props: ClozeFieldProps) {
  const [answer, setAnswer] = useState<string>('')
  const expectedAnswer = answerFromCloze(props.clozeContent)
  return (
    <span>
      <Input
        className="clozefield"
        onChange={(e) => {
            props.onAnswer(e.target.value)
            setAnswer(e.target.value)
          }}
      />
      {props.showCorrect &&
        <>{(expectedAnswer === answer ?
          <Label basic color='green' pointing='left'>
            <Icon name='check' />
          </Label>
        :
          <Label basic color='red' pointing='left'>
            {expectedAnswer}
          </Label>
          )}
          <span> </span>
          </>
      }

      </span>
  )
}

interface CardProps {
  card: Card
}

function ClozeCard(props: CardProps) {
  const clozes: string[] = props.card.to_tokens.filter(t => t.startsWith('{{'))
  const [answers, setAnswers] = useState<string[]>(clozes.map(e => ''))
  const [showAnswers, setShowAnswers] = useState<boolean>(false)

  const submitAnswers = () => {
    setShowAnswers(true)
  }

  return (
    <div>
      <Segment>
        <Divider horizontal>{props.card.from_language}</Divider>
        <Header size='large'>{props.card.from_txt}</Header>
        <Divider horizontal>{props.card.to_language}</Divider>
        <Form onSubmit={submitAnswers}>
          <Header size='large'>{props.card.to_tokens.map((e) => {
            const idx=clozes.indexOf(e)
            if (idx !== -1) {
              return <ClozeField
                  clozeContent={e}
                  showCorrect={showAnswers}
                  onAnswer={(ans) => setAnswers(update(answers, {[idx]: {$set: ans}}))}
                />
            }
            else {
              return <span>{e} </span>
            }
          })}
          </Header>
          <Form.Button type='submit' positive><Icon name='check' />Submit</Form.Button>
        </Form>
      </Segment>
    </div>
  )
}

export default ClozeCard
