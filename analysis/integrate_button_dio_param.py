import pandas as pd
import glob
import os

path_button = "../log/*"
path_int = "../data/integrated/"

button_folders = glob.glob(path_button)
button =[button for button in button_folders if button.endswith("_cleaned")]
print(button)

int_folders = glob.glob(path_int+"*")
int = [int for int in int_folders if int.endswith("_cleaned")]
print(int)

name ={11:"0831_1",12:"ono",13:"yu",14:"kyoka",15:"kozaki",16:"yuta",17:"ken"}

if not os.path.exists("../log/dio_button"):
      os.mkdir("../log/dio_button")

path_dio_button = "../log/dio_button/"

# for i in range(11,17):
#     if i == 11:
#         for j in range(20):
#             df_button=pd.read_csv("../log/11_cleaned/0831_1_"+str(i)+"_cleaned.csv")
#             df_int=pd.read_csv(path_int+str(i)+"/"+str(j)+".csv")
#             df=pd.concat([df_button,df_int],axis=1)
#             print(df)
#             if not os.path.exists(path_dio_button +"11_cleaned_dio_button"):
#                 os.mkdir(path_dio_button +"11_cleaned_dio_button")
#             df.to_csv(path_dio_button +"11_cleaned_dio_button/11_cleaned_dio_button_"+str(j)+".csv")

#     else:
#         for j in range(20):
#             df_button = pd.read_csv("../log/"+ str(i) +"_cleaned/"+ name[i] +"_"+ str(j) +"_cleaned.csv")
#             df_int = pd.read_csv(path_int + str(i)+"/"+str(j)+".csv")
#             df=pd.concat([df_button,df_int],axis=1)
#             print(df)
#         if not os.path.exists(path_dio_button +str(i)+"_cleaned_dio_button"):
#             os.mkdir(path_dio_button + str(i)+"_cleaned_dio_button")
#             df.to_csv(path_dio_button + str(i)+"_cleaned_dio_button/"+str(i)+"_cleaned_dio_button_"+str(j)+".csv")




for i in range(11,18):
    if i == 11:
        for j in range(20):
            df_button=pd.read_csv("../log/11_cleaned/0831_1_"+str(i)+"_cleaned.csv")
            df_int=pd.read_csv(path_int+str(i)+"/"+str(j)+".csv")
            df=pd.concat([df_button,df_int],axis=1)
            print(df)
            if not os.path.exists(path_dio_button +"11_cleaned_dio_button"):
                os.mkdir(path_dio_button +"11_cleaned_dio_button")
            df.to_csv(path_dio_button +"11_cleaned_dio_button/11_cleaned_dio_button_"+str(j)+".csv")
    else:
        for j in range(20):
            df_button = pd.read_csv("../log/"+ str(i) +"_cleaned/"+ name[i] +"_"+ str(j) +"_cleaned.csv")
            try:
                df_int = pd.read_csv(path_int + str(i)+"/"+str(j)+".csv")
                df=pd.concat([df_button,df_int],axis=1)
                print(df)
                if not os.path.exists(path_dio_button +str(i)+"_cleaned_dio_button"):
                    os.mkdir(path_dio_button + str(i)+"_cleaned_dio_button")
                df.to_csv(path_dio_button + str(i)+"_cleaned_dio_button/"+str(i)+"_cleaned_dio_button_"+str(j)+".csv")
            except:
                pass

