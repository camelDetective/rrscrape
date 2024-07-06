from io import BytesIO
import requests

import numpy as np
from PIL import Image


def load_image(url: str) -> np.ndarray:
    """
    Loads an image from a URL into a numpy array.

    Args:
        url (str): The URL of the image (.jpg).

    Returns:
        np.ndarray: A numpy array representing the image.

    Raises:
        ValueError: If an error occurs while fetching or loading the image.
    """
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img = np.array(img)
    # handle common errors from PIL, requests, and numpy
    except requests.RequestException as e:  # this is the base exception for requests
        raise ValueError(f"Error fetching image from URL: {e}")
    except OSError as e:  # this is the base exception for PIL
        raise ValueError(f"Error loading image: {e}")
    except Exception as e:  # this is the base exception for numpy
        raise ValueError(f"Error converting image to numpy array: {e}")
    return img
