"""
    Project Name:       ARJewelBox
    Author:             Asutosh Pati (https://in.linkedin.com/in/asutoshpati)
    Date of Creation:   21 Jul 2020
    Purpose:            Demonstration of AR filters using python
    Description:
        This is an extended helper library for the main program of
        ARJewelleryBox. This library has functions that helps to load data from
        the configuration files.
"""

################################   Libraries   ################################

import json
import os
from pathlib import Path

import cv2
import numpy as np

#############################   Global variables   ############################

BASE_DIR = Path(__file__).resolve().parent
np_key = None
sources = None
loading_screen_data = None


def get_absolute_path(path_str: str, from_cwd: bool = False) -> str:
    """
    Get the absolute path; from the path from root.

    Args:
        path_str (str): path of the file from the root folder
        from_cwd (bool): whether to get the path from current working directory
    Returns:
        str: absolute path of the file
    """
    if from_cwd:
        # This is required when creating a single executable file
        return rf"{os.getcwd()}\{path_str}"
    return rf"{str(BASE_DIR)}\{path_str}"


def validate_settings_file():
    """
    Get the data from the settings file

    Author: Asutosh Pati
    Returns:
        dict: Welcome messages from settings file
    """
    global sources, np_key

    settings_path = get_absolute_path(r"assets\configs\settings.json")
    try:
        settings_file = open(settings_path)
        data = json.load(settings_file)
        valid_code = data["LIC_KEY"]
        np_key = "".join(
            [chr(int(hex_num, 16)) for hex_num in [valid_code[i : i + 2] for i in range(0, len(valid_code), 2)]]
        )
        assert np_key == validate_settings_file.__doc__.split("\n")[3].split(":")[1].strip().upper()
        np_key = "".join(["B", "y", ": "] + list(np_key))
        return data
    except FileNotFoundError:
        print(f"Error: Unable to load file {settings_path}")
    except json.decoder.JSONDecodeError:
        print(f"Error: Corrupt file {settings_path}")
    except AssertionError:
        print(f"Error: Corrupt license key.... Please do not try to remove the author credits.")


def load_settings():
    """
    Load the required data from source file

    Returns:
        None
    """
    global sources, loading_screen_data

    data = validate_settings_file()
    sources = data["source"] if "source" in data else 0
    sources["FILE"] = get_absolute_path(sources["FILE"].replace("/", "\\"))
    loading_screen_data = data["welcome"]


def get_source(selection: str):
    """
    Get the source of the video used in program

    Args:
        selection (str): Selected option
    Returns:
        int/str: Source of video frame
    """
    if not sources:
        load_settings()

    return sources.get(selection)


def load_files():
    """
    Load the assets and get ready for the program

    Returns:
        cv2.CascadeClassifier: Returns haarcascade frontalface classifier
        dict: Jewellery data from the file
    """
    if not sources:
        load_settings()

    model_path = get_absolute_path(r"assets\model\haarcascade_frontalface_default.xml")
    try:
        cascade = cv2.CascadeClassifier(model_path)
    except FileNotFoundError:
        print(f"Error: Unable to load file {model_path}")

    jewellery_path = get_absolute_path(r"assets\configs\jewellery.json")
    try:
        jewellery_file = open(jewellery_path)
        jewellery_data = json.load(jewellery_file)
        jewellery_data = {
            k: {**v, "path": cv2.imread(get_absolute_path(v["path"]), cv2.IMREAD_UNCHANGED)}
            for k, v in jewellery_data.items()
        }
    except FileNotFoundError:
        print(f"Error: Unable to load file {jewellery_path}")
    except json.decoder.JSONDecodeError:
        print(f"Error: Corrupt file {jewellery_path}")
    except AssertionError:
        print(f"Error: Corrupt file {jewellery_path}")

    return cascade, jewellery_data


def generate_loading_screen(height: int, width: int):
    """
    Generate the loading screen to show till the files are loading

    Args:
        height (int): height of the frame
        width (int): width of the frame
    Returns:
         np.array: loading screen as frame
    """
    loading_screen = np.zeros((height, width, 3))
    if not loading_screen_data:
        load_settings()
    loading_screen_data.append(
        {"text": np_key, "org": (220, 375), "fontScale": 1, "color": (255, 255, 255), "thickness": 1}
    )
    for msg_data in loading_screen_data:
        cv2.putText(loading_screen, **msg_data, fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL, lineType=cv2.LINE_AA)
    cv2.putText(loading_screen, **msg_data, fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL, lineType=cv2.LINE_AA)
    return loading_screen
