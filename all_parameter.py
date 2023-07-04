import Photo_Parameters_2 as pp



adjust_params = {
    "luminunce": [1,2,3], # パラメーターの値を入れる
    "contrast": [1,2,3],
    "gamma": [1,2,3],
    
}

for param1 in adjust_params:
    for param2 in adjust_params:
        if param1 != param2:
            print(param1, param2)
            # toolに対してtool2を適用する
            for num in adjust_params[param1]:
                print(num)
                # tool2に対してnumを適用する
                for num2 in adjust_params[param2]:
                    print(num2)
                    # tool2に対してnum2を適用する
                    #ここに処理を書く
        else:
            print("同じ")
            # 同じ場合、toolのみ適用する
            for num in adjust_params[param2]:
                print(num)
                # toolに対してnumを適用する

                #ここに処理を書く
