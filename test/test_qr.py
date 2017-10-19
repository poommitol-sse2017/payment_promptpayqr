import qrcode
import tempfile

import base64

service = 'BCD'
version = '001'
code    = '1'
function = 'SCT'
bic     = 'Somcompany'
display = 'This QR-Code will be used to initialize bank payment, you will need to confirm this payment using your E-banking system'

lf ='\n'
qr_string = lf.join([service,version,code,function,bic,display])
#_logger.debug('FGF QR string %s', qr_string)
#qr = qrencode.encode_scaled(qr_string,min_size,2)
#f = tempfile.TemporaryFile(mode="r+")
#qrCode = qr[2]
#qrCode.save(f,'png')
#f.seek(0)
#qr_pic = base64.encodestring(f.read())            
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_M,
    box_size=5,
    border=4,
)
qr.add_data(qr_string)
qr.make(fit=True)

qr_pic = qr.make_image()
print('FGF QR pic %s', qr_pic)
f = tempfile.TemporaryFile(mode="r+")
print(f)
qr_pic.save('FF.png','png')
f.seek(0)
qr_pic1 = base64.encodestring(f.read())            

