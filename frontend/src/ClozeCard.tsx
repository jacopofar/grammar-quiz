import React from 'react'
import { Divider, Header, Input, Segment } from 'semantic-ui-react'

import { Card } from './Quiz'
import './Cloze.css'

interface ClozeFieldProps {
  clozeContent: string
}


function ClozeField(props: ClozeFieldProps) {
  return (
    <span>
      <Input className="clozefield"/>
    </span>
  )
}

interface CardProps {
  card: Card
}

function ClozeCard(props: CardProps) {
  return (
    <div>
      <Segment>
        <Divider horizontal>{props.card.from_language}</Divider>
        <Header size='large'>{props.card.from_txt}</Header>
        <Divider horizontal>{props.card.to_language}</Divider>
        <Header size='large'>{props.card.to_tokens.map(e => {
          if (e.startsWith('{{')) {
            return ClozeField({clozeContent: e})
          }
          else {
            return <span>{e} </span>
          }
        })}
        </Header>
      </Segment>
    </div>
  )
}

export default ClozeCard
