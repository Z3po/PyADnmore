#. -*- coding: UTF- -*-
'''
Copyright (C) 2010 Sebastian Cabrera
<Sebastian.Cabrera@sophos.com>
'''

from ConfigParser import RawConfigParser
from sys import exit
from re import sub
import os

def existSection(section): # {{{
    result = confparser.has_section(section)
    return result
# }}}

def existOption(section, option): # {{{
    result = confparser.has_option(section, option)
    return result
# }}}

def getOption(section, option): # {{{
    result = confparser.get(section, option)
    return result
# }}}

def getADConfig(): # {{{
    _optionscount = 1
    _optionfound = True
    
    if existSection('AD'):
        while _optionfound:
            _tempobject = {}
            if existOption('AD','USESSL%s' % (_optionscount)):
                if int(getOption('AD','USESSL%s' % (_optionscount))):
                    if existOption('AD','HOSTNAME%s' % (_optionscount)):
                        _tempobject.update({ 'HOSTNAME' : 'ldaps://' + getOption('AD','HOSTNAME%s' % (_optionscount)) })
                    else:
                        print 'ERROR: Hostname does not exist at Configoption Nr. ' + str(_optionscount)
                else:
                     if existOption('AD','HOSTNAME%s' % (_optionscount)):
                        _tempobject.update({ 'HOSTNAME' : 'ldap://' + getOption('AD','HOSTNAME%s' % (_optionscount)) })
                     else:
                        print 'ERROR: Hostname does not exist at Configoption Nr. ' + str(_optionscount)
            else:
                print 'ERROR: USESSL does not exist at Configoption Nr. ' + str(_optionscount)
    
            if existOption('AD','BINDUSER%s' % (_optionscount)):
                _tempobject.update({ 'BINDUSER' : getOption('AD','BINDUSER%s' % (_optionscount)) })
            else:
                print 'ERROR: BINDUSER does not exist at Configoption Nr. ' + str(_optionscount)
    
            if existOption('AD','BINDPASSWD%s' % (_optionscount)):
                _tempobject.update({ 'BINDPASSWD' : getOption('AD','BINDPASSWD%s' % (_optionscount)) })
            else:
                print 'ERROR: BINDPASSWD does not exist at Configoption Nr. ' + str(_optionscount)
    
            if existOption('AD','BASE%s' % (_optionscount)):
                _tempobject.update({ 'BASE' : getOption('AD','BASE%s' % (_optionscount)) })
            else:
                print 'ERROR: BASE does not exist at Configoption Nr. ' + str(_optionscount)
    
            if existOption('AD','NAME%s' % (_optionscount)):
                configobject.update({ 'AD_%s' % (getOption('AD','NAME%s' % (_optionscount))): _tempobject })
            else:
                print 'ERROR: NAME does not exist at Configoptoin Nr. ' + str(_optionscount)
    
            _optionscount += 1

            if not existOption('AD', 'USESSL%s' % (_optionscount)):
                _optionfound = False
# }}}

def getIMConfig(): # {{{
    _optionscount = 1
    _optionfound = True
    
    if existSection('INTERMEDIA'):
        while _optionfound:
            _tempobject = {}
            if existOption('INTERMEDIA','LDAPHOST%s' % (_optionscount)):
                _tempobject.update({ 'LDAPHOST' : 'ldaps://' + getOption('INTERMEDIA','LDAPHOST%s' % (_optionscount)) })
            else:
                print 'ERROR: LDAPHOST does not exist at Configoption Nr. ' + str(_optionscount)

            if existOption('INTERMEDIA','BINDUSER%s' % (_optionscount)):
                _tempobject.update({ 'BINDUSER' : getOption('INTERMEDIA','BINDUSER%s' % (_optionscount)) })
            else:
                print 'ERROR: BINDUSER does not exist at Configoption Nr. ' + str(_optionscount)

            if existOption('INTERMEDIA','BINDPASSWD%s' % (_optionscount)):
               _tempobject.update({ 'BINDPASSWD' : getOption('INTERMEDIA','BINDPASSWD%s' % (_optionscount)) })
            else:
               print 'ERROR: BINDPASSWD does not exist at Configoption Nr. ' + str(_optionscount)
    
            if existOption('INTERMEDIA','BASE%s' % (_optionscount)):
                _tempobject.update({ 'BASE' : getOption('INTERMEDIA','BASE%s' % (_optionscount)) })
            else:
                print 'ERROR: BASE does not exist at Configoption Nr. ' + str(_optionscount)
    
            if existOption('INTERMEDIA','MANAGERURL%s' % (_optionscount)):
                _tempobject.update({ 'MANAGERURL' : getOption('INTERMEDIA','MANAGERURL%s' % (_optionscount)) })
            else:
                print 'ERROR: MANAGERURL does not exist at Configoption Nr. ' + str(_optionscount)
    
            if existOption('INTERMEDIA','MANAGERLOGIN%s' % (_optionscount)):
                _tempobject.update({ 'MANAGERLOGIN' : getOption('INTERMEDIA','MANAGERLOGIN%s' % (_optionscount)) })
            else:
                print 'ERROR: MANAGERLOGIN does not exist at Configoption Nr. ' + str(_optionscount)

            if existOption('INTERMEDIA','MANAGERPASSWD%s' % (_optionscount)):
                _tempobject.update({ 'MANAGERPASSWD' : getOption('INTERMEDIA','MANAGERPASSWD%s' % (_optionscount)) })
            else:
                print 'ERROR: MANAGERPASSWD does not exist at Configoption Nr. ' + str(_optionscount)

            if existOption('INTERMEDIA','NAME%s' % (_optionscount)):
                configobject.update({ 'IM_%s' % (getOption('INTERMEDIA','NAME%s' % (_optionscount))): _tempobject })
            else:
                print 'ERROR: NAME does not exist at Configoption Nr. ' + str(_optionscount)
    
            _optionscount += 1

            if not existOption('INTERMEDIA', 'LDAPHOST%s' % (_optionscount)):
                _optionfound = False
