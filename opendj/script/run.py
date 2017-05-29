# -*- coding: utf-8 -*-
# Copyright (c) 2015 Gluu
#
# All rights reserved.


def get_config():
    print 'getting config form datastore'

def get_data():
    print 'geting data from datastore'

def setup_opendj():
    print 'setting up opendj'

def configure_opendj():
    print 'configuring opendj'

def index_opendj():
    print 'indexing opendj'

def replicate():
    print 'replicating'

def run():
    get_config()
    get_data()
    setup_opendj()
    configure_opendj()
    index_opendj()
    replicate()


if __name__ == '__main__':
    run()
