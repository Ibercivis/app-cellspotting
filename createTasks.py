#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of PyBOSSA.
#
# PyBOSSA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyBOSSA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyBOSSA.  If not, see <http://www.gnu.org/licenses/>.

import urllib
import urllib2
import json
import re
import string
from optparse import OptionParser
import pbclient
import csv

if __name__ == "__main__":
    # Arguments for the application
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    # URL where PyBossa listens
    parser.add_option("-u", "--url", dest="api_url",
                      help="PyBossa URL http://domain.com/", metavar="URL")
    # API-KEY
    parser.add_option("-k", "--api-key", dest="api_key",
                      help="PyBossa User API-KEY to interact with PyBossa",
                      metavar="API-KEY")
    # Input Path: where the input data is stored
    parser.add_option("-i", "--input-path", dest="input_path",
                      help="Path where the input data is stored",
                      metavar="INPUT-PATH")
    # Input List File: CSV file containing the list of input files
    parser.add_option("-f", "--inputs-file", dest="inputs_file",
                      help="File where the input file names are stored",
                      metavar="INPUTS-FILE")
    # Create App
    parser.add_option("-c", "--create-app", action="store_true",
                      dest="create_app",
                      help="Create the application",
                      metavar="CREATE-APP")
                      
    # Update template for tasks and long_description for app
    parser.add_option("-t", "--update-template", action="store_true",
                      dest="update_template",
                      help="Update Tasks template",
                      metavar="UPDATE-TEMPLATE"
                     )

    # Update tasks question
    parser.add_option("-q", "--update-tasks", action="store_true",
                      dest="update_tasks",
                      help="Update Tasks question",
                      metavar="UPDATE-TASKS"
                     )

    parser.add_option("-x", "--extra-task", action="store_true",
                      dest="add_more_tasks",
                      help="Add more tasks",
                      metavar="ADD-MORE-TASKS"
                      )
    # Modify the number of TaskRuns per Task
    # (default 30)
    parser.add_option("-n", "--number-answers",
                      dest="n_answers",
                      help="Number of answers per task",
                      metavar="N-ANSWERS"
                     )

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose")
    (options, args) = parser.parse_args()
    
    # Load app details
    try:
        app_json = open('app.json')
        app_config = json.load(app_json)
        app_json.close()
    except IOError as e:
        print "app.json is missing! Please create a new one"
        exit(0)
        
    # If an endpoint is not provided, localhost on the port 5000 is assigned
    if not options.api_url:
        options.api_url = 'http://localhost:5000/'
       
    pbclient.set('endpoint', options.api_url+"/pybossa")

    if not options.api_key:
        parser.error("You must supply an API-KEY to create an \
                      applicationa and tasks in PyBossa")
    else:
        pbclient.set('api_key', options.api_key)

    if (options.verbose):
        print('Running against PyBosssa instance at: %s' % options.api_url)
        print('Using API-KEY: %s' % options.api_key)

    if not options.n_answers:
        options.n_answers = 15

    if not options.input_path:
        parser.error("You must supply the input data path")

    if not options.inputs_file:
        parser.error("You must supply the file where the input data files are listed")
                      
    if options.create_app:
        # Create the app with its corresponding info and files
        pbclient.create_app(app_config['name'],
                app_config['short_name'],
                app_config['description'])
        app = pbclient.find_app(short_name=app_config['short_name'])[0]
        app.long_description = open('long_description.html').read()
        app.info['task_presenter'] = open('cellSpottingPresenter.html').read()
        app.info['tutorial'] = open('tutorial.html').read()
        app.info['thumbnail'] = app_config['thumbnail']
        app.info['sched'] = 'breadth_first'

        pbclient.update_app(app)
        
        # Prepare the url of the server to be accessed in order to get the input data
                #data_url = 'http://pybossa.ibercivis.es:5000/static/input/'
        data_url = options.api_url+"/"+options.input_path
     
        # Filenames and the rest of task infos are written down within the following CSV file
        # A CSV reader is used to go through the document
        # Each row contains a task to be created with the following info: 
        #       task generic filename, number of images composing the task
                #with open('CellImagesData.csv', 'rb') as csvfile:
        with open(options.inputs_file, 'rb') as csvfile:
                csvreader = csv.reader(csvfile, delimiter=',')
                # Create a task for every row
                # It saves for every task:
                #       - Basename of the input files
                #       - Number of microtasks = number of input files for the task
                for row in csvreader:
                        task_info = dict(question="Are the cells still alive?",
                                n_answers=int(options.n_answers), link=data_url + row[0], n_utasks=row[1])
                        print task_info['link']
                        pbclient.create_task(app.id, task_info)
    else:
        if options.add_more_tasks:
            app = pbclient.find_app(short_name=app_config['short_name'])[0]
            # Prepare the url of the server to be accessed in order to get the input data
            #data_url = 'http://pybossa.ibercivis.es:5000/static/input/'
            data_url = options.api_url+"/"+options.input_path
     
            # Filenames and the rest of task infos are written down within the following CSV file
            # A CSV reader is used to go through the document
            # Each row contains a task to be created with the following info:
            #       task generic filename, number of images composing the task
            with open(options.inputs_file, 'rb') as csvfile:
                csvreader = csv.reader(csvfile, delimiter=',')
                # Create a task for every row
                # It saves for every task:
                #       - Basename of the input files
                #       - Number of microtasks = number of input files for the task
                for row in csvreader:
                        task_info = dict(question="Are the cells still alive?",
                                n_answers=int(options.n_answers), link=data_url + row[0], n_utasks=row[1])
                        print task_info['link']
                        pbclient.create_task(app.id, task_info)

    if options.update_template:
        print "Updating app template"
        app = pbclient.find_app(short_name=app_config['short_name'])[0]
        app.long_description = open('long_description.html').read()
        app.info['task_presenter'] = open('cellSpottingPresenter.html').read()
        app.info['tutorial'] = open('tutorial.html').read()
        app.info['sched'] = 'breadth_first'
        pbclient.update_app(app)

    if options.update_tasks:
        print "Updating task question"
        app = pbclient.find_app(short_name='cellspotting')[0]
        for task in pbclient.get_tasks(app.id):
            task.info['question'] = u'Are the cells still alive?'
            pbclient.update_task(task)

    if not options.create_app and not options.update_template\
            and not options.add_more_tasks and not options.update_tasks:
        parser.error("Please check --help or -h for the available options")
