import hug
import json
import xmltodict
from lxml import etree
from io import StringIO
from json2html import *


@hug.post('/upload', output=hug.output_format.html)
def upload_file(body):
    """
    API endpoint for parsing uploaded file

    :param body: File sent from browser
    :return: JSON (dictionary) describing file and its contents

    Assumes uploaded file from form filed is named 'myfile'
    """
    html_pre = '<html><head><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/boot' \
               'strap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u"' \
               ' crossorigin="anonymous"><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.' \
               '3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooP' \
               'p2bWYgmgJQIXwl/Sp" crossorigin="anonymous"></head><body>'
    html_post = '</body></html>'
    try:
        file_type = 'Unknown'
        file_size = 0
        file_name = 'Unknown'
        processed_data = None

        #  Initial validation of file upload
        if body is None:
            raise ValueError('No file uploaded!')
        if not isinstance(body, dict):
            raise ValueError('API error')
        if 'myfile' not in body.keys():
            raise ValueError('Improperly named file or file not correctly posted.')

        file_name = list(body.keys()).pop()
        file_size = len(list(body.values()).pop())

        #  Get data from file
        incoming_data = body['myfile']
        if incoming_data is None:
            raise ValueError('No data sent')

        #  Pre-process data inside file
        if isinstance(incoming_data, bytes):
            try:
                incoming_data = str(body['myfile'], 'utf-8')
            except Exception:
                raise ValueError('Invalid data format')
        else:
            raise ValueError('Unknown data format')

        #  Determine data type
        if is_json(incoming_data):
            file_type = 'JSON'
            processed_data = json.loads(incoming_data)
        elif is_xml(incoming_data):
            file_type = 'XML'
            processed_data = xmltodict.parse(incoming_data)
            """
            Check other data types here
            """
        else:
            raise ValueError('Invalid data format')
        return '{}{}{}'.format(html_pre, json2html.convert(json={
            'filename': file_name,
            'filesize': file_size,
            'filetype': file_type,
            'data': processed_data
        }, table_attributes="class=\"table table-bordered table-hover\""), html_post)

    except ValueError as e:
        return json2html.convert(json={'error type': 'API generated error', 'error description': str(e)},
                                 table_attributes="class=\"table table-bordered table-hover\"")
    except Exception as e:
        return json2html.convert(json={'error type': 'Unhandled Server Exception: {}'.format(str(e))},
                                 table_attributes="class=\"table table-bordered table-hover\"")


def is_json(data_in):
    """
    Determines if the passed data contains valid JSON data.

    :param data_in: Data to test
    :return: BOOL - True if valid JSON
    """
    is_valid_json = False
    try:
        json_dict = json.loads(data_in)
        is_valid_json = True
    except Exception:
        pass
    return is_valid_json


def is_xml(data_in):
    """
    Determines if the passed data contains valid XML data
    :param data_in:
    :return:
    """
    is_valid_xml = False
    try:
        doc = etree.parse(StringIO(data_in))
        is_valid_xml = True
    except Exception:
        pass
    return is_valid_xml
