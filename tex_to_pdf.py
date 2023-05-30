from pylatex import Document, Section, Subsection, Command, NoEscape

doc = Document()
section = Section('Hello')
subsection = Subsection('World')
doc.append(section)
section.append(subsection)
subsection.append('Hello World!')
next_command = "\\newpage"
raw_s = rf'{next_command}'
doc.append(NoEscape(raw_s))
doc.append(Section("Hehe"))
doc.append(Section("Hehe"))
doc.generate_pdf('full', clean_tex=False)