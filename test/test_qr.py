import qrcode
import tempfile

import base64
import crc16pure


def get_promptpayqr_str(acc_id,amount):
    promptpay_acc_id = ""
    promptpay_amount = ""
    promptpay_chksum = ""

    if len(acc_id) == 15:
        promptpay_acc_id = "0315" + acc_id
    elif len(acc_id) == 13:
        promptpay_acc_id = "0213" + acc_id
    elif len(acc_id) == 10:
        promptpay_acc_id = "01130066" + acc_id[1:]
    else:
        return "null"

    if len(amount) > 0 and len(amount) < 10:
        promptpay_amount = '540' + str(len(amount)) + amount
    elif len(amount) > 0 and len(amount) >= 10:
        promptpay_amount = '54' + str(len(amount)) + amount  
    else:
        promptpay_amount = ''
    # _ = emvco
    _version = '000201'
    _qr_type = '010211'
    app = '0016A000000677010111' + promptpay_acc_id
    _merchant = '29' + str(len(app)) + app
    _country = '5802TH'
    _currency = '5303764'
    _chksum = '6304'

    promptpay_qr_str = _version + _qr_type  + _merchant + _country + promptpay_amount + _currency  + _chksum
    crc16_chksum = hex(crc16pure.crc16xmodem(promptpay_qr_str,0xffff))[2:]
    promptpay_qr_str = promptpay_qr_str + crc16_chksum
    return promptpay_qr_str


qr_string = get_promptpayqr_str('0123456789','9999')
          
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

