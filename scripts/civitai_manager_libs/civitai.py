import os
import re
import json
import requests
from . import util
from . import setting 

# Set the URL for the API endpoint

url_dict = {
    "modelPage":"https://civitai.com/models/",
    "modelId": "https://civitai.com/api/v1/models/",
    "modelVersionId": "https://civitai.com/api/v1/model-versions/",
    "modelHash": "https://civitai.com/api/v1/model-versions/by-hash/",
    "imagePage" :  "https://civitai.com/api/v1/images"
}

def Url_Page():
    return url_dict["modelPage"]

def Url_ModelId():
    return url_dict["modelId"]

def Url_VersionId():
    return url_dict["modelVersionId"]

def Url_Hash():
    return url_dict["modelHash"]

def Url_ImagePage():
    return url_dict["imagePage"]

def request_models(api_url=None):
    try:
        # Make a GET request to the API
        with requests.get(api_url, verify=False, proxies=setting.proxies) as response:
            # Check the status code of the response
            if response.status_code != 200:
                util.printD("Request failed with status code: {}".format(response.status_code))
                return         
            data = json.loads(response.text)
    except Exception as e:
        return
    return data

def get_model_info(id:str) -> dict:    
    if not id:
        return
    
    content = None
    try:            
        with requests.get(Url_ModelId()+str(id), verify=False, proxies=setting.proxies) as response:
            content = response.json()

        if 'id' not in content.keys():
            return None
        
    except Exception as e:
        return None

    return content

def get_model_info_by_version_id(version_id:str) -> dict:        
    if not version_id:
        return
    
    version_info = get_version_info_by_version_id(version_id) 
    return get_model_info_by_version_info(version_info)

def get_model_info_by_version_info(version_info) -> dict:    
    if not version_info:
        return 
    return get_model_info(version_info['modelId'])
  
def get_version_info_by_hash(hash) -> dict:        
    if not hash:                
        return 
    
    content = None
    
    try:
        with requests.get(f"{Url_Hash()}{hash[:12]}", verify=False, proxies=setting.proxies) as response:
            content = response.json()
            
        if 'id' not in content.keys():
            return None
        
    except Exception as e:
        return None

    return content  
  
def get_version_info_by_version_id(version_id:str) -> dict:        
    if not version_id:                
        return 
    
    content = None
    
    try:
        with requests.get(Url_VersionId()+str(version_id), verify=False, proxies=setting.proxies) as response:
            content = response.json()

        if 'id' not in content.keys():
            return None
        
    except Exception as e:
        return None
    
    return content   

def get_latest_version_info_by_model_id(id:str) -> dict:

    model_info = get_model_info(id)
    if not model_info:
        return

    if "modelVersions" not in model_info.keys():
        return
            
    def_version = model_info["modelVersions"][0]
    if not def_version:
        return
    
    if "id" not in def_version.keys():
        return
    
    version_id = def_version["id"]

    # 모델에서 얻는 버전 인포는 모델 정보가 없으므로 새로 받아오자
    version_info = get_version_info_by_version_id(str(version_id))

    return version_info

def get_version_id_by_version_name(model_id:str,name:str)->str:
    version_id = None
    if not model_id:
        return 
    
    model_info = get_model_info(model_id)
    if not model_info:
        return
    
    if "modelVersions" not in model_info.keys():
        return
            
    version_id = None
    
    for version in model_info['modelVersions']:
        if version['name'] == name:
            version_id = version['id']
            break
        
    return version_id

def get_files_by_version_info(version_info:dict)->dict:
    download_files = {}
    
    if not version_info:                
        return         
    
    for file in version_info['files']:
        download_files[str(file['id'])] = file
    
    return download_files

def get_files_by_version_id(version_id=None)->dict:   
    if not version_id:                
        return         
    
    version_info = get_version_info_by_version_id(version_id)          
    
    return get_files_by_version_info(version_info)

def get_primary_file_by_version_info(version_info:dict)->dict:
   
    if not version_info:
        return
    
    for file in version_info['files']:
        if 'primary' in file.keys():
            if file['primary']:
                return file        
    return
        
def get_primary_file_by_version_id(version_id=None)->dict:   
    if not version_id:                
        return         
    
    version_info = get_version_info_by_version_id(version_id)          
    
    return get_primary_file_by_version_info(version_info)

