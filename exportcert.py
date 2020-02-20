# coding=utf-8
import sys
import xml.etree.ElementTree as ET
from subprocess import run
from pathlib import Path

package_path = Path(sys.argv[1])
package_name = package_path.name
package_id = str(package_name)[:-4]

unpack_cl = '7z e {0} -o{1} -y'.format(str(package_path),
                                       str(package_path)[:-4])
run(unpack_cl)

unpack_path = package_path.parent.joinpath(package_id)

tree = ET.parse(unpack_path.joinpath('packageDescription.xml'))
root = tree.getroot()

for document in root.iter('документ'):
        
    document_code = document.attrib['кодТипаДокумента']
    
    if document_code == '01':
        
        print('Found main document:', document_code) 
        
        for document_element in document.iter('подпись'):
            content_file_name = document_element.attrib['имяФайла']
            print('Found signature file:', content_file_name)
            
content_file_path = unpack_path.joinpath(content_file_name)

cert_file = str(package_path.parent) + '\\' + package_id + '.cer'

export_cl = 'openssl pkcs7 -inform DER -outform PEM -print_certs -in {0} -out {1}' \
            .format(str(content_file_path), cert_file)
run(export_cl)

sn_file = package_id + '_SN.txt'
run('openssl x509 -noout -serial -in {0} > {1}' \
               .format(cert_file, sn_file), shell=True)
               
tp_file = package_id + '_TP.txt'
run('openssl x509 -noout -fingerprint -sha1 -inform pem -in {0} > {1}' \
               .format(cert_file, tp_file), shell=True)
               
sntp_file = str(package_path.parent) + '\\' + package_id + '.txt'

with open(sn_file, 'r') as snf:
    cert_sn = snf.readline()[7:-1]
    
with open(tp_file, 'r') as tpf:
    cert_tp = tpf.readline()[17:-1].replace(':','')

with open(sntp_file, 'w') as sntpf:
    sntpf.write(cert_sn + '\t' + cert_tp)

Path(sn_file).unlink()
Path(tp_file).unlink()
    
print('Serial number:', cert_sn)
print('Thumbprint:', cert_tp)

