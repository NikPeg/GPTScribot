cnt = 0
for i in range(1000, 10000, 5):
    s = str(i)
    if len(set(s)) == len(s):
        cnt += 1
print(cnt)
print(cnt % 6)
