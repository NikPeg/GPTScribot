from google_images_search import GoogleImagesSearch

# you can provide API key and CX using arguments,
# or you can set environment variables: GCS_DEVELOPER_KEY, GCS_CX
gis = GoogleImagesSearch('AIzaSyBQCEVvvPOa_KMxoCQWHiuNAB8GoyOsEL8', '42a5950c36f38455f')

# define search params
# option for commonly used search param are shown below for easy reference.
# For param marked with '##':
#   - Multiselect is currently not feasible. Choose ONE option only
#   - This param can also be omitted from _search_params if you do not wish to define any value
_search_params = {
    'q': 'Схема общей системы безопасности',
    'num': 1,
    # 'fileType': 'jpg|gif|png',
    # 'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived',
    # 'safe': 'active|high|medium|off|safeUndefined', ##
    # 'imgType': 'clipart|face|lineart|stock|photo|animated|imgTypeUndefined', ##
    # 'imgSize': 'huge|icon|large|medium|small|xlarge|xxlarge|imgSizeUndefined', ##
    # 'imgDominantColor': 'black|blue|brown|gray|green|orange|pink|purple|red|teal|white|yellow|imgDominantColorUndefined', ##
    # 'imgColorType': 'imgColorTypeUndefined' ##
}
# this will only search for images:
gis.search(search_params=_search_params, path_to_dir='pictures/', custom_image_name='Схема общей системы безопасности')
