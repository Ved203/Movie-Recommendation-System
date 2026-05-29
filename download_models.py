
import os
import gdown

os.makedirs("saved_models", exist_ok=True)

if not os.path.exists("saved_models/similarity.pkl"):
    print("Downloading similarity.pkl...")
    gdown.download(
        "https://drive.google.com/uc?id=1lYzJ9xUyc1XKCC3cYvrY_ETf8N5hUHny",
        "saved_models/similarity.pkl",
        quiet=False
    )

if not os.path.exists("saved_models/movie_dict.pkl"):
    print("Downloading movie_dict.pkl...")
    gdown.download(
        "https://drive.google.com/uc?id=1ngEfMd2GS5abTOA9hRNJAW8x0kt-gJET",
        "saved_models/movie_dict.pkl",
        quiet=False
    )
