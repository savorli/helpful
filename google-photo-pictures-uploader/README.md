# google-photo-pictures-uploader
Small to upload photo to the google photo album 


```pip3 install -r requirements.txt```

Generate `googleCredentials.json`: [Get started with REST](https://developers.google.com/photos/library/guides/get-started)
Put generated file in this folder and run:
```python3 create_token.py```

Copy and paste access token into .env file, so it looks like: 
```TOKEN=```
```python3 upload_files.py```