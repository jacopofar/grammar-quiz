import React from 'react'
import { Header, Segment } from 'semantic-ui-react'

function PrivacyNotice() {

  return (
    <Segment>
      <Header>Privacy agreement</Header>
      <p>By registering to this site, either using username and password or with an Single Sign On provider
      (e.g. "Log in using your Google account"), a session cookie is stored on your computer to recognize you across
      visits, and a personal account is created in the internal database. This data is stored and used solely to offer the service,
      for example to let you write notes on the sentences or keep track of which sentences you flagged and your progress.</p>
      <p>Your personal data (name, email, IP address, etc.) is <strong>not shared with any third party</strong>, like
      advertising companies, and no e-mail will be sent unless you provide explicit consent later.</p>

      <p>The data relative to the quiz interactions (for example which words were used to answer, and which answers were
      correct or not) may be published to allow research on grammar usage, but it will be without your personal user data.</p>
    </Segment>
  )
}

export default PrivacyNotice
