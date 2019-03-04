import argparse
import requests
import logging
import psycopg2
import sys
from config import \
	ETHERPAD_BASE, \
	CODIMD_BASE, CODIMD_LOGIN, CODIMD_PASSWORD, \
	PG_HOST, PG_USER, PG_PASS, PG_DBNAME

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


login_url = '{}/login'.format(CODIMD_BASE)
log.info('Logging into codimd at {}'.format(login_url))
codimd_session = requests.Session()
data = {"email":CODIMD_LOGIN, "password":CODIMD_PASSWORD}
result = codimd_session.post(login_url, data=data)
check_result(login_url, result)

export_url = '{}/{}/export/txt'.format(ETHERPAD_BASE, pad_name)
log.info('Fetching old pad content at {}'.format(export_url))
result = requests.get(export_url)
check_result(export_url, result)
pad_content = result.text

new_url = '{}/{}'.format(CODIMD_BASE, pad_name)
log.info('Creating new pad in codimd at {}'.format(new_url))
result = codimd_session.get(new_url)
check_result(new_url, result)

# set content in db
cursor = db_conn.cursor()
cursor.execute('UPDATE "Notes" set content = %s where alias = %s', (
	pad_content, pad_name))
db_conn.commit()
cursor.close()
db_conn.close()