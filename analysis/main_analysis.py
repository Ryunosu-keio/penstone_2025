import pandas as pd
from integrate_adjust import integrate_adjust
from emr_extract_max2 import emr_extract_max, emr_extract, name_dict
from devide_emrLog import devide_emrLog
from graph_average_images import graph_average_image
from integrate_emr_answer import integrate_emr_answer, emr_answer_dict
from integrate_participants import integrate_participants
import os


def main(participants, bottom=0.1, top=0.9, filenum="test"):
    # for num in participants:
    #     devide_emrLog(num)
    # emr_extract(name_dict, bottom, top, filenum)
    if not os.path.exists("../data/integrated" + filenum):
        os.mkdir("../data/integrated" + filenum)
    for key in emr_answer_dict.keys():
        integrate_emr_answer(key, emr_answer_dict[key], filenum)


if __name__ == "__main__":
    participants = ["2", "3", "4", "5", "8", "10",
                    "11", "12", "13", "14", "15", "16", "17"]
    bottom = input("bottom: ")
    top = input("top: ")
    filenum = input("filename: ")
    main(participants, float(bottom), float(top), filenum)
