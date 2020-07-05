import React from 'react'
import { Header, Segment } from 'semantic-ui-react'

function Faq() {

  return (
    <Segment>
      <Header as='h3'>What is this?</Header>
      <p>This is a tool that allows you to exercise your grammar using sentences from
      <a href="https://tatoeba.org/">Tatoeba</a>.</p>
      <p>Using <a href="https://en.wikipedia.org/wiki/Spaced_repetition">Spaced Repetition</a> you can better memorize
      the grammar rules of a language, taking note on the cards regarding the reason for some word choice.</p>
      <Header as='h3'>How much does it cost?</Header>
      <p>It's free and <a href="https://github.com/jacopofar/grammar-quiz">the code of the website</a> is publicly
      available.</p>
      <p>This is a project from the <a href="https://blog.tatoeba.org/2020/05/announcing-kodoeba-1.html">Kodoba</a>
      event</p>
      <Header as='h3'>How are the questions generated?</Header>
      <p>The sentences from Tatoeba, around 12 millions at the moment, are processed to extract the words statistically more likely to
         have a grammar role, and compared with multilingual data from
         <a href="https://en.wiktionary.org/wiki/Wiktionary:Main_Page">en.wiktionary</a> to detect and display the dictionary forms</p>
      <Header as='h3'>Do I have to login?</Header>
      <p>No. But without logging in you cannot take custom notes on the sentences and the spaced repetition system
        cannot show you the sentences that were problematic to you in the past.</p>
      <Header as='h3'>A sentence is wrong!</Header>
      <p>You can report wrong sentence with the report button, they will not be shown to you anymore.</p>
      <p>Notice that sentences are written by many people, and sometimes there are more than one correct translations.</p>
      <Header as='h3'>How can I contribute?</Header>
      <p>You can <a href="https://github.com/jacopofar/grammar-quiz">contribute to the code or report bugs</a>,
        and you can contribute to Tatoeba by translating sentences, in particular if your first language is rare.
      </p>
      <Header as='h3'>What do you do with my data?</Header>
       <p>Your personal data (email and credentials) is used only to provide access to the app and not shared with anyone.</p>
       <p>In the future it's possible that the language data will be made public, for example to show which words are more
         often confused with others. If this happens, this data will not include your personal information.</p>
    </Segment>
  )
}

export default Faq
