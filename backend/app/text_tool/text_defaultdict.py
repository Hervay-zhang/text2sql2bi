from collections import defaultdict

data = [("a", 1), ("a", 2), ("b", 3), ("b", 4)]
d = defaultdict(list)


for k,v in data:
    d[k].append(v)

# 转成普通dict
print(dict(d)) # {'a': [1, 2], 'b': [3, 4]}



# 访问不存在key，自动得到空list
print(d["c"])  # []


#案例二
words = ["apple","banana","apple","orange","banana","apple"]
count = defaultdict(int)

for w in words:
    count[w] += 1
    
print(dict(count))
    # {'apple': 3, 'banana': 2, 'orange': 1}