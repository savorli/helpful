# google-photo-pictures-uploader
Small to upload photo to the google photo album 


1. Run `pip3 install -r requirements.txt`
2. Create credentials and put them in this folder with name `googleCredentials.json`: [Get started with REST](https://developers.google.com/photos/library/guides/get-started)
3. Generate ACCESS_TOKEN by running: `python3 create_token.py`
4. Copy/paste ACCESS_TOKEN value into `.env` file, so it looks like `TOKEN=`
5. Check the setting in the begging of the `upload_files.py`. (***CAREFUL**: REMOVE_IF_UPLOADED = True*)
6. Upload files by running `python3 upload_files.py`

