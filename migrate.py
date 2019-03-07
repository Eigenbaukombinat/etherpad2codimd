import argparse
import requests
import logging
import psycopg2
import sys
import re
from htmlmd import html2md
from config import \
	ETHERPAD_BASE, \
	CODIMD_BASE, CODIMD_LOGIN, CODIMD_PASSWORD, \
	PG_HOST, PG_USER, PG_PASS, PG_DBNAME


regex = re.compile(r"^\ \ \ \ ")

parser = argparse.ArgumentParser()
parser.add_argument('pad_name', nargs=1, help='Name of the Pad to migrate.')
args = parser.parse_args()
pad_name = args.pad_name[0]

LOG_FORMAT = '%(asctime)-15s - %(msg)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)
log = logging.getLogger('Migrator')

log.info('Connecting to {}@{} using user {}.'.format(
	PG_DBNAME, PG_HOST, PG_USER))
dbcon_str = "dbname='{}' user='{}' host='{}' password='{}'".format(
	PG_DBNAME, PG_USER, PG_HOST, PG_PASS)
db_conn = psycopg2.connect(dbcon_str)


def check_result(url, result):
	if result.status_code != 200:
		log.error("Request to {} failed".format(url))
		sys.exit(0)



log.info('Migrating pad {}.'.format(pad_name))


export_url = '{}/{}/export/txt'.format(ETHERPAD_BASE, pad_name)
log.info('Fetching old pad content at {}'.format(export_url))
result = requests.get(export_url)
check_result(export_url, result)



pad_content = result.text
# convert tabs to spaces
new_pad_content = pad_content.replace('\t', '    ')
lines = []
# remove extra whitespace at the beginning of lines
for line in new_pad_content.splitlines():
	if line.startswith('    '):
		line = line[4:]
	lines.append(line)

new_pad_content = '\n'.join(lines)

new_url = '{}/{}'.format(CODIMD_BASE, pad_name)
log.info('Creating new pad in codimd at {}'.format(new_url))
result = codimd_session.get(new_url)
check_result(new_url, result)

# for now, print the result

print(new_pad_content)



# set content in db
#cursor = db_conn.cursor()
#cursor.execute('UPDATE "Notes" set content = %s where alias = %s', (
#	pad_content, pad_name))
#db_conn.commit()
#cursor.close()
#db_conn.close()