import requests
import os

response = requests.get('https://api.telegram.org/bot6873708372:AAF1HxDdrK_cGIke7FuFDit91nMlG3eWQ5c/getMe')
print(response.status_code)