import React, { useEffect, useState } from 'react'
import { Segment } from 'semantic-ui-react'
import axios from 'axios'

type DayRevision = {
  day: string
  correct: number
  total: number
}

function MyProfile() {
  const [loggedInUser, setLoggedInUser] = useState<{name: string, id: number}>()
  const [revisions, setRevisions] = useState<DayRevision[]>([])

  // check whether the user is logged in, and the name
  useEffect(() => {
    async function getMyProfile() {
      const identity = (await axios.get('/login/whoami')).data
      setLoggedInUser({name: identity.name, id: identity.id})
    }
    async function getMyRevlogData() {
      const revLog = (await axios.get('/my_revision_stats')).data
      setRevisions(revLog.map((r: any) => ({
        day: r.day,
        correct: r.correct,
        total: r.total
      })))
    }
    getMyProfile()
    getMyRevlogData()
  }, [])

  const totalAnswers = revisions.reduce((acc, cur) => acc + cur.total, 0)
  const totalCorrect = revisions.reduce((acc, cur) => acc + cur.correct, 0)

  return (
    <Segment>
      <h3>Your account</h3>
      <p>Your username is <strong>{loggedInUser?.name}</strong> and your internal id is <strong>{loggedInUser?.id}</strong></p>
      <h3>Your study activity</h3>
      <p>So far you gave <strong>{totalAnswers}</strong> answers.</p>
      <p>Of these, <strong>{totalCorrect}</strong> were correct.</p>
    </Segment>
  )
}

export default MyProfile
