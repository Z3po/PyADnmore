# -*- coding: UTF-8 -*-
'''
Copyright (C) 2010 Sebastian Cabrera
<scabrera-github@portachtzig.de> 
'''

from sys import exit as __exit
import config
import gdata.apps.service
import gdata.apps.groups.service
from random import choice
from datetime import datetime

configdict = config.configobject
debug = config.debug
debuglog = config.debuglog

def __writeDebug(logfile, logline): # {{{
    if logfile == 'stdout':
        print logline
    else:
        debfile = open(logfile, 'a')
        debfile.write(str(datetime.now()) + '\t')
        debfile.write(logline + '\n')
        debfile.close()
# }}}

# function to handle all Errors
def __handleError(function, Error): # {{{
    if debug:
        __writeDebug(debuglog, 'joined __handleError function in gappsmodule with function ' + function + ' and Error ' + str(Error))
    print 'ERROR in ' + function + ': ' + str(Error)
    __exit(2)
# }}}

def getUsers(gappsname, username): # {{{
    """get Users from Google Apps
    name: we need the name of the GAPPS Account to use
    username: we need the name of the user to search for or * for all
    """
    gappsname = 'GAPPS_' + gappsname

    _tempresult = {}
    result = []
    if debug:
        __writeDebug(debuglog, 'joined getUsers function in gappsmodule with gappsname ' + gappsname + ' and username ' + username)

    # try
    try:
        # Set Authentication information
        service = gdata.apps.service.AppsService(email=configdict[gappsname]["ADMINUSER"], domain=configdict[gappsname]["DOMAIN"], password=configdict[gappsname]["ADMINPASSWD"])

        # get Token
        service.ProgrammaticLogin()

        # Get Data
        if username == '*':
            _tempfetch = service.RetrieveAllUsers().entry
        else:
            _tempfetch = service.RetrieveUser(username)

    # unless exception is raised
    except gdata.apps.service.AppsForYourDomainException , e:
        __handleError('getUsers', e)
    # if no exception is raised, return results
    else:
        try:
            length = len(_tempfetch)
        except TypeError, e:
            length = 0

        if length > 0:
            for i in range(len(_tempfetch)):
                _tempresult.update({ 'user_name' : _tempfetch[i].login.user_name })
                _tempresult.update({ 'suspended' : _tempfetch[i].login.suspended })
                _tempresult.update({ 'admin' : _tempfetch[i].login.admin })
                _tempresult.update({ 'change_password' : _tempfetch[i].login.change_password })
                _tempresult.update({ 'agreed_to_terms' : _tempfetch[i].login.agreed_to_terms })
                _tempresult.update({ 'ip_whitelisted' : _tempfetch[i].login.ip_whitelisted })
                _tempresult.update({ 'family_name' : _tempfetch[i].name.family_name })
                _tempresult.update({ 'given_name' : _tempfetch[i].name.given_name })
                _tempresult.update({ 'limit' : _tempfetch[i].quota.limit })
                _tempresult.update({ 'email' : _tempfetch[i].login.user_name + '@' + configdict[gappsname]["DOMAIN"] })
                result.append( _tempresult )
                _tempresult = {}
        else:
                _tempresult.update({ 'user_name' : _tempfetch.login.user_name })
                _tempresult.update({ 'suspended' : _tempfetch.login.suspended })
                _tempresult.update({ 'admin' : _tempfetch.login.admin })
                _tempresult.update({ 'change_password' : _tempfetch.login.change_password })
                _tempresult.update({ 'agreed_to_terms' : _tempfetch.login.agreed_to_terms })
                _tempresult.update({ 'ip_whitelisted' : _tempfetch.login.ip_whitelisted })
                _tempresult.update({ 'family_name' : _tempfetch.name.family_name })
                _tempresult.update({ 'given_name' : _tempfetch.name.given_name })
                _tempresult.update({ 'limit' : _tempfetch.quota.limit })
                _tempresult.update({ 'email' : _tempfetch.login.user_name + '@' + configdict[gappsname]["DOMAIN"] })
                result.append( _tempresult )
        if debug:
            __writeDebug(debuglog, 'left getUsers function in gappsmodule with gappsname ' + gappsname + ' and resultset ' + str(result))

        return result
# }}}

