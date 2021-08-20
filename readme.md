# Project Description

This is a style that implements the Biblatex package for legal citations to be
used in legal proceedings.

# Citations and Database Model

## Caselaw

With modern internet search and within-page text search, the only thing you
need for a citation is a unique identifier (such as the Digital Object
Identifier). The purpose of including data with the citation and bibliographic
entry may be to give a summary of the importance or reliability of the source.
In the case of caselaw citations, the year and venue are such data. Volume,
reporter, and reporter page are also standard to include, as well as the names
of the parties in a case name. This just appears to be legacy, from a time when
most law was consulted in paper recorders (the case name provides a memorable,
if not unique, partial identifier). Because the `casename volume reporter
reporterpage pinpages (venue year)` format remains standard, it is so
implemented (but see later about pinpages location).

Citations also have a position locator such as page number or line number.
Locators can also be related to document structure such as section and
paragraph numbers which don't have a fixed physical location (if a document is
rendered in more than one way or is updated over time)---these are called
fragments in HTML but I will call them structure locators for the purpose of
locator being either a position or structure locator. It is not standard to use
locators other than the position locator of page number, but that is not
enforced here. The bibliography entry should have a summary of the citations'
locators to give an overview of how the source was used, and this is supported
here. Due to difficulties with comparing mixed alphanumeric strings in LaTeX,
it isn't guaranteed the bibliography will have the locators in order, nor will
they generally be range compressed (see Biblatex issue 1138).

Some may think citations should have explanatory parentheticals. I don't
consider this to be part of the citation, as it merely elaborates on what the
citation is being used for, which is what the text doing the citing should do.
Even explanatory parantheticals that suggest the validity (e.g., Conley v.
Gibson (overruled in Iqbal, Twombly)) aren't using data which belongs to the
source but another one, and so shouldn't be considered part of its citation.
Therefore, explanatory parentheticals are also not part of the bibliography
entry for a source.

It is standard to include page number in a position which is after the page
in the reporter and before the venue and year in a citation to caselaw. This
may be to do with the fact that the paranthetical giving the venue and year is
not considered necessary for the citation, just as an explanatory paranthetical
is not necessary. It isn't possible to use the page in the middle of the
citation if supplied as a postnote, and so that is not done (but in the
bibliography entry it is easily done). It would be simple if the value is
assigned the field in the prenote argument, because then the citation loop code
could access it. So it is merely a matter of \cite[pageno][]{citekey} and a
small change to the .cbx file if one wanted the usual order of fields inside the citation.

## Caselaw versus Present Case Documents

In case law rarely are particular documents cited. The final order and opinion
are almost always what is cited, and on rare occasion someone will reference a
Findings & Reccomendations from a magistrate judge, though far oftener they
will simply cite the opinion's citation of the F&R. As a result, most
citations to specific documents are exclusively for a present case and, on
appeal, to the trial or lower appeals case(s). Here the data model
distinguishes betweem "externalproceedings" with the externalproceeding entry
type, where you can specify a particular document by its docket number and
inherit from an appealcase or trialcase entry, and "caselaw", which is
ambiguous to what document is used.

## Other legal sources

Standard citation formats for other legal sources, based on the Indigo Book,
are also here provided.

## What Should Count as a Source

It isn't always trivial to delimit what is and is not a source. Caselaw is
simple, because it is the sum of opinions and orders for that case (people
generally consider appeals, taking place in a different venue, to be a
different case).  But when legislation is large, or one uses treatises which
are large such as the restatements, it isn't clear what is a single source,
hence requiring a separate bibtex entry and/or bibliography entry. For example,
the division of restatements into volumes is mostly arbitrary and follows,
based on the amount of material, the highly structured document (into
divisions, sections, chapters, and so on). If one considers each restatement to
be a separate authority, then there is much redundant data in the bibliography,
since the bibliography entries differ only by the section number (for the same
restament). Alternatively, one might consider a division, section, or chapter
as a given source. But this classification isn't uniform across all
restatements, and even within the same chapter very different subjects may be
treated (for example, see 652A--B of Second Restatement, Torts).  In law there
is no general concept of tree balance or depth in which the level in the
document tree is related to how specific the subject is, so there is no way to
consistently delimit what is and is not a source. I have considered sources to
be the same only when the conventional citation is the same excluding the
locator and explanatory paranthetical. But note this raises the question of
what a restatement section is, since as a document subpart identifier it can be
a locator, as given in the previous section.

