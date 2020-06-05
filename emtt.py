#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
emtt.py ~ emergya time-tracker

https://github.com/dskywalk/emtt
Copyright (C) 2020 dskywalk - http://david.dantoine.org

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 2 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import os, sys, urllib, optparse, json, datetime
from pprint import pprint
from bs4 import BeautifulSoup, CData

__VERSION__ = '0.2'
COMMANDS = {
    'ini': { 'label': 'inputOption', 'id': '27780', },
    'end': { 'label': 'outputOption', 'id': '27781', },
    'inirest': { 'label': 'inputOption', 'id': '27782', },
    'endrest': { 'label': 'inputOption', 'id': '27783', },
    'info': { 'id': None, },
}

WEEK = {
    0: 9,
    1: 9,
    2: 9,
    3: 7,
    4: 7,
}

""" fix ssl v1 problems - force TLSv1 """
from requests.adapters import HTTPAdapter
try:
    from requests.packages.urllib3.poolmanager import PoolManager
except:
    from urllib3.poolmanager import PoolManager
import ssl


class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


""" virtual class for fake request config """


class webpnp:
    def __init__(self, p_sUser, p_sSite):
        self.m_sSite = p_sSite
        self.m_dHeaders = {
            'Referer': 'https://%s/home' % self.m_sSite,
            'User-Agent':
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0'
        }
        self.m_sUrl = "https://%s" % self.m_sSite
        self.m_sUser = p_sUser
        # self.m_sCompany = p_sCompany
        self.m_netloc = self.m_sUrl

        import requests
        self.m_oSession = requests.Session()
        self.m_oSession.mount('https://', MyAdapter())  # force ssl v1

        try:  # remove windows warnings
            requests.packages.urllib3.disable_warnings()
        except:
            pass

        # finally call setup
        self.setup()

    def log_file(self, p_sFile, p_sTxt):
        with open(p_sFile, 'w') as file_:
            file_.write(p_sTxt)
            file_.close()

    def setup(self):
        pass

    def login(self):
        return False


