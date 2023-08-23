import create_photos_fromlist as cpf
import back_rate as br
from library.transform_condition import transform_condition

if __name__ == "__main__":
    filename = input("使用するエクセルファイルの名前を決めてください")
    room_condition = input("部屋の明るさを入力してください（明るい場合1）")
    figure_condition = input("文字の明るさを入力してください（明るい場合1）")
    use_photos_path = transform_condition(room_condition, figure_condition)
    num = 48
    for i in range(30):
        name = filename + "_" + str(i) 
        br.back_rate(p = 0.33, q = 0.5, savefile = name, num = num, use_photos_path = use_photos_path)
        cpf.create_photos_fromlist(usefile= name)