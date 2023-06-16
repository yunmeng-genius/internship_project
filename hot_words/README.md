# hot_words

## config

```bash
pip install -r requirements.txt

gunicorn -c gunicorn_config.py main:genius
```

## requests

### query hot words

```bash
curl 'http://localhost:9090/hot_words/'
```

return results:

```json
{
    "16504": [
        "内账",
        "代理记账",
        "外账",
        "印花税没得抵",
        "……"
    ],
    "……": ["……"]
}
```

### update hot words with json data

```bash
curl 'http://localhost:9090/update/with_words' \
--header 'Content-Type: application/json' \
--data '{
    "id": "16504",
    "companyHotWords": [
        "天才",
        "hello"
    ]
}'
```

results:

```json
{
    "status": "1"
}
```

### update hot words with file

```bash
curl --location 'http://localhost:9090/update/with_file' \
--form 'file=@"{filepath}"' \
--form 'id="0000"'
```

results:

```json
{
    "status": "1"
}
```

### replace hot words in your texts with json data after ASR

```bash
curl --location 'http://localhost:9090/replace/with_words' \
--header 'Content-Type: application/json' \
--data '{
    "id": "15414",
    "textContent": [
        "哎，我这边是销售宝外呼系统的产品经理，我姓易。",
        "还有大概20块钱。",
        "销售宝",
        "开户费是99，这个是一次性收取，终身使用的",
        "交社保外呼系统",
        "这是22，花费多少啊啊",
        "操售宝",
        "快递啊啊",
        "花呗",
        "防风好",
        "防风号外部系统、放风耗外部系统"
    ]
}'

```

return results:

```json
{
    "status": "1",
    "text_content": [
        "哎，我这边是销售保外呼系统的产品经理，我姓易。",
        "还有大概20块钱。",
        "销售保",
        "开话费是99，这个是一次性收取，终身使用的",
        "交社保外呼系统",
        "这是22，话费多少啊啊",
        "销售保",
        "快递啊啊",
        "话费",
        "防封号",
        "防封号外呼系统、防封号外呼系统"
    ]
}
```

## API-doc

```
http://localhost:9090/docs
```


## hot_words_with_sql

replace the static file `hot_words.csv` with SQLite, while is's still to be finished~