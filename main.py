import create_photos_fromlist as cpf
import back_rate as br

if __name__ == "__main__":
    filename = input("使用するエクセルファイルを入力してください")
    for i in range(10):
        name = filename + "_" + str(i) 
        br.back_rate(savefile = name, num = 120, use_photos_path = "testpic_yobi_transformed")
        cpf.create_photos_fromlist(usefile= name)