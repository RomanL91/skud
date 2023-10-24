import certifi

path_cert = certifi.where()

file_cert_to_add = open(
    'Unified_State_Internet_Access_Gateway.cer', 'r'
)

cert_to_add = file_cert_to_add.read()
file_cert_to_add.close()

with open(path_cert, 'a') as file_cert:
    file_cert.write(cert_to_add)
print('[==INFO==] Unified_State_Internet_Access_Gateway.cer добавлен')