import React, { useEffect, useState } from 'react'
import { Dropdown, DropdownProps, Form, TextArea } from 'semantic-ui-react'
import { Card } from './Quiz'

interface Props {
  card: Card
}

const issueTypes =[
  {text: 'Wrong answer', value: 'WRONG'},
  {text: 'Multiple valid answers', value: 'MULTI'},
  {text: 'Other', value: 'MULTI'}
]

function CardIssueReport(props: Props) {
  const [issueType, setIssueType] = useState<string>()

  const handleIssueChange = (e: any, data: DropdownProps ) => {
    setIssueType(data.value as string)
  }

  return (
    <>
      <p>What's the problem with this question?</p>
      <p>From:</p>
      <p>{props.card.fromTxt}</p>
      <p>To:</p>
      <p>{props.card.toTxt}</p>
      <Form>
      <Dropdown
          placeholder='Choose problem type'
          fluid
          selection
          options={issueTypes.map((e, i) => ({...e, key: i}))}
          onChange={handleIssueChange}
        />
        <TextArea placeholder='Tell us more' />
      </Form>
      </>
  )
}

export default CardIssueReport
