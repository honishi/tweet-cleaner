#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import logging.config
import configparser
import threading
import time
import datetime

from twython import Twython


CONFIG_FILE = os.path.dirname(os.path.abspath(__file__)) + '/clean.configuration'


# main sequence
def main():
    logging.config.fileConfig(CONFIG_FILE)

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    user_configs = load_configuration(config)
    log_configuration(user_configs)

    clean_threads = open_clean_threads(user_configs)
    wait_threads_ends(clean_threads)


# internal methods
def load_configuration(config):
    user_configs = []
    section = 'clean'

    target_users = config[section]['target_users'].split(',')

    for target_user in target_users:
        clean_interval = eval(config[target_user]['clean_interval'])
        clean_threshold = eval(config[target_user]['clean_threshold'])
        consumer_key = config[target_user]['consumer_key']
        consumer_secret = config[target_user]['consumer_secret']
        access_key = config[target_user]['access_key']
        access_secret = config[target_user]['access_secret']

        user_config = {
            'target_user': target_user,
            'clean_interval': clean_interval,
            'clean_threshold': clean_threshold,
            'consumer_key': consumer_key,
            'consumer_secret': consumer_secret,
            'access_key': access_key,
            'access_secret': access_secret}

        user_configs.append(user_config)

    return user_configs


def log_configuration(user_configs):
    for user_config in user_configs:
        logging.debug("user:{} interval:{} threshold:{} ck:{} cs:{} ak:{} as:{}"
                      .format(user_config['target_user'],
                              user_config['clean_interval'], user_config['clean_threshold'],
                              user_config['consumer_key'], user_config['consumer_secret'],
                              user_config['access_key'], user_config['access_secret']))


def open_clean_threads(user_configs):
    clean_threads = []

    for user_config in user_configs:
        clean_thread = threading.Thread(
            name="{}".format(user_config['target_user']),
            target=clean_tweet,
            args=(user_config['target_user'],
                  user_config['clean_interval'], user_config['clean_threshold'],
                  user_config['consumer_key'], user_config['consumer_secret'],
                  user_config['access_key'], user_config['access_secret']
                  ))
        clean_thread.start()
        clean_threads.append(clean_thread)

    return clean_threads


def clean_tweet(screen_name, clean_interval, clean_threshold,
                consumer_key, consumer_secret, access_key, access_secret):
    while True:
        try:
            twitter = Twython(consumer_key, consumer_secret, access_key, access_secret)
            my_statuses = twitter.get_user_timeline(screen_name=screen_name)
            # logging.debug(my_statuses)

            clean_base_datetime = (datetime.datetime.now()
                                   - datetime.timedelta(seconds=clean_threshold))

            for status in my_statuses:
                status_id = status['id']
                created_at = datetime.datetime.strptime(status['created_at'],
                                                        '%a %b %d %H:%M:%S +0000 %Y')
                text = status['text']
                # logging.debug("id:{} created_at:{} text:{}".format(status_id, created_at, text))

                should_destroy = (created_at < clean_base_datetime)
                if should_destroy:
                    logging.info("removing status:{} {} {}".format(status_id, created_at, text))
                    twitter.destroy_status(id=status_id)
                    # logging.info("removed status")
                    # raise Exception()

        except Exception as exception:
            logging.error("caught exception:{}".format(exception))

        logging.debug("sleeping {} seconds...".format(clean_interval))
        time.sleep(clean_interval)


def wait_threads_ends(clean_threads):
    for clean_thread in clean_threads:
        clean_thread.join()


# application entry point
if __name__ == "__main__":
    main()