# Bibliography

In law, bibliographies are not used for anything other than summary, and are
usually called tables of points and authorities. Fully verbose citations are
given in the text equivalent to what would normally be used for a bibliography
entry in some other professions like academic science.

## Name formatting

This is somewhat related to the data model, but as far as the datamodel is
concerned it just requires defining many name parts. Name lists in Biblatex are
almost a kind of subentry which allow you to define arbitrary number of name
parts using the biber backend. Here the bibliography entries are formatted
based on which fields of the names exist (and therefore what thing the name is
of, e.g., a person or corporation) and how many names there are. For defining
counsel contact information to be placed at the beginning or end of a
proceeding, name lists and the complicated formatting they allow are clearly
warranted.  However, case name logic is generally quite simple: it is the last
name of the first party (if a person) and the entity name otherwise (e.g.,
government or corporation). I included complicated name formatting for case
names in the bibliography entry so that the bibliography entry would contain
more information than the citation would, but it is a package option to enable.

## Case names 

Generally, though no convention including this one is followed by all courts,
one can define the following party titles from trial and on appeal:

```
plaintiffs/defendants -> appellants/appellees -> petitioner/respondent
```

and then cycle through these, if it reaches an even higher level of appeal.
Hence it is possible to have, if a case first goes to a state trial court, then
a state appeal court, then a state supreme court, and finally the supreme
court, plaintiff-appellant-respondent-appellee and
defendant-appellee-petitioner-appellant. For every level of appeal, there are
`2^n` possibilities for the parties' titles. Enumerated with the above
convention these are

```
- plaintiff,defendant
- plaintiff-appellant,defendant-appellee
  plaintiff-appellee,defendant-appellant
- plaintiff-appellant-petitioner,defendant-appelee-respondent
  plaintiff-appellant-respondent,defendant-appelee-petitioner
  plaintiff-appellee-petitioner,defendant-appellant-respondent
  plaintiff-appellee-respondent,defendant-appellant-petitioner
- plaintiff-appellant-petitioner-appellant,defendant-appelee-respondent-appellee
  plaintiff-appellant-respondent-appellant,defendant-appelee-petitioner-appellee
  plaintiff-appellee-petitioner-appellant,defendant-appellant-respondent-appellee
  plaintiff-appellee-respondent-appellant,defendant-appellant-petitioner-appellee
  plaintiff-appellant-petitioner-appellee,defendant-appelee-respondent-appellant
  plaintiff-appellant-respondent-appellee,defendant-appelee-petitioner-appellant
  plaintiff-appellee-petitioner-appellee,defendant-appellant-respondent-appellant
  plaintiff-appellee-respondent-appellee,defendant-appellant-petitioner-appellee
```

Different courts differ in how they order the names upon appeal. The simplest is an
appeal of a trial decision, but not even this is uniform, with some reversing
in the case the defendant appeals and some not. It's also possible that a high court may not
reverse parties if it directly reviews a trial court decision, but will reverse
parties if it reviews a lower appeals court decision on a trial court decision.

There are also conventions for interlocutary appeals and post-conviction
relief. These are different from "direct appeals". In particular, when a motion
is denied and this is appealed, rather than a final judgement, often the party
names are switched, even when an appeal of a final judgement would not switch
the party names. This also applies when a conviction and sentencing have
already been made and the appeal is not to the judgement, but rather, is an
appeal which argues something new (in interpretation of law) rather than
suggest there was an error in prior judgement. Finally, an impossible problem
is what to do when there are cross-appellants and cross-appellees. Courts may
assign the first name to the party which finds greater error in the decision,
but that can't be known to any program.

