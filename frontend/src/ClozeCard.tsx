import React, { useEffect, useState } from 'react'
import { Button, Divider, Form, Header, Icon, Input, Label, Modal, Segment } from 'semantic-ui-react'
import update from 'immutability-helper';

import { Card } from './Quiz'
import CardIssueReport from './CardIssueReport'
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

  // tolerate an extra punctuation mark
  if (/['.,?!;。、？！' ]/.test(expected.slice(-1))) {
    expected = expected.slice(0, -1)
  }
  if (/['.,?!;。、？！' ]/.test(answer.slice(-1))) {
    answer = answer.slice(0, -1)
  }
  if (answer === expected) {
    return true
  }
  // tolerate empty cloze as space
  if (expected === '-' && (answer === '' || answer === ' ')) {
    return true
  }
  return false
}

interface ClozeFieldProps {
  clozeContent: string
  showCorrect: boolean
  onAnswer: (answer: string) => void
  autoFocus: boolean
  hintDirection: 'left' | 'right'
}


function ClozeField(props: ClozeFieldProps) {
  const [answer, setAnswer] = useState<string>('')
  const expectedAnswer = answerFromCloze(props.clozeContent)
  return (
    <span>
      <Input
        autoFocus={props.autoFocus}
        autoCapitalize="off"
        autoComplete="off"
        autoCorrect="off"
        className="clozefield"
        onChange={(e) => {
            props.onAnswer(e.target.value)
            setAnswer(e.target.value)
          }}
      />
      {props.showCorrect &&
        <>{(isAnswerOK(expectedAnswer, answer) ?
          <Label basic color='green' pointing={props.hintDirection}><Icon name='check' /></Label>
        :
          <Label basic color='red' pointing={props.hintDirection}>{expectedAnswer}<span> </span></Label>
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
  onTrouble: (card: Card, issueType: string, issueDescription: string) => void
}

function ClozeCard(props: CardProps) {
  const [clozes, setClozes] = useState<string[]>(['ERROR'])
  const [answers, setAnswers] = useState<string[]>(['ERROR'])
  const [showAnswers, setShowAnswers] = useState<boolean>(false)
  const [inIssueModal, setInIssueModal] = useState<boolean>(false)

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

  const textDirection = (lang: string) => {
    if ([
      "ara", "arq","heb", "arz", "uig", "pes", "acm", "urd", "yid", "pnb", "oar", "ary", "aii", "afb", "pus",
      "snd", "div", "otk", "tmr", "syc", "phn", "jpa"
      ].includes(lang)){
        return 'rtl'
      }
      else{
        return 'ltr'
      }
  }

  return (
    <div>
      <Segment>
        <Divider horizontal>{props.card.fromLanguage}</Divider>
        <Header size='medium' dir={textDirection(props.card.fromLanguageCode)}>{props.card.fromTxt}</Header>
        <Divider horizontal>{props.card.toLanguage}</Divider>
        <Form onSubmit={nextAction} dir={textDirection(props.card.toLanguageCode)}>
          <Header size='medium'>{props.card.toTokens.map((e, i) => {
            const idx=clozes.indexOf(e)
            if (idx !== -1) {
              return <ClozeField
                  autoFocus={idx === 0}
                  key={`${props.card.toId}-${idx}-c`}
                  clozeContent={e}
                  showCorrect={showAnswers}
                  onAnswer={(ans) => setAnswers(update(answers, {[idx]: {$set: ans}}))}
                  hintDirection={textDirection(props.card.toLanguageCode) === 'rtl' ? 'right' : 'left'}
                />
            }
            else {
              return <span key={`${props.card.toId}-${i}-t`}>{e}</span>
            }
          })}
          </Header>
          {showAnswers ?
          <>
            <Form.Button primary type='submit'> Next card <Icon name='angle right' /></Form.Button>
            <Button
              icon
              labelPosition='left' color='red' onClick={(event) => {
                setInIssueModal(true)
                // it's in a form, prevent submit
                event.preventDefault()
                }}>
              <Icon name='warning sign' />
              Report issue
            </Button>
            </>
          :
            <Form.Button type='submit' positive><Icon name='check' />Submit</Form.Button>
          }
        </Form>
      </Segment>
      <Modal size='large' open={inIssueModal} onClose={() => setInIssueModal(false)}>
        <Modal.Header>Report a problem with the sentence</Modal.Header>
        <Modal.Content>
          <CardIssueReport
            card={props.card}
            onReportDone={(type?: string, description?: string) => {
              if(typeof type === 'undefined') {
                setInIssueModal(false)
              }
              else{
                props.onTrouble(props.card, type, description || '')
                setInIssueModal(false)
              }
            }}
          />
        </Modal.Content>
      </Modal>
    </div>
  )
}

export default ClozeCard