def modifyUser(gappsname, username, changesdict): # {{{
    """Modify Google Apps User
    gappsname: we need the name of the GAPPS Account to use
    username: we need the name of the user to search for or * for all
    changesdict: dictionary with changes
    """
    gappsname = 'GAPPS_' + gappsname

    _attributemapping = { 'family_name' : 'name', 'given_name' : 'name', 'suspended' : 'login', 'change_password' : 'login',
                            'admin' : 'login', 'limit' : 'quota', 'user_name' : 'login' }
    if debug:
        __writeDebug(debuglog, 'joined modifyUser function in gappsmodule with gappsname ' + gappsname + ' ,username ' + username + ' and changesdict ' + str(changesdict))
    # try
    try:
        # Set Authentication information
        service = gdata.apps.service.AppsService(email=configdict[gappsname]["ADMINUSER"], domain=configdict[gappsname]["DOMAIN"], password=configdict[gappsname]["ADMINPASSWD"])

        # get Token
        service.ProgrammaticLogin()

        # get UserObject for username
        _userobject = service.RetrieveUser(username)

        for key in changesdict.keys():
            if key in _attributemapping:
                if _attributemapping[key] == 'login':
                    setattr( _userobject.login, '%s' % key, changesdict[key] )
                elif _attributemapping[key] == 'name':
                    setattr( _userobject.name, '%s' % key, changesdict[key] )
                elif _attributemapping[key] == 'quota':
                    setattr( _userobject.quota, '%s' % key, changesdict[key] )
                else:
                    __handleError('modifyUser', 'ATTRIBUTE ERROR:' + key)
            else:
                __handleError('modifyUser', 'ATTRIBUTE ERROR: ' + key )

        # Get Data
        service.UpdateUser(username, _userobject)

    # unless exception is raised
    except gdata.apps.service.AppsForYourDomainException , e:
        __handleError('modifyUsers', e)

    # if no exception is raised, return results
    if debug:
        __writeDebug(debuglog, 'left modifyUser function in gappsmodule with gappsname ' + gappsname)
    return True
# }}}

def modifyGroup(gappsname, groupname, changesdict): # {{{
    """get Groups from Google Apps User Account
    gappsname: we need the name of the Gapps Account to use
    username: name of the user whos groups we wanna know
    """
    gappsname = 'GAPPS_' + gappsname

    if debug:
        __writeDebug(debuglog, 'joined modifyGroup function in gappsmodule with gappsname ' + gappsname + ',groupname ' + groupname + ' and changesdict ' + str(changesdict))

    # try
    try:
        # Set Authentication information
        service = gdata.apps.groups.service.GroupsService(email=configdict[gappsname]["ADMINUSER"], domain=configdict[gappsname]["DOMAIN"], password=configdict[gappsname]["ADMINPASSWD"])

        # get Token
        service.ProgrammaticLogin()

        # Get Data
        service.UpdateGroup(groupname, changesdict["group_name"], changesdict["description"], changesdict["email_permission"])

    # unless exception is raised
    except gdata.apps.service.AppsForYourDomainException , e:
        __handleError('getGroups', e)

    # if no exception is raised, return results
    if debug:
        __writeDebug(debuglog, 'left modifyGroup function in gappsmodule with gappsname ' + gappsname)
    return True
# }}}

def getUserGroups(gappsname, username): # {{{
    """get Groups from Google Apps User Account
    gappsname: we need the name of the Gapps Account to use
    username: name of the user whos groups we wanna know
    """
    gappsname = 'GAPPS_' + gappsname

    if debug:
        __writeDebug(debuglog, 'joined getUserGroups function in gappsmodule with gappsname ' + gappsname + ' and username ' + username)
    # try
    try:
        # Set Authentication information
        service = gdata.apps.groups.service.GroupsService(email=configdict[gappsname]["ADMINUSER"], domain=configdict[gappsname]["DOMAIN"], password=configdict[gappsname]["ADMINPASSWD"])

        # get Token
        service.ProgrammaticLogin()

        # Get Data
        result = service.RetrieveGroups(username)

    # unless exception is raised
    except gdata.apps.service.AppsForYourDomainException , e:
        __handleError('getGroups', e)

    # if no exception is raised, return results
    if debug:
        __writeDebug(debuglog, 'left getUserGroups function in gappsmodule with gappsname ' + gappsname + ' and resultset ' + str(result))
    return result