class myTeam2Go(webpnp):
    """     setup with ps elements    """
    def setup(self):
        self.m_sLoginUrl = "%s/j_security_check"
        self.m_sHomeUrl = "%s/home"
        self.m_sTimerUrl = "%s/pages/employeePortal/workAssistanceList"
        self.m_sSSID = None
        self.m_sViewSate = None
        self.m_sFormId = None
        self.m_lSelectId = []
        self.m_dFormBase = {
            "javax.faces.ViewState": None,
            "javax.faces.partial.ajax": "true",
            "javax.faces.source": "topMenuIdForm:menuWorkAssitance",
            "javax.faces.partial.execute": "@all",
            "javax.faces.partial.render": "workAssistanceForm",
            "topMenuIdForm:menuWorkAssitance":
            "topMenuIdForm:menuWorkAssitance",
            "topMenuIdForm": "topMenuIdForm",
        }

        self.m_dForm = {
            # "workAssistanceForm:outputOption_input": None,
            #"workAssistanceForm:outputOption_focus":"",
            "javax.faces.source": None,
            "javax.faces.partial.execute": None,
            "javax.faces.ViewState": None,
            "javax.faces.partial.ajax":"true",
            "javax.faces.partial.render":"workAssistanceForm",
            "javax.faces.behavior.event":"change",
            "javax.faces.partial.event":"change",
            "workAssistanceForm":"workAssistanceForm",
            "workAssistanceForm:locationLatitude":"",
            "workAssistanceForm:locationLongitude":"",
            "workAssistanceForm:locationError":"geolocation.error.permission_denied",
        }
        
        self.m_dTicket = {
            # workAssistanceForm:inputOption_input
            # workAssistanceForm:outputOption_input
            'javax.faces.ViewState': None,
            'javax.faces.source': None,
            # 'workAssistanceForm:j_idt312': 'workAssistanceForm:j_idt312',
            'javax.faces.partial.ajax': 'true',
            'javax.faces.partial.execute': '@all',
            'javax.faces.partial.render':
            'workAssistanceForm+session_messages+workAssistanceList:workAssistance',
            'workAssistanceForm': 'workAssistanceForm',
            'workAssistanceForm:outputOption_focus': '',
            'workAssistanceForm:locationLatitude': '',
            'workAssistanceForm:locationLongitude': '',
            'workAssistanceForm:locationError': '',
        }
        self.m_sStateName = 'javax.faces.ViewState'
        self.m_sFacesName = 'javax.faces.source'
        self.m_sPartialName = 'javax.faces.partial.execute'
        self.m_sFormPrefix = 'workAssistanceForm:'
        # self.m_oSession.cookies.set('company', self.m_sCompany, domain=self.m_sSite, path='/')
        self.m_oSession.cookies.set('username', self.m_sUser, domain=self.m_sSite, path='/')


    def get_form(self, p_oCmd):
        self.m_dFormBase[self.m_sStateName] = self.m_sViewSate
        response = self.m_oSession.post(self.m_sHomeUrl % self.m_netloc,
                                        data=self.m_dFormBase,
                                        headers=self.m_dHeaders,
                                        verify=False)
        html = BeautifulSoup(response._content, features='lxml')
        self.m_sFormId = html.find('button').get('id')

        if not self.m_sFormPrefix in self.m_sFormId:
            print "Error-Form", self.m_sFormId
            exit(1)

        for s in html.find_all('select'):
            value = s.find_all('option', selected=True)[0].get("value")
            self.m_lSelectId.append({
                'name': s.get('id'), 
                'value': value if value else p_oCmd['id']
            })

        print 'Form Id: %s' % self.m_sFormId
        print 'Select Id: %s' % self.m_lSelectId

    def send_cmd(self):
        FormId = self.m_sFormPrefix
        for select in self.m_lSelectId:
            self.m_dTicket[select['name']] = select['value']
        self.m_dTicket[self.m_sStateName] = self.m_sViewSate
        self.m_dTicket[self.m_sFacesName] = self.m_sFormId
        self.m_dTicket[self.m_sFormId] = self.m_sFormId

        response = self.m_oSession.post(self.m_sTimerUrl % self.m_netloc,
                                        data=self.m_dTicket,
                                        headers=self.m_dHeaders,
                                        verify=False)
        html = BeautifulSoup(response._content, features='lxml')
        try:
            error = html.find('span', {
                'class': 'ui-messages-error-summary'
            }).get_text()

            if error:
                print self.m_dTicket
                pprint(vars(response))
                print "ERROR:", error
                exit(5)
        except:
              pass

        print 'OK!\n'

    def get_form_paranoic(self, p_oCmd):
    
        # form base optional?
        self.m_dFormBase[self.m_sStateName] = self.m_sViewSate
        response = self.m_oSession.post(self.m_sHomeUrl % self.m_netloc,
                                        data=self.m_dFormBase,
                                        headers=self.m_dHeaders,
                                        verify=False)
        html = BeautifulSoup(response._content, features='lxml')
        self.m_sFormId = html.find('button').get('id')

        if not self.m_sFormPrefix in self.m_sFormId:
            print "Error-Form", self.m_sFormId
            exit(1)

        for s in html.find_all('select'):
          print s

        input_name = "%s%s" % (self.m_sFormPrefix, p_oCmd['label'])
        selectId = "%s_input" % input_name
        print 'Form: %s' % self.m_sFormId
        print 'Select: %s' % selectId
        
        # required ?
        self.m_dForm[self.m_sStateName] = self.m_sViewSate
        self.m_dForm[self.m_sFacesName] = input_name
        self.m_dForm[self.m_sPartialName] = input_name
        self.m_dForm[selectId] = p_oCmd['id']
        self.m_dForm["%s_focus" % input_name] = ''

        response = self.m_oSession.post(self.m_sTimerUrl % self.m_netloc,
                                        data=self.m_dForm,
                                        headers=self.m_dHeaders,
                                        verify=False)
        html = BeautifulSoup(response._content, features='lxml')

        for tag in html.find_all('label', {'class': 'col-form-label'}):
            print tag.parent.get_text().strip()

        formId = html.find('button').get('id')
        for s in html.find_all('select'):
            value = s.find_all('option', selected=True)[0].get("value")
            self.m_lSelectId.append({
                'name': s.get('id'), 
                'value': value if value else p_oCmd['id']
            })

        if not self.m_sFormPrefix in formId or formId != self.m_sFormId:
            print "Error-Form", self.m_sFormId, formId
            exit(1)

        print 'Form Id: %s' % self.m_sFormId
        print 'Select Id: %s' % self.m_lSelectId

    def get_timer(self):
        response = self.m_oSession.get(self.m_sTimerUrl % self.m_netloc,
                                       headers=self.m_dHeaders)
        html = BeautifulSoup(response._content, features='html.parser')
        data = html.find(id='homeForm')
        sHoras = data.find('span').get_text()
        weekday = datetime.datetime.today().weekday()
        totalreq = sum(WEEK[i] for i in range(len(WEEK)) if i <= weekday)
        print 'Horas Trabajadas: %s (%i h)' % ( sHoras, totalreq)

    def show_data(self, content):
        html = BeautifulSoup(content, features='html.parser')
        data = html.find(id='homeForm:personalInfoPanel_content')
        self.m_sViewSate = html.find('input', {
            'name': 'javax.faces.ViewState'
        }).get('value')
        sDNI = data.find('span', id='homeForm:dninie').get_text()
        sEmail = data.find('span', id='homeForm:email').get_text()
        sId = data.find('span', id='homeForm:employeeid').get_text()
        print '\nDNI: %s ~ %s' % (sDNI, sEmail)
        print 'ID: %s' % sId

    """     login to https site and save cookies   """

    def login(self, p_sUser, p_sPass):
        payload = {
            'j_username': p_sUser,
            'j_password': p_sPass,
            'login': '',
            'g-recaptcha-response': '',
        }
        response = self.m_oSession.post(self.m_sLoginUrl % self.m_netloc,
                                        headers=self.m_dHeaders,
                                        data=payload,
                                        verify=False)
        if "error" in response.url:
            return False
        self.show_data(response._content)
        return True