# }}}

def getGAPPSConfig(): # {{{
    _optionscount = 1
    _optionfound = True
    
    if existSection('GAPPS'):
        while _optionfound:
            _tempobject = {}
            if existOption('GAPPS','DOMAIN%s' % (_optionscount)):
                _tempobject.update({ 'DOMAIN' : getOption('GAPPS','DOMAIN%s' % (_optionscount)) })
            else:
                print 'ERROR: DOMAIN does not exist at Configoption Nr. ' + str(_optionscount)

            if existOption('GAPPS','ADMINUSER%s' % (_optionscount)):
                _tempobject.update({ 'ADMINUSER' : getOption('GAPPS','ADMINUSER%s' % (_optionscount)) })
            else:
                print 'ERROR: ADMINUSER does not exist at Configoption Nr. ' + str(_optionscount)

            if existOption('GAPPS','ADMINPASSWD%s' % (_optionscount)):
               _tempobject.update({ 'ADMINPASSWD' : getOption('GAPPS','ADMINPASSWD%s' % (_optionscount)) })
            else:
               print 'ERROR: ADMINPASSWD does not exist at Configoption Nr. ' + str(_optionscount)
    
            if existOption('GAPPS','NAME%s' % (_optionscount)):
                configobject.update({ 'GAPPS_%s' % (getOption('GAPPS','NAME%s' % (_optionscount))): _tempobject })
            else:
                print 'ERROR: NAME does not exist at Configoption Nr. ' + str(_optionscount)
    
            _optionscount += 1

            if not existOption('GAPPS', 'DOMAIN%s' % (_optionscount)):
                _optionfound = False
# }}}

def getMAINConfig(): # {{{
    global debug, debuglog
    if existSection('MAIN'):
        if existOption('MAIN','debuglog'):
            debuglog = getOption('MAIN','debuglog')
        if existOption('MAIN','debug'):
            debug = int(getOption('MAIN','debug'))
# }}}

def createConfigFile(): # {{{
    print 'CREATING CONFIGFILE AT: ' + conffile

    confparser.add_section('GAPPS')
    confparser.set('GAPPS','adminuser1','username@domain.com')
    confparser.set('GAPPS','adminpasswd1','P!ssw=rd')
    confparser.set('GAPPS','domain1','domain.com')
    confparser.set('GAPPS','name1','CONFIGNAME')

    print 'GAPPS CONFIG CREATED!'

    confparser.add_section('INTERMEDIA')
    confparser.set('INTERMEDIA','managerurl1','dex.intermedia.net')
    confparser.set('INTERMEDIA','bindpasswd1','P!ssw=rd')
    confparser.set('INTERMEDIA','managerlogin1','admin@domain.com')
    confparser.set('INTERMEDIA','managerpasswd1','anotherP!ssw=rd')
    confparser.set('INTERMEDIA','base1','ou=domain,dc=dex002,dc=intermedia,dc=net')
    confparser.set('INTERMEDIA','name1','CONFIGNAME')
    confparser.set('INTERMEDIA','ldaphost1','ldapd002.intermedia.net')
    confparser.set('INTERMEDIA','binduser1','binduser@domain.com')

    print 'INTERMEDIA CONFIG CREATED!'

    confparser.add_section('AD')
    confparser.set('AD','name1','CONFIGNAME')
    confparser.set('AD','bindpasswd1','P!ssw=rd')
    confparser.set('AD','base1','dc=domain,dc=com')
    confparser.set('AD','hostname1','dcx.domain.com')
    confparser.set('AD','usessl1','1')
    confparser.set('AD','binduser1','admininstrator@domain.com')

    print 'AD CONFIG CREATED!'

    confparser.add_section('MAIN')
    confparser.set('MAIN','debuglog','stdout')
    confparser.set('MAIN','debug','0')

    print 'MAIN CONFIG CREATED!'
    print 'please be sure to update your configfile or nothing will work'

    confparser.write(conffilehandle)
    exit(1)
# }}}

debug = 0
debuglog = 'stdout'
conffile = os.path.expanduser('~/.config/PyADnmore/PyADnmore.conf')
configobject = {}
globalconf = '/etc/PyADnmore/PyADnmore.conf' # you may not want to use different configurations by users. Even you
                                             # may not want to have apache user use his own .config file everybody may 
                                             # look inty browsingly

confparser = RawConfigParser()

if os.access(conffile,os.R_OK):
    confparser.read(conffile)
else:
    if os.access(globalconf,os.R_OK):
        confparser.read(globalconf)
    else:
        if not os.access(sub('PyADnmore.conf','',conffile),os.R_OK):
            os.mkdir(sub('PyADnmore.conf','',conffile))
        try:
            conffilehandle = open(conffile,'w')
            createConfigFile()
        except IOError:
            print 'CONFIGFILE NOT WRITEABLE!\nCannot create' + conffile
            exit(2)

getMAINConfig()
getADConfig()
getIMConfig()
getGAPPSConfig()
