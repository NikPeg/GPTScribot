import subprocess
result = subprocess.run(["pdflatex", "Internetmemy.tex"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
result = subprocess.run(["pdflatex", "Internetmemy.tex"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print(result.stdout)
print(result.stderr)
print(result.returncode)
