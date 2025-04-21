from configparser_crypt import ConfigParserCrypt

file = 'config.encrypted'
conf_file = ConfigParserCrypt()

# Setting up config file

# Create new AES key
conf_file.generate_key()
# Don't forget to backup your key somewhere
aes_key = conf_file.aes_key
print(aes_key)

conf_file.add_section('user')

# Add your credentials here
conf_file['user']['email'] = 'Enter Email'
conf_file['user']['pwd'] = 'Enter Password'
conf_file['user']['assemblyAI'] = 'Enter assembly API'

# Write encrypted config file
with open(file, 'wb') as file_handle:
    conf_file.write_encrypted(file_handle)