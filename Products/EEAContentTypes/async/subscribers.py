""" Subscribers
"""
import os
import logging
from plone.app.async.subscribers import set_quota
logger = logging.getLogger('Products.EEAContentTypes')


def getMaximumThreads(queue):
    """ Get the maximum threads per queue
    """
    size = 0
    for da in queue.dispatchers.values():
        if not da.activated:
            continue
        for _agent in da.values():
            size += 3
    return size or 1


def configureQueue(event):
    """ Configure zc.async queue for EEAContentTypes jobs
    """
    queue = event.object

    try:
        size = int(os.environ.get(
            'EEACONTENTTYPES_ASYNC_THREADS', getMaximumThreads(queue)))
    except Exception, err:
        logger.warn(err)
        size = 1

    set_quota(queue, 'ctypes', size=size)
    logger.info("quota 'ctypes' with size %r configured in queue %r.",
                size, queue.name)