These differing conventions are unfortunate because it means one cannot deduce,
from the name of the case, which party is moving (either summoning to trial or
petitioning on appeal). For this reason, the name formatting assumes plaintiffs
are the first party and defendants are the second party in any case. I have
included in this directory an (unused) data file with a survey of the naming
conventions showing how they vary between states---no guarantee is made to
accuracy based on the survey.

# Exhibits

There are several ways to include exhibits using the bibliography database
manager. One is to includegraphics or includepdf. The technical challenge here
is in escaping the current mode, since both graphicx and pdfpages commands are
by default inside the box which is defined by the bibliography entry. I haven't
solved this problem, but one can include exhibits within the box of
the bibliography environment.

Some courts such as the Oregon circuit courts require exhibits to be displayed
in the main document of the proceeding, but many (such as the federal courts)
have them external. PACER (and presumably most state court electronic filing
systems) don't allow embedded files in pdf for security reasons.  Exhibits
therefore need to be linked to, either as local files to be downloaded with the
document, or as web links where the exhibits are hosted. Both embedding and
linking exhibits are supported.

# Package options 

Several package options are provided to switch from more standard legal
citation to less standard. These are

- verboseparties: use a verbose list of parties names, rather than the case
  name, in the bibliography entry
- bibcaseno: include the case number in the bibliography 
  entry (this is a good unique identifier, but convention is not to include it)
- exhibitinclude: include exhibits in the document (as images), rather than
  linking to them

## Overriding default formating by shorthand fields

Invariably edge cases will not be handled satisfactorily. To overcome
this, the following fields will be used to override otherwise inferred ones:

- pincites: the particular pages (or line numbers or paragraphs or sections or
  other locators), usually inferred from the postnote arguments made to the
  citation command
- casename: the casename, usually inferred from the parties' names
- shorthand: the citation when it is first cited
- shorthandshort: the citation after it has been once cited

# Sorting

Jurists often want their bibliographies listed in order of importance.
There are at least two orderings for importance:

- The supremacy of the court, which is actually Judge Posner's recommendation
  in his style guide. Source mapping is used to allow automated sorting based
  on supremacy.
- Number of citations made to the source (in the legal proceeding).

The former is here supported, the latter has an issue on the Biblatex GitHub
(issue #1146) which is supported in development but not implemented here.

# Further Development

This package is not well-polished, but I lost interest in making it so, as TeX
and LaTeX programming is unnecessarily difficult. If I were to continue, I
would likely make a python package that simply substitutes citation commands
and appends a bibliography by reading a (La)TeX file as a template and writing
out a filled template: something like Biber but that accomplishes both front
end and back end.  There is already the bibulous package, which is a python
bibtex replacement, though it doesn't support arbitrary data models. The only
runtime data that a bibliography needs are the page numbers, and so the
motivation for having a LaTeX solution (even a partial one like in Biblatex) is
low. One can define macros which store the page number at every citation in a
control sequence which can later be used by the bibliography, following some
convention like \citekey[a-z] where [a-z] is an alphabetical index. E.g.,
before LaTeX compiling, change \cite{abckey} to {ABC. Proceedings of ABC. 2000.
\edef\abckeya{\thepage}}. For links, one can use the standard LaTeX label/ref
and if desired hyperref hypertarget/hyperlink, which has the additional
advantage of supporting \pageref.  A proof of concept python script,
`simplebib.py`, shows how simply this could be implemented compared to a mixed
LaTeX and "p-language" (Perl/Python/Lua) package.

# License

This uses the same LPPL 1.3 which Biblatex uses. This package only extends,
rather than a modifies, Biblatex, and so the LPPL 1.3 is taken without considering
anything here as "a direct replacement component".