# }}}

def getGroups(gappsname, groupname): # {{{
    """get Groups form Google Apps
    gappsname: we need the name of the Gapps Account to use
    groupname: name of the group to search for or * for all
    """
    gappsname = 'GAPPS_' + gappsname

    result = []
    if debug:
        __writeDebug(debuglog, 'joined getGroups function in gappsmodule with gappsname ' + gappsname + ' and groupname ' + groupname)
    # try
    try:
        # Set Authentication information
        service = gdata.apps.groups.service.GroupsService(email=configdict[gappsname]["ADMINUSER"], domain=configdict[gappsname]["DOMAIN"], password=configdict[gappsname]["ADMINPASSWD"])

        # get Token
        service.ProgrammaticLogin()

        # Get Data
        if groupname == '*':
            result = service.RetrieveAllGroups()

        else:
            result.append(service.RetrieveGroup(groupname))

    # unless exception is raised
    except gdata.apps.service.AppsForYourDomainException , e:
        __handleError('getGroups', e)

    # if no exception is raised, return results
    if debug:
        __writeDebug(debuglog, 'left getGroups function in gappsmodule with gappsname ' + gappsname + ' and resultset ' + str(result))
    return result
# }}}

def getGroupMembers(gappsname, groupname): # {{{
    """get Group Members from Google Apps
    gappsname: we need the name of the Gapps Account to use
    groupname: name of the group to search for users
    """
    gappsname = 'GAPPS_' + gappsname

    if debug:
        __writeDebug(debuglog, 'joined getGroupMembers function in gappsmodule with gappsname ' + gappsname + ' and groupname ' + groupname)
    # try
    try:
        # Set Authentication information
        service = gdata.apps.groups.service.GroupsService(email=configdict[gappsname]["ADMINUSER"], domain=configdict[gappsname]["DOMAIN"], password=configdict[gappsname]["ADMINPASSWD"])

        # get Token
        service.ProgrammaticLogin()

        # Get Data
        result = service.RetrieveAllMembers(groupname)

    # unless exception is raised
    except gdata.apps.service.AppsForYourDomainException , e:
        __handleError('getGroupMembers', e)

    # if no exception is raised, return results
    if debug:
        __writeDebug(debuglog, 'left getGroupMembers function in gappsmodule with gappsname ' + gappsname + ' and resultset ' + str(result))
    return result
# }}}

def addMemberToGroup(gappsname, member_id, group_id): # {{{
    """add a user to Google Apps Group
    gappsname: we need the name of the Gapps Account to use
    member_id: member_id of the user
    group_id: group_id of the group the user should be in
    """
    gappsname = 'GAPPS_' + gappsname

    if debug:
        __writeDebug(debuglog, 'joined addMemberToGroup function in gappsmodule with gappsname ' + gappsname + ',member_id ' + member_id + ' and group_id ' + group_id)
    # try
    try:
        # Set Authentication information
        service = gdata.apps.groups.service.GroupsService(email=configdict[gappsname]["ADMINUSER"], domain=configdict[gappsname]["DOMAIN"], password=configdict[gappsname]["ADMINPASSWD"])

        # get Token
        service.ProgrammaticLogin()
        
        # Update Group
        service.AddMemberToGroup(member_id, group_id)

    # unless exception is raised
    except gdata.apps.service.AppsForYourDomainException , e:
        __handleError('addMemberToGroup', e)

    # if no exception is raised, return results
    if debug:
        __writeDebug(debuglog, 'left addMemberToGroup function in gappsmodule with gappsname ' + gappsname)
    return True
# }}}

def removeMemberFromGroup(gappsname, member_id, group_id): # {{{
    """remove user from Google Apps Group
    gappsname: we need the name of the Gapps Account to use
    member_id: member_id of the user
    group_id: group_id of the group the user should be removed from
    """
    gappsname = 'GAPPS_' + gappsname

    if debug:
        __writeDebug(debuglog, 'joined removeMemberFromGroup function in gappsmodule with gappsname ' + gappsname + ',member_id ' + member_id + ' and group_id ' + group_id)
    # try
    try:
        # Set Authentication information
        service = gdata.apps.groups.service.GroupsService(email=configdict[gappsname]["ADMINUSER"], domain=configdict[gappsname]["DOMAIN"], password=configdict[gappsname]["ADMINPASSWD"])

        # get Token
        service.ProgrammaticLogin()
        
        # Update Group
        service.RemoveMemberFromGroup(member_id, group_id)

    # unless exception is raised
    except gdata.apps.service.AppsForYourDomainException , e:
        __handleError('removeMemberFromGroup', e)

    # if no exception is raised, return results
    if debug:
        __writeDebug(debuglog, 'left removeMemberFromGroup function in gappsmodule with gappsname ' + gappsname)
    return True
