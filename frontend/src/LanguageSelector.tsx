import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { Button, Dropdown, DropdownProps, Label, Form } from 'semantic-ui-react'

interface Props {
  onSelected: (src: string[], tgt: string) => void
}

function LanguageSelector(props: Props) {
  const [languages, setLanguages] = useState<{iso693_3: string, name: string}[]>([])
  const [srcLangs, setSrcLangs] = useState<string[]>([])
  const [tgtLang, setTgtLang] = useState<string>()
  const [errorMsg, setErrorMsg] = useState<string>()

  useEffect(() => {
    async function loadLanguageList() {
        const mods = (await axios.get('/languages')).data
        setLanguages(mods)
    }
    loadLanguageList()
  }, [])

  const handleSourceChange = (e: any, data: DropdownProps ) => {
    setSrcLangs(data.value as string[])
  }
  const handleTargetChange = (e: any, data: DropdownProps ) => {
    // TODO handle the target change, check that it's not in the source
    // if so, show an error
    setTgtLang(data.value as string)
  }
  const sendSelection = () => {
    if (!tgtLang || srcLangs?.length === 0){
      setErrorMsg('Please select a target language and at least 1 known languages')
    }
    else {
      setErrorMsg(undefined)
      props.onSelected(srcLangs, tgtLang)
    }
  }

  return (
    <Form>
      <Form.Field>
      <label>Language to exercise</label>
      <Dropdown
        placeholder='Choose language to exercise'
        fluid
        search
        selection
        clearable
        options={languages
          .filter(l => !srcLangs?.includes(l.iso693_3))
          .map(l => ({key: l.iso693_3, text: l.name, value: l.iso693_3}))}
        onChange={handleTargetChange}
      />

    </Form.Field>
    <Form.Field>
      <label>Known languages</label>
    <Dropdown
      placeholder='Choose known languages...'
      fluid
      multiple
      search
      selection
      clearable
      options={languages
        .filter(l => l.iso693_3 !== tgtLang)
        .map(l => ({key: l.iso693_3, text: l.name, value: l.iso693_3}))}
      onChange={handleSourceChange}
    />
    </Form.Field>
    <Button primary onClick={sendSelection}>Choose languages</Button>
    {errorMsg &&
        <Label prompt color="red">
          {errorMsg}
        </Label>
      }
  </Form>
  )
}

export default LanguageSelector
