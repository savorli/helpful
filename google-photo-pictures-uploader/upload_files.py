from dotenv import load_dotenv
from datetime import datetime
import requests
import logging
import os

logging.basicConfig(level=logging.INFO)

load_dotenv()

ACCESS_TOKEN = os.getenv('TOKEN')
ACCEPTABLE_FORMATS = ['.jpeg', '.jpg', '.png']
REMOVE_IF_UPLOADED = True
ALBUM_TITLE = 'test'
PHOTO_PATH = "./photo"


def generate_file_description(file_name, folder_name, time_created):
    file_name = file_name.replace('_', ' ').replace('-', ' ')
    time_created = time_created.strftime("%Y_%m_%d")
    return folder_name


def add_file_to_album(album_id, file_description, file_token):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    json = {
        'albumId': album_id,
        'newMediaItems': [{
                "description": file_description,
                "simpleMediaItem": {
                    "uploadToken": file_token
                }
            }]}
    response = requests.post("https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate",
                             headers=headers, json=json)
    try:
        if response.status_code == 200:
            for item_result in response.json()["newMediaItemResults"]:
                if 'mediaItem' in item_result.keys():
                    filename = item_result['mediaItem']['filename']
                    url = item_result['mediaItem']['productUrl']
                    logging.info(f"\t\"{filename}\" [{file_description}]: (url = {url})")
                    return True
                else:
                    logging.error(f"Something went wrong: {item_result['status']}")
                    return False
    except Exception as e:
        logging.error(response, e)
        return False


def upload_image(image_name, image_full_path):
    headers = {
        'Content-Type': "application/octet-stream",
        'X-Goog-Upload-File-Name': image_name,
        'X-Goog-Upload-Protocol': "raw",
        'Authorization': f"Bearer {ACCESS_TOKEN}",
    }
    data = open(image_full_path, 'rb').read()
    response = requests.post('https://photoslibrary.googleapis.com/v1/uploads', headers=headers, data=data)
    if response.status_code == 200:
        logging.debug(f'\tPicture uploaded {response.status_code} - \"{image_name}\"')
        return response.text
    else:
        return False


def upload_pics(album_id, pics):
    not_uploaded = []
    for pic in pics:
        time_created = datetime.fromtimestamp(os.stat(pic["path"]).st_ctime)
        filename_no_extension, file_extension = os.path.splitext(pic["path"])
        file_description = generate_file_description(filename_no_extension, pic["folder"], time_created)
        file_token = upload_image(pic["name"], pic["path"])
        if file_token:
            file_added = add_file_to_album(album_id, file_description, file_token)
            if file_added:
                pic['uploaded'] = True
                if REMOVE_IF_UPLOADED:
                    os.remove(pic["path"])
        if not pic['uploaded']:
            pic['uploaded'] = False
            not_uploaded.append(pic["path"])
    return not_uploaded


def create_folders_dict(path):
    folder_list_with_files = {}
    logging.info(f"Walking though {path}, looking for [{', '.join(ACCEPTABLE_FORMATS)}]")
    id_number = 0
    for root, dirs, files in os.walk(path):
        folder = os.path.basename(root)
        if folder not in folder_list_with_files.keys() and len(files) > 0:
            folder_list_with_files[folder] = {"pics": [], "not_uploaded": [], "folder_path": f"{os.path.join(root)}"}
        for i, filename in enumerate(files):
            filename_no_extension, file_extension = os.path.splitext(filename)
            if file_extension.lower() in ACCEPTABLE_FORMATS:
                file_path = f"{path}/{folder}/{filename}"
                item = {"id": id_number, "name": filename, "path": file_path, "folder": folder, "uploaded": False}
                id_number += 1
                folder_list_with_files[folder]["pics"].append(item)
    return folder_list_with_files


def create_new_album(title):
    new_album_res = requests.post("https://photoslibrary.googleapis.com/v1/albums",
                                  headers={
                                      "Authorization": f"Bearer {ACCESS_TOKEN}",
                                      "Content-type": "application/json"
                                  },
                                  json={
                                      "album": {
                                          "title": title
                                      }
                                  })
    return new_album_res.json()['id']


def upload_files(title, path):
    album_id = create_new_album(title)
    logging.info(f"Album created album_id = {album_id}")
    folders_dict = create_folders_dict(path)

    all_count = 0
    uploaded_count = 0
    for folder in folders_dict.keys():
        pics = folders_dict[folder]['pics']
        not_uploaded_pics = upload_pics(album_id, pics)
        all_count += len(pics)
        uploaded_count += len(pics) - len(not_uploaded_pics)

        dir_empty = len(os.listdir(folders_dict[folder]["folder_path"])) == 0
        if len(not_uploaded_pics) == 0 and dir_empty and REMOVE_IF_UPLOADED:
            os.rmdir(folders_dict[folder]["folder_path"])
        folders_dict[folder]['not_uploaded'] = not_uploaded_pics

    for folder in folders_dict.keys():
        not_uploaded = folders_dict[folder]['not_uploaded']
        for not_uploaded_pic in not_uploaded:
            logging.error(f"NOT UPLOADED: {not_uploaded_pic}")

    logging.info(f"FINISHED: {uploaded_count}/{all_count} picture uploaded to the album \"{title}\"")
    return


if __name__ == "__main__":
    upload_files(ALBUM_TITLE, PHOTO_PATH)