# }}}

def createUser(gappsname, _userdict): # {{{
    """add a User to Gapps
    name: we need the name of the Gapps Account here too
    userdict: dictionary with values to set
    Needed values: 
                    -> user_name: Username of the google apps user
                    -> family_name: Surname of the user
                    -> given_name: Given Name of the user
                    -> password: Password of the user
    valid values:
                    -> quota_limit: Quota Limit of the users mailbox
                    -> suspended: Create the user suspended
    """
    gappsname = 'GAPPS_' + gappsname

    _tempresult = {}
    if debug:
        __writeDebug(debuglog, 'joined createUser function with gappsname ' + gappsname + ' and _userdict ' + str(_userdict))

    if 'user_name' not in _userdict:
        __handleError('createUser', 'MISSING ARGUMENT user_name')

    if 'family_name' not in _userdict:
        __handleError('createUser', 'MISSING ARGUMENT family_name')

    if 'given_name' not in _userdict:
        __handleError('createUser', 'MISSING ARGUMENT given_name')

    if 'password' in _userdict:
        _userdict.update({ 'password' : _userdict["password"] })
    else:
        __handleError('createUser', 'MISSING ARGUMENT password')

    if 'quota_limit' in _userdict:
        _newuser = { 'user_name' : _userdict["user_name"], 'family_name' : _userdict["family_name"], 'given_name' : _userdict["given_name"], 'password' : _userdict["password"], 'quota_limit' : _userdict["quota_limit"] }
    else:
        _newuser = { 'user_name' : _userdict["user_name"], 'family_name' : _userdict["family_name"], 'given_name' : _userdict["given_name"], 'password' : _userdict["password"] }

    if 'suspended' in _userdict:
        _newuser.update({ 'suspended' : _userdict["suspended"] })
    else:
        _newuser.update({ 'suspended' : 'false' })

    # try
    try:
        # Set Authentication information
        service = gdata.apps.service.AppsService(email=configdict[gappsname]["ADMINUSER"], domain=configdict[gappsname]["DOMAIN"], password=configdict[gappsname]["ADMINPASSWD"])

        # get Token
        service.ProgrammaticLogin()

        # CREATE User
        if 'quota_limit' in _newuser:
            result = service.CreateUser(_newuser["user_name"], _newuser["family_name"], _newuser["given_name"], _newuser["password"], suspended=_newuser["suspended"], quota_limit=_newuser["quota_limit"])
        else:
            result = service.CreateUser(_newuser["user_name"], _newuser["family_name"], _newuser["given_name"], _newuser["password"], suspended=_newuser["suspended"])

    # unless exception is raised
    except gdata.apps.service.AppsForYourDomainException , e:
        __handleError('createUser', e)
    else:
        _tempresult.update({ 'user_name' : result.login.user_name })
        _tempresult.update({ 'suspended' : result.login.suspended })
        _tempresult.update({ 'admin' : result.login.admin })
        _tempresult.update({ 'change_password' : result.login.change_password })
        _tempresult.update({ 'agreed_to_terms' : result.login.agreed_to_terms })
        _tempresult.update({ 'password' : _newuser["password"] })
        _tempresult.update({ 'ip_whitelisted' : result.login.ip_whitelisted })
        _tempresult.update({ 'family_name' : result.name.family_name })
        _tempresult.update({ 'given_name' : result.name.given_name })
        _tempresult.update({ 'limit' : result.quota.limit })
        _tempresult.update({ 'email' : result.login.user_name + '@' + configdict[gappsname]["DOMAIN"] })
        result =  _tempresult

    if debug:
        __writeDebug(debuglog, 'left createUser function in gappsmodule with gappsname ' + gappsname + ' and resultset ' + str(result))
    return result
# }}}

def deleteUser(gappsname, username): # {{{
    """delete a User from Google Apps
    name: we need the name of the Gapps Account here
    username: username of the user to delete
    """
    gappsname = 'GAPPS_' + gappsname

    if debug:
        __writeDebug(debuglog, 'joined deleteUser function in gappsmodule with gappsname ' + gappsname + ' and username ' + username)
    # try
    try:
        # Set Authentication information
        service = gdata.apps.service.AppsService(email=configdict[gappsname]["ADMINUSER"], domain=configdict[gappsname]["DOMAIN"], password=configdict[gappsname]["ADMINPASSWD"])

        # get Token
        service.ProgrammaticLogin()

        # CREATE User
        service.DeleteUser(username)

    # unless exception is raised
    except gdata.apps.service.AppsForYourDomainException , e:
        __handleError('deleteUser', e)

    if debug:
        __writeDebug(debuglog, 'left deleteUser function in gappsmodule with gappsname ' + gappsname)
    return True
# }}}

def deleteGroup(gappsname, groupname): # {{{
    """delete Groups form Gapps
    name: we need the name of the Gapps Account to use
    groupname: name of the goup to delete
    """
    gappsname = 'GAPPS_' + gappsname

    if debug:
        __writeDebug(debuglog, 'joined deleteGroup function in gappsmodule with gappsname ' + gappsname + ' and groupname ' + groupname)
    # try
    try:
        # Set Authentication information
        service = gdata.apps.groups.service.GroupsService(email=configdict[gappsname]["ADMINUSER"], domain=configdict[gappsname]["DOMAIN"], password=configdict[gappsname]["ADMINPASSWD"])

        # get Token
        service.ProgrammaticLogin()

        # Get Data
        service.DeleteGroup(groupname)

    # unless exception is raised
    except gdata.apps.service.AppsForYourDomainException , e:
        __handleError('deleteGroup', e)

    if debug:
        __writeDebug(debuglog, 'left deleteGroup function in gappsmodule with gappsname ' + gappsname)
    return True
# }}}

def changePassword(gappsname, username, password): # {{{
    """Change Password of Google Apps user
    name: the name of the Gapps Account to use
    username: username of the user
    password: the new password value
    """
    gappsname = 'GAPPS_' + gappsname

    if debug:
        __writeDebug(debuglog, 'joined changePassword function in gappsmodule with gappsname ' + gappsname + ',username ' + username + ' and a password')
    # try
    try:
        # Set Authentication information
        service = gdata.apps.service.AppsService(email=configdict[gappsname]["ADMINUSER"], domain=configdict[gappsname]["DOMAIN"], password=configdict[gappsname]["ADMINPASSWD"])

        # get Token
        service.ProgrammaticLogin()

        # get userentry object to modify
        _userobject = service.RetrieveUser(username)
        _userobject.login.password = password


        # Update User
        result = service.UpdateUser(username, _userobject)

    # unless exception is raised
    except gdata.apps.service.AppsForYourDomainException , e:
        __handleError('createUser', e)

    if debug:
        __writeDebug(debuglog, 'left changePassword function in gappsmodule with gappsname ' + gappsname)
    return True
    # }}}

def generatePassword(keylength=None): # {{{
    """Generate new Password
    keylength: length of the password
    returns the new password
    """
    if debug:
        __writeDebug(debuglog, 'joined generatePassword function in gappsmodule with keylength ' + str(keylength))
    _specialchars = '^!@#$%&*()-_+=.,?'
    _upperkeys = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _lowerkeys = 'abcdefghijklmnopqrstuvwxyz'
    _digits = '1234567890'
    _result=""
    if not ( keylength > 0 ):
        keylength = 10
    for i in range(keylength):
        _result += choice(choice(_specialchars) + choice(_upperkeys) + choice(_lowerkeys) + choice(_digits))
    for char in _result:
        if _specialchars.find(char) > 0:
            for char in _result:
                if _upperkeys.find(char) > 0:
                    for char in _result:
                        if _lowerkeys.find(char) > 0:
                            for char in _result:
                                if _digits.find(char) > 0:
                                    return _result
                                    break
    if debug:
        __writeDebug(debuglog, 'left generatePassword function in gappsmodule with a password')
    return generatePassword(keylength)
# }}}

# EOF
# vim:foldmethod=marker:autoindent:expandtab:tabstop=4