def get_images_by_version_id(version_id=None)->dict:   
    if not version_id:                
        return         
    
    version_info = get_version_info_by_version_id(version_id)          
    
    return get_images_by_version_info(version_info)

                
def get_images_by_version_info(version_info:dict)->dict:   
    if not version_info:                
        return         
    
    return version_info["images"]


def get_triger_by_version_info(version_info:dict)->str:   
    if not version_info:                
        return         
    try:
        triger_words = ", ".join(version_info['trainedWords'])    
        if len(triger_words.strip()) > 0:
            return triger_words
    except:
        pass
    
    return

def get_triger_by_version_id(version_id=None)->str:   
    if not version_id:                
        return         
    
    version_info = get_version_info_by_version_id(version_id)          
    
    return get_triger_by_version_info(version_info)

def write_model_info(file, model_info:dict)->str:   
    if not model_info:
        return False
           
    try:
        with open(file, 'w') as f:
            f.write(json.dumps(model_info, indent=4))
    except Exception as e:
            return False
    
    return True

def write_version_info(file, version_info:dict):   
    if not version_info:
        return False

    try:
        with open(file, 'w') as f:
            f.write(json.dumps(version_info, indent=4))
    except Exception as e:
            return False              
    
    return True

def write_triger_words_by_version_id(file, version_id:str):
    if not version_id: 
        return False
        
    version_info = get_version_info_by_version_id(version_id)
    
    return write_triger_words(file,version_info)
    
def write_triger_words(file, version_info:dict):   
    if not version_info:
        return False
    
    triger_words = get_triger_by_version_info(version_info)
        
    if not triger_words:
        return False

    try:
        with open(file, 'w') as f:
            f.write(triger_words)
    except Exception as e:
        return False
        
    return True

def write_LoRa_metadata_by_version_id(file, version_id:str):
    if not version_id: 
        return False
        
    version_info = get_version_info_by_version_id(version_id)
    
    return write_LoRa_metadata(file,version_info)

def write_LoRa_metadata(filepath, version_info):

    LoRa_metadata = {
	    "description": None,
	    "sd version": None,
	    "activation text": None,
	    "preferred weight": 0,
	    "notes": None
    }
    
    if not version_info:
        return False
    
    if os.path.isfile(filepath):        
        return False
    
    if "description" in version_info.keys():
        LoRa_metadata['description'] = version_info["description"]

    if "baseModel" in version_info.keys():
        baseModel = version_info["baseModel"]
        if baseModel in setting.model_basemodels.keys():            
            LoRa_metadata['sd version'] = setting.model_basemodels[baseModel]
        else:
            LoRa_metadata['sd version'] = 'Unknown'
        
    if "trainedWords" in version_info.keys():    
        LoRa_metadata['activation text'] = ", ".join(version_info['trainedWords']) 
    
    notes = list()
    if "modelId" in version_info.keys():                
        notes.append(f"{url_dict['modelPage']}{version_info['modelId']}")
    
    if "downloadUrl" in version_info.keys():
        notes.append(version_info['downloadUrl'])

    if len(notes) > 0:    
        LoRa_metadata['notes'] = ", ".join(notes) 

    try:
        with open(filepath, 'w') as f:
            json.dump(LoRa_metadata, f, indent=4)
    except Exception as e:
        return False

    return True   


def get_images_by_modelid(model_id: str,
                          model_versionid: str | None = None,
                          username: str | None = None) -> list[dict]:
    """"use images api to get all the images from civitai (model api will limit to first 10)
    TODO: support paging logic
    """
    params = {
        'modelId': model_id,
    }

    if model_versionid:
        params['modelVersionId'] = model_versionid

    if username:
        params["username"] = username

    if setting.shortcut_max_download_image_per_version > 0:
        params["limit"] = setting.shortcut_max_download_image_per_version

    try:
        content = {}
        with requests.get(Url_ImagePage(),
                          params=params,
                          verify=False,
                          proxies=setting.proxies) as response:
            content = response.json()

        if 'items' not in content:
            return []

        res_list = []
        for img_dict in content['items']:
            img_dict['nsfw'] = img_dict.get('nsfwLevel', 'None')
            res_list.append(img_dict)

        return res_list

    except Exception as e:
        print(
            "Civitai Shortcut getting model images failed",
            f"({model_id}:{model_versionid})",
            f"({e.__traceback__.tb_frame.f_code.co_filename}:{e.__traceback__.tb_lineno})",
            repr(e))

    return []
