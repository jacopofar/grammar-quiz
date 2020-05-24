# grammar-quiz
Online cloze deletion tool focused on grammar

This is a project for the [Kodoeba event](https://blog.tatoeba.org/2020/05/announcing-kodoeba-1.html) organized by Tatoeba.

This project aims at using the vast sentence database of Tatoeba to generate grammar exercises, in particular cloze deletions, that can be used both to study and to evaluate the usage of a language.

This project will be completely FOSS and the produced data will be published when possible and non-personal (e.g. user account data).

The event officially starts at June 1st and the accepted participants are not announced yet, for now I'm writing this page to document the tentative roadmap I have in mind.

## Roadmap

This will have to be moved into proper GH issues, with milestones

Week 1: generate simple cloze deletions from the CSV using word frequency and store them into a DB. Also produce a JSON output?

Week 2: create a minimal webapp (in English and with no real authentication) to randomly draw cards and answer for a given deck

Week 3: add flagging the cards content, add a process to register and authenticate, publish the dev version somewhere. presumably use k8s but should be possible to execute without

Week 4: allow the user to write a comment on a card, add a up/down vote mechanism on comments. Alternatively, let the tag be visible only from the user ho wrote them.

Week 5: if there's time, add lemmatization for some language and reimport

Week 6: Improve the UI, add charts for the progress, export for Anki of the seen cards
