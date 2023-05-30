from pylatex import Document, Section, Subsection, Command

doc = Document()
section = Section('Hello')
subsection = Subsection('World')
doc.append(section)
section.append(subsection)
subsection.append('Hello World!')
doc.generate_pdf()