import React, { useEffect, useState } from 'react'
import { Dropdown, DropdownProps, Form, TextArea } from 'semantic-ui-react'
import { Card } from './Quiz'

interface Props {
  card: Card
  onReportDone: (type?: string, description?: string) => void
}

const issueTypes =[
  {text: 'Wrong answer', value: 'WRONG'},
  {text: 'Multiple valid answers', value: 'MULTI'},
  {text: 'Other', value: 'MULTI'}
]

function CardIssueReport(props: Props) {
  const [issueType, setIssueType] = useState<string>()
  const [issueDescription, setIssueDescription] = useState<string>()

  return (
    <>
      <p>Ops! What's the problem with this question?</p>
      <p>From {props.card.fromLanguage}:</p>
      <p>{props.card.fromTxt}</p>
      <p>To {props.card.toLanguage}:</p>
      <p>{props.card.toTxt}</p>
      <Form>
        <Dropdown
          placeholder='Choose problem type'
          fluid
          selection
          options={issueTypes.map((e, i) => ({...e, key: i}))}
          onChange={(e: any, data: DropdownProps ) => {setIssueType(data.value as string) }}
        />
        <TextArea
          placeholder="what's up?"
          onChange={(e: any) => {setIssueDescription(e.target.value) }}
          />
        <p>You will not get again this sentence</p>
        <Form.Button
          primary
          type='submit'
          onClick={() => props.onReportDone(issueType, issueDescription)}
          >Report issue</Form.Button>
        <Form.Button
          secondary
          onClick={() => props.onReportDone()}
          >Cancel</Form.Button>
      </Form>
      </>
  )
}

export default CardIssueReport
