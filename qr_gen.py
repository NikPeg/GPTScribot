import segno
import os
def create_link(url:str):
    qr=segno.make_qr(url)
    path = os.path.join("pictures", "qrCode.png")
    qr.save(path, scale=30, border=1, dark="#2874de")
    return path