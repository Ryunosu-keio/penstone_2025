import create_photos_fromlist as cpf
import back_rate as br

if __name__ == "__main__":
    filename = input("使用するエクセルファイルの名前を決めてください")
    for i in range(20):
        name = filename + "_" + str(i) 
        br.back_rate(p = 0.33, q = 0.5, savefile = name, num = 48, use_photos_path = "testpic_yobi_transformed")
        cpf.create_photos_fromlist(usefile= name)