import create_photos_fromlist as cpf
import back_rate as br

if __name__ == "__main__":
    filename = input("使用するエクセルファイルを入力してください")
    br.back_rate(savefile = filename, num = 120, use_photos_path = "testpic_yobi_transformed")
    cpf.create_photos_fromlist(usefile= filename)