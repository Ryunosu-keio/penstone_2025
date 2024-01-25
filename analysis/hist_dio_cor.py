# 組み合わせをつくるモジュールをインポート
import itertools
list = ["gamma","contrast","sharpness","brightness","equalization"]
# 3つの組み合わせを作る
list2 = list(itertools.combinations(list, 3))
print(list2)

# tupleの中身を連結する
list3 = []
for i in list2:
    list3.append("".join(i))
print(list3)
