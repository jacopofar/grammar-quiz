import React from 'react'
import { render } from '@testing-library/react'
import App from './App'

// not really a meaningful test :( But TDD in this context seems unlikely
test('renders the title', () => {
  const { getByText } = render(<App />)
  const welcomeText = getByText(/Grammar quiz/i)
  expect(welcomeText).toBeInTheDocument()
})
