import argparse
import requests
import logging
import psycopg2
import sys
import re
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

if CODIMD_LOGIN is not None:
	login_url = '{}/login'.format(CODIMD_BASE)
	log.info('Logging into codimd at {}'.format(login_url))
	codimd_session = requests.Session()
	data = {"email":CODIMD_LOGIN, "password":CODIMD_PASSWORD}
	result = codimd_session.post(login_url, data=data)
	check_result(login_url, result)


new_url = '{}/{}'.format(CODIMD_BASE, pad_name)
log.info('Creating new pad in codimd at {}'.format(new_url))
if CODIMD_LOGIN is not None:
	codimd_getter = codimd_session
else:
	codimd_getter = requests
result = codimd_getter.get(new_url)
check_result(new_url, result)

# set content in db
log.info('Saving new content for {} in DB.'.format(pad_name))
cursor = db_conn.cursor()
cursor.execute('UPDATE "Notes" set content = %s where alias = %s', (
	new_pad_content, pad_name))
db_conn.commit()
cursor.close()
db_conn.close()