import subprocess
filename = input("Введите название pdf файла:\n")
result = subprocess.run(["pdflatex", "h.tex"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
result = subprocess.run(["pdflatex", "h.tex"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print(result.stdout)
print(result.stderr)
print(result.returncode)
