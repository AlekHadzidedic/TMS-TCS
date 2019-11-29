from configparser import ConfigParser


def config(filename='db/database.ini', section='localhost'):
    """
    Fetches configurations
    :param filename: config file path
    :param section: section in config to read from
    :return: Dict representing the config parameters
    """
    # create a parser
    parser = ConfigParser()

    # read config file
    parser.read(filename)

    # get section, default to localhost
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db
