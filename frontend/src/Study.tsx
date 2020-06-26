import axios from 'axios'
import React, { useEffect, useState } from 'react'
import { Loader, Message, Segment } from 'semantic-ui-react'
import { Link } from 'react-router-dom'


import LanguageSelector from './LanguageSelector'
import Quiz, { Card } from './Quiz'

function Study(props: {loggedIn: boolean}) {
  const [sourceTargetLanguage, setSourceTargetLanguage] = useState<{src: string[], tgt: string}>()
  const [quizCards, setQuizCards] = useState<Card[]>()
  const [loading, setLoading] = useState<boolean>(false)
  const [errorMessage, setErrorMessage] = useState<string>('')

  // draw the cards
  useEffect(() => {
    if (typeof sourceTargetLanguage === 'undefined'){
      return
    }
    async function getQuizCards() {
      try {
        const cards = (await axios.post('/draw_cards', {
          target_lang: sourceTargetLanguage?.tgt,
          source_langs: sourceTargetLanguage?.src
        })).data
        setQuizCards(cards.map((c: any) => ({
          fromId: c.from_id,
          fromLanguage: c.from_language,
          fromTxt: c.from_text,
          toTxt: c.to_text,
          toId: c.to_id,
          toLanguage: c.to_language,
          toTokens: c.to_tokens,
          repetition: false,
          fromLanguageCode: c.from_language_code,
          toLanguageCode: c.to_language_code,
          hint: c.hint,
          explanation: c.explanation
        })))
        setLoading(false)
      }
      catch (e){
        setErrorMessage(`${e} - ${JSON.stringify(e)}`)      }
    }
    getQuizCards()
  }, [sourceTargetLanguage])

  return (
    <>
      <h2>
          Grammar quiz: exercise your grammar with sentences from Tatoeba
      </h2>
      {errorMessage ?
        <Message negative>
          <Message.Header>Something went wrong :(</Message.Header>
          <p>Computers are unrealiable, aren't they?</p>
          <p>Error description: {errorMessage}</p>
        </Message>
      :
        null
      }
      {loading && (!errorMessage)?
          <Loader size='large' active inline='centered'>Loading sentences...</Loader>
      :
        null
      }
      {(sourceTargetLanguage) ? null :
        <Segment>
          <LanguageSelector
            onSelected={(src, tgt) => {
              setLoading(true)
              setSourceTargetLanguage({src, tgt})}}
            loggedIn={props.loggedIn}
          />
          {props.loggedIn ?
            null
          :
            <Link to="/login">
              <Message
                warning
                header='You are not logged in'
                content='Log in to be able to save your progress and take notes.'
              />
            </Link>
          }
        </Segment>
      }
      {quizCards ?
        <Quiz
          cards={quizCards}
          loggedIn={props.loggedIn}/>
        : null
      }
    </>
  )
}

export default Study
