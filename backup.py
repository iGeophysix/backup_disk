import filecmp
import logging.handlers
import os
import shutil

BACKUP_ROOT = os.path.join(os.path.expanduser('~'), 'Yandex.Disk')

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

LOGS_PATH = os.path.join(BASE_PATH, 'logs')

logger = logging.getLogger('backups')
logger.setLevel(logging.DEBUG)
fh = logging.handlers.RotatingFileHandler(os.path.join(LOGS_PATH, 'backups.log'), maxBytes=5 * 1024 ** 2, backupCount=5)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


def get_excludes(path: str = os.path.join(BASE_PATH, 'exclude.txt')):
    with open(path, 'r') as f:
        return [line.strip() for line in f]


if __name__ == "__main__":
    logger.info('Backup process started')
    exclude_list = get_excludes(os.path.join(BASE_PATH, 'exclude.txt'))
    stats = {
        'copied': 0,
        'errors': 0,
        'exists': 0,
        'total': 0
    }
    with open('items.txt', 'r') as items:
        for item in items:
            if item.startswith('#'):
                continue

            for root, dirs, files in os.walk(item.strip(), followlinks=True):
                for file in files:

                    src = os.path.join(root, file)

                    # skip excluded folders
                    if any([excl in src for excl in exclude_list]):
                        continue

                    dst = os.path.join(BACKUP_ROOT, root[1:], file)

                    os.makedirs(os.path.dirname(dst), exist_ok=True)

                    if not os.path.exists(dst) or not filecmp.cmp(src, dst):
                        try:
                            shutil.copy2(src, dst)
                            stats['copied'] += 1
                        except Exception as e:
                            logger.error(f"Cannot copy file {src}. Exception: {e}")
                            stats['errors'] += 1
                    else:
                        stats['exists'] += 1

                    stats['total'] += 1

    logger.info(f"Backup completed. Stats : {stats}")
