from configparser_crypt import ConfigParserCrypt

file = 'config.encrypted' # filename
conf_file = ConfigParserCrypt()

# Set AES key
conf_file.aes_key = ['Enter encripted key']
# Read from encrypted config file
conf_file.read_encrypted(file)

# Get user email
def get_email():
    return conf_file['user']['email']

# Get password
def get_pwd():
    return conf_file['user']['pwd']

# Get AssemblyAI API token
def get_assembyai_api():
    return conf_file['user']['assemblyAI']

