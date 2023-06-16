# labeling

## config
install the necessary python package, run the code below in your terminal, i.e. `cmd`

```cmd
pip install "fastapi[all]" 
pip install transformers accelerate torch
pip install sentencepiece protobuf==3.19.0
```

## run

```cmd
gunicorn -c gunicorn_config.py main:labeling

```

`gubicorn_config.py`: the configuration file of your [fastapi] service\
`main`: the file main.py, which defines your fastapi application\
`labeling`: your application name

\
you can access your application through http requests, for example:
```cmd
curl --location 'http://your-ip-address:9090/labeling' \
--header 'Content-Type: application/json' \
--data '{
    "clueId": 123456,
    "tagGroup": [{
        "groupId": 123,
        "tagList": [
            {
                "tagId": 3,
                "tagName": "3节课"
            },
            {
                "tagId": 64564156,
                "tagName": "4节课"
            },
            {
                "tagId": 55585214585,
                "tagName": "好多课"
            }
        ],
        "hitWord": [
            {
                "role": "销售",
                "word": "今天有个5节,哦不是，是4节，的编程特惠课给到孩子"
            },
            {
                "role": "销售",
                "word": "明天有个4节的编程特惠课给到孩子"
            }
        ]
    }]
}'
```

## file

`main.py`: the application extrance\
`gunicorn_config.py`: the configuration of your service\
`mns`: the python sdk package of ALI-MQ\
`model`: the zero-shot classification model stored locally, you can also access it here(`https://huggingface.co/joeddav/xlm-roberta-large-xnli`)\
`sample`: some usage samples provided by ali-mq\
`sample.cfg`：parameters needed for ali-mq\
`model_test_draft.ipynb`: a draft notebook for model test and comparison\
`test.json`: fake data generated for test\
`label_mns.ipynb`: label application with ali-mq, while it is still half-way and to be finished~