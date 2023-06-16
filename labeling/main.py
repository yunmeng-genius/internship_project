import re
import warnings
from typing import List

from fastapi import Body, FastAPI, status
from pydantic import BaseModel
from transformers import pipeline

warnings.filterwarnings("ignore")

# Load the model
classifier = pipeline("zero-shot-classification", model="./model", device=0)

# define the application
labeling = FastAPI()


# sub-class, to be recognized as taglist
class TagListItem(BaseModel):
    tagId: int
    tagName: str

    def __getitem__(self, item):
        return self.__dict__[item]


# sub-class, to be recognized as hitword
class HitWordItem(BaseModel):
    role: str
    word: str

    def __getitem__(self, item):
        return self.__dict__[item]


# main class
class TagGroupItem(BaseModel):
    groupId: int
    tagList: List[TagListItem]
    hitWord: List[HitWordItem]

    def __getitem__(self, item):
        return self.__dict__[item]


# the main function, to classify the text with the labels provided
def classify_text(classifier, text, labels, batch_size=5):
    # limit the batch_size for the limited computing resource
    if batch_size > 20:
        batch_size = 20
    return classifier(text, labels, multi_label=True, batch_size=batch_size)


@labeling.get("/")
def hello():
    return "hello world!"


@labeling.post("/labeling", status_code=status.HTTP_200_OK)
def labeling_with_llm(
    *,
    # get clueId from body, and no procession
    clueId: int = Body(...),
    # get tagGroup from body
    tagGroup: List[TagGroupItem] = Body(...),
    # control the batch_size for inference, the bigger, the faster
    batch_size: int = 5
):
    clueId = clueId

    # extract tagNames from data
    tags = [[tag["tagName"] for tag in item["tagList"]] for item in tagGroup]
    # extract hitWord from data
    text = [[hit["word"] for hit in item["hitWord"]] for item in tagGroup]


    output = [classify_text(classifier, text[i], tags[i], batch_size=batch_size) for i in range(len(tags))]
    # print(output)

    tagId = []
    # return the ID corresponding to the label of the maximum probability of each sequence
    for tagIter, items in enumerate(output):
        for item in items:
            matched_tags = item["labels"][0]
            # query the ID corresponding to the label in the tagList
            for tag in tagGroup[tagIter]["tagList"]:
                if tag["tagName"] == matched_tags:
                    tagId.append(tag["tagId"])
                    break
    return {"clueId": clueId, "tagId": tagId}