"""
****  MAIN 
"""

if __name__ == '__main__':
    parser = optparse.OptionParser(
        usage='%prog [options] [ini|inirest|endrest|end|info]',
        version=__VERSION__,
    )

    install_opts = optparse.OptionGroup(
        parser,
        'Login Options',
        'These options control login.',
    )

    install_opts.add_option('--config',
                            action='store',
                            default=False,
                            help='your emergya login config.')

    parser.add_option_group(install_opts)
    lOptions, lArgs = parser.parse_args()
    dataJson = {}

    if not len(lArgs):
        parser.print_help()
        sys.exit(1)

    if lArgs[0] in COMMANDS.keys():
        command = lArgs[0]
    else:
        parser.print_help()
        sys.exit(1)

    with open(lOptions.config) as f:
        dataJson = json.load(f)

    oWeb = myTeam2Go(
        dataJson['username'],
        # dataJson['company'],
        dataJson['site']
    )

    userLogged = False
    if dataJson['username'] and dataJson['password']:
        print "Login..."
        userLogged = oWeb.login(dataJson['username'], dataJson['password'])
    else:
        print "ERROR! json config needs a username/password."
        sys.exit(2)

    if not userLogged:
        print "ERROR LOGIN! Check your user/pass."
        sys.exit(2)

    if not oWeb.m_sViewSate:
        print "ERROR! getting data..."
        sys.exit(2)

    oWeb.get_timer()

    # check info command
    if COMMANDS[command]['id'] is not None:
        cmd = COMMANDS[command]
        print "Sending CMD: %s (%s) " % (command, cmd['id'])
        oWeb.get_form(cmd)
        oWeb.send_cmd()

    sys.exit(0)
