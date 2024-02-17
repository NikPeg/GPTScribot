lines = []
try:
    while True:
        line = input()
        if len(lines) > 0 and lines[0] == line:
            break
        lines.append(line)
except EOFError:
    pass

lines.sort(key=lambda s: s[::-1])

print(lines[0])
print(lines[-1])
