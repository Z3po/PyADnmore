# -*- coding: UTF-8 -*-
'''
Copyright (C) 2011 Sebastian Cabrera
<scabrera-github@portachtzig.de> 
'''

import ldap
from datetime import datetime
from random import choice
import config
from sys import exit as __exit

debug = config.debug
debuglog = config.debuglog
configdict = config.configobject

# writes Debuglog
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
        __writeDebug(debuglog, 'joined handleError function in admodule with function ' + function + ' and Error ' + str(Error))
    if str(Error) == 'Server is unwilling to perform':
        print 'ERROR in ' + function + ': ' + str(Error)
        print 'Do you have SSL ENABLED??'
        print 'Does the new password meet the requirements?'
    elif str(Error) == 'Invalid credentials':
        print 'ERROR in ' + function + ': ' + str(Error)
        print 'BIND user or password is wrong'
    else:
        print 'ERROR in ' + function + ': ' + str(Error)
    __exit(2)
# }}}

def __ldap_connect(adname): # {{{

    adname = 'AD_' + adname

    if debug:
        __writeDebug(debuglog, 'joined __ldap_connect function with adname ' + adname)

    try:
        # try to open ldap connection
        lobject = ldap.initialize(configdict[adname]["HOSTNAME"])

        #lobject.set_option(LDAPOPTIONS)
        # bind to AD
        lobject.simple_bind_s(configdict[adname]["BINDUSER"],configdict[adname]["BINDPASSWD"])
    except (ldap.SERVER_DOWN, ldap.INVALID_CREDENTIALS), e:
        __handleError('__ldap_connect', e.args[0]["desc"])
    else:
        if debug:
            __writeDebug(debuglog, 'seems we successfully connected to ' + adname)
        return lobject, configdict[adname]["BASE"]

# }}}

def getuserAccountControl(value): # {{{
    """get userAccountControl by Name or Value
    you can hand the value of "userAccountControl" attribute and it will be translated to INT or STRING
    """

#   values from: http://support.microsoft.com/kb/305144
    _liststrings = ("SCRIPT","ACCOUNTDISABLE","HOMEDIR_REQUIRED","LOCKOUT","PASSWD_NOTREQD","PASSWD_CANT_CHANGE",
                    "ENCRYPTED_TEXT_PWD_ALLOWED","TEMP_DUPLICATE_ACCOUNT","NORMAL_ACCOUNT","INTERDOMAIN_TRUST_ACCOUNT","WORKSTATION_TRUST_ACCOUNT",
                    "SERVER_TRUST_ACCOUNT","DONT_EXPIRE_PASSWORD","MNS_LOGON_ACCOUNT","SMARTCARD_REQUIRED","TRUSTED_FOR_DELEGATION","NOT_DELEGATED",
                    "USE_DES_KEY_ONLY","DONT_REQ_PREAUTH","PASSWORD_EXPIRED","TRUSTED_TO_AUTH_FOR_DELEGATION")
    _listvalues = (1,2,8,16,32,64,128,256,512,2048,4096,8192,65536,131072,262144,524288,1048476,2097152,4194304,8388608,16777216)
    _result = []
    if debug:
        __writeDebug(debuglog, 'joined getuserAccountControl function in admodule with value ' + str(value))

    if isinstance(value,str):
        if value.isdigit():
            value = int(value)
            i = len(_listvalues)
            while value != 0 and i > 1:
                if value > _listvalues[i-1] or value == _listvalues[i-1]:
                    if _result:
                        _result.append( _liststrings[i-1] )
                    else:
                        _result.append( _liststrings[i-1] )
                    value -= _listvalues[i-1]
                i -= 1
        else:
            return 'STRANGE STRING?!?! WHERE YOU GOT THIS FROM??'
    else:
        if isinstance(value,list):
            i = len(_liststrings)
            _result = 0
            while i > 1:
                for key in value:
                    if key == _liststrings[i-1]:
                        _result += _listvalues[i-1]
                i -= 1
        else:
            return 'STRANGE TYPE?!?!? WHERE YOU GOT THIS FROM??'
    if not _result:
        _result = "not found"

    if debug:
        __writeDebug(debuglog, 'left getuserAccountControl function in admodule with result ' + str(_result))
        
    return _result
# }}}

def windowsTOunixtime(time): # {{{
    """
    get real time out of windowstime
    time: windows timestamp from attribute
    """

    if debug:
        __writeDebug(debuglog, 'joined windowsTOunixtime function in admodule with value ' + str(time))

    YearsFrom1601to1970 = 1970 - 1601
    DaysFrom1601to1970 = YearsFrom1601to1970 * 365
    DaysFrom1601to1970 += int(YearsFrom1601to1970 / 4) #leap years
    DaysFrom1601to1970 -= 3 # non-leap centuries (1700,1800,1900).  2000 is a leap century
    SecondsFrom1601to1970 = DaysFrom1601to1970 * 24 * 60 * 60

    TotalSecondsSince1601 = int(time / 10000000)

    TotalSecondsSince1970 = TotalSecondsSince1601 - SecondsFrom1601to1970
    timestamp = datetime.fromtimestamp(TotalSecondsSince1970)

    if debug:
        __writeDebug(debuglog, 'left windowsTounixtime function in admodule with result ' + str(timestamp))

    return timestamp
# }}}

def addObjectToGroup(adname, objectdn, groupdn): # {{{
    """add an Object to the given groupDN
    adname: name of the AD we use
    objectdn: DN of the group or userobject we want to add to the group
    groupdn: the DN of the group
    """
    groupmembers = getGroups(adname, groupdn)[0][1]['member']
    if objectdn in groupmembers:
        __handleError('addUserToGroup', objectdn + 'is already member of ' + groupdn)
    groupmembers.append(objectdn)
    changesdict = { 'member' : groupmembers }
    modifyObject(adname, groupdn, changesdict)
# }}}

def delObjectFromGroup(adname, objectdn, groupdn): # {{{
    """remove an Object from the given groupDN
    adname: name of the AD we use
    objectdn: DN of the group or userobject we want to remove from the group
    groupdn: the DN of the group
    """
    groupmembers = getGroups(adname, groupdn)[0][1]['member']
    if objectdn not in groupmembers:
        __handleError('addUserToGroup', objectdn + 'is no member of ' + groupdn)
    groupmembers.remove(objectdn)
    changesdict = { 'member' : groupmembers }
    modifyObject(adname, groupdn, changesdict)
# }}}

def getEntryByAttribute(adname, lookupstring): # {{{
    """get Entries from AD by its attributes
    adname: we need the name of the AD to use
    lookupstring: ldap Filter String
    returned: unsorted  list of results from AD
    """
    result = []

    if debug:
        __writeDebug(debuglog, 'joined getEntryByAttribute function in admodule with adname ' + adname + ' and lookupstring ' + str(lookupstring))

    lobject, searchbase = __ldap_connect(adname)

    try:
        # get all matching objects
        result = lobject.search_s(searchbase,ldap.SCOPE_SUBTREE,lookupstring)
        # unbind from ad
        lobject.unbind_s()
    # unless exception is raised
    except Exception, e:
        __handleError('getEntryByAttribute', e.args[0]["desc"])
    # if no exception is raised, return results after popping "waste" (nobody needs "None")
    else:
        while result[(len(result)-1)][0] == None:
            result.pop()
            if len(result) == 0:
                break

    if debug:
        __writeDebug(debuglog, 'left getEntryByAttribute function in admodule with adname ' + adname + 'and resultset with a length of ' + str(len(result)))

    return result
# }}}

def getUsers(adname, username): # {{{
    """get Users from AD
    adname: we need the name of the AD to use
    username: we need the name of the user to search for or * for all
    returned: List of Users sorted by sAMAccountName
    NOTE: username can be: sAMAccountName, name, givenName, sn, distinguishedName, mail, userPrincipalName
    """
    result = ''
    _itemdict = {}
    _counter = 0
    _tempresult = []
    if debug:
        __writeDebug(debuglog, 'joined getUsers in admodule with adname ' + adname + ' and username ' + username)

    lobject, searchbase = __ldap_connect(adname)

    try:
        # get all matching users
        result = lobject.search_s(searchbase,ldap.SCOPE_SUBTREE,'(|(&(sAMAccountName=%s)(objectCategory=person)(objectClass=user))(&(name=%s)(objectCategory=person)(objectClass=user))(&(givenName=%s)(objectCategory=person)(objectClass=user))(&(sn=%s)(objectCategory=person)(objectClass=user))(&(distinguishedName=%s)(objectCategory=person)(objectClass=user))(&(mail=%s)(objectCategory=person)(objectClass=user))(&(userPrincipalName=%s)(objectCategory=person)(objectClass=user)))' % (username, username, username, username, username, username, username))
        # unbind from ad
        lobject.unbind_s()
    # unless exception is raised
    except Exception, e:
        __handleError('getUsers', e.args[0]["desc"])
    # if no exception is raised, return results after popping "waste" (again nobody needs "None")
    else:
        while result[(len(result)-1)][0] == None:
            result.pop()
            if len(result) == 0:
                break
        # Sort the results by sAMAcountName
        for _entry in result:
            _itemdict.update({ _entry[1]["sAMAccountName"][0] : _counter })
            _counter += 1
        _sorted = sorted((key.lower(), value) for (key, value) in _itemdict.iteritems())
        for key, value in _sorted:
            _tempresult.append( result[value] )
        result = _tempresult

    if debug:
        __writeDebug(debuglog, 'left getUsers in admodule with adname ' + adname + ' and resultset with a length of ' + str(len(result)))

    return result
# }}}

def getGroups(adname, groupname): # {{{
    """get Groups from AD
    adname: we need the name of the AD to use
    groupname: name of the goup to search for or * for all
    returned: List of Groups sorted by sAMAccountName
    NOTE: groupname can be: sAMAccountName, name, distinguishedName
    """
    _itemdict = {}
    _counter = 0
    _tempresult = []
    if debug:
        __writeDebug(debuglog, 'joined getGroups function in admodule with adname ' + adname + ' and groupname ' + groupname)

    lobject, searchbase = __ldap_connect(adname)

    try:
        # get all matching gruops
        result = lobject.search_s(searchbase,ldap.SCOPE_SUBTREE,'(|(&(objectCategory=group)(sAMAccountName=%s))(&(objectCategory=group)(name=%s))(&(objectCategory=group)(distinguishedName=%s)))' % (groupname, groupname, groupname))
        # unbind from AD
        lobject.unbind_s()
    # unless exception is raised
    except Exception, e:
        __handleError('getGroups', e.args[0]["desc"])
    # if no exception is raised, return results after popping "waste"
    else:
        while result[(len(result)-1)][0] == None:
            result.pop()
            if len(result) == 0:
                break
        # Sort results by sAMAccountName
        for _entry in result:
            _itemdict.update({ _entry[1]["sAMAccountName"][0] : _counter })
            _counter += 1
        _sorted = sorted((key.lower(), value) for (key, value) in _itemdict.iteritems())
        for key, value in _sorted:
            _tempresult.append( result[value] )
        result = _tempresult

    if debug:
        __writeDebug(debuglog, 'left getGroups function in admodule with adname ' + adname + ' and resultset with a length of ' + str(len(result)))
    return result
# }}}

def getContacts(adname, contact): # {{{
    """get Contacts from AD
    adname: we need the name of the AD to use
    contact: name of the contact to search for, * for all
    returned: List of Groups sorted by sAMAccountName
    NOTE: contact can be any of: name, displayName, distinguishedName, email
    """
    _itemdict = {}
    _counter = 0
    _tempresult = []
    if debug:
        __writeDebug(debuglog, 'joined getContacts function in admodule with adname ' + adname + ' and contact ' + contact)

    lobject, searchbase = __ldap_connect(adname)

    try:
        # get all matching gruops
        result = lobject.search_s(searchbase,ldap.SCOPE_SUBTREE,'(|(&(objectClass=contact)(objectCategory=person)(name=%s))(&(objectClass=contact)(objectCategory=person)(displayName=%s))(&(objectClass=contact)(objectCategory=person)(distinguishedName=%s))(&(objectClass=contact)(objectCategory=person)(targetAddress=SMTP:%s)))' % (contact, contact, contact, contact))
        # unbind from AD
        lobject.unbind_s()
    # unless exception is raised
    except Exception, e:
        __handleError('getGroups', e.args[0]["desc"])
    # if no exception is raised, return results after popping "waste" (deletion of None)
    else:
        while result[(len(result)-1)][0] == None:
            result.pop()
            if len(result) == 0:
                break
        # Sort results by name
        for _entry in result:
            _itemdict.update({ _entry[1]["name"][0] : _counter })
            _counter += 1
        _sorted = sorted((key.lower(), value) for (key, value) in _itemdict.iteritems())
        for key, value in _sorted:
            _tempresult.append( result[value] )
        result = _tempresult

    if debug:
        __writeDebug(debuglog, 'left getContacts function in admodule with adname ' + adname + ' and resultset with a length of ' + str(len(result)))
    return result
# }}}

def createUser(adname, dn, userdict): # {{{
    """add a User to Active Directory
    adname: we need the name of the AD here too
    dn: DN path of the new user
    userdict: dictionary with values to set
    NOTE: needed attributes are: displayName, givenName, name, sn, sAMAccountName, userPrincipalName, objectClass
    """
    _neededAttributes = ( 'displayName', 'givenName', 'name', 'sn', 'sAMAccountName', 'userPrincipalName', 'pwdLastSet', 'objectClass' )
    _user = []
    if debug:
        __writeDebug(debuglog, 'joined createUser function in admodule with adname ' + adname + ', dn ' + dn + ' and userdict ' + str(userdict))

    # create list out of user dictionary
    for _attribute in _neededAttributes:
        if _attribute in userdict:
            _user.append((_attribute, userdict[_attribute]))
        else:
            if _attribute == 'pwdLastSet':
                _user.append(_attribute, '0')
            else:
                __handleError('createUser', 'MISSING attribute ' + _attribute)

        for attname in userdict:
            _user.append((attname, userdict[attname]))

    # here happens the magic
    lobject, searchbase = __ldap_connect(adname)

    try:
        # add user to AD
        lobject.add_s(dn,_user)
        # unbind from AD
        lobject.unbind_s()
    except Exception, e:
        __handleError('createUser', e.args[0]["desc"])
    if debug:
        __writeDebug(debuglog, 'left createUser function in admodule with adname ' + adname)
# }}}

def createGroup(adname, dn, groupdict):
    pass

def deleteObject(adname, dn): # {{{
    """delete a User from Active Directory
    adname: we need the name of the AD here too
    dn: DN of the object we need to delete
    """
    if debug:
        __writeDebug(debuglog, 'joined deleteObject function in admodule with adname ' + adname + ' and dn ' + dn)

    lobject, searchbase = __ldap_connect(adname)

    try:
        # add user to AD
        lobject.delete_s(dn)
        # unbind from AD
        lobject.unbind_s()
    except Exception, e:
        __handleError('deleteADUser', e.args[0]["desc"])
    if debug:
        __writeDebug(debuglog, 'left deleteAdObject function in admodule with adname ' + adname)
# }}}

def modifyObject(adname, dn, moddict): # {{{
    """modify a Active Directory user
    adname: we need the name of the AD here too
    dn: DN path of the user
    moddict: dictionary of object attributes to change
    NOTE: you can add just changed attributes here, no value to delete the attribute
    """
    _modattrs = []
    if debug:
        __writeDebug(debuglog, 'joined modifyObject function in admodule with adname ' + adname + ',dn ' + dn + ' and moddict ' + str(moddict))
    # generate modlist out of given dictionary
    for attname in moddict:
        if moddict[attname]:
            if isinstance(moddict[attname],list):
                if len(moddict[attname]) > 1:
                    _modattrs.append((ldap.MOD_REPLACE, attname, moddict[attname]))
                else:
                    _modattrs.append((ldap.MOD_REPLACE, attname, str(moddict[attname][0])))
            else:
                _modattrs.append((ldap.MOD_REPLACE, attname, str(moddict[attname])))
        else:
            _modattrs.append((ldap.MOD_DELETE, attname, None))
    # here happens the magic
    lobject, searchbase = __ldap_connect(adname)
    try:
        # modify AD dn object
        lobject.modify_s(dn,_modattrs)
        # unbind from AD
        lobject.unbind_s()
    except Exception, e:
        __handleError('modifyObject', e.args[0]["desc"])
    if debug:
        __writeDebug(debuglog, 'left modifyObject function in admodule with adname ' + adname)
# }}}

def changePassword(adname, dn, password): # {{{
    """Change Password of AD user
    adname: the name of the AD to use
    dn: dn of the user
    password: the new password value
    """
    if debug:
        __writeDebug(debuglog, 'joined changePassword function in admodule with adname ' + adname + ',dn ' + dn + ' and a secret password :)')

    lobject, searchbase = __ldap_connect(adname)

    try:
        # !! got this snippet from: http://snipt.net/Fotinakis/tag/active%20directory

        # Encode the password in UTF-16 Little Endian
        #
        # ASCII "new":     0x6E 0x65 0x77
        # UTF-16 "new":    0x6E 0x00 0x65 0x00 0x77 0x00
        # UTF-16 "new"
        #     with quotes: 0x22 0x00 0x6E 0x00 0x65 0x00 0x77 0x00 0x22 0x00
        #
        # http://msdn.microsoft.com/en-us/library/cc200469%28PROT.10%29.aspx
        #
        # NOTE: The article says to BER encode the password octet stream before
        # sending for change, but doing so causes the server to give its standard
        # "will not perform" error on password change. So, no BER encoding is done here.
        #
        ## WARNING: Password is needed in quotation marks! I did make that fault changing it
        ## and got CONSTRAINT_VIOLATION Errors

        # encode new password
        new_password = ('"%s"' % password).encode("utf-16-le")

        # For some reason, two MOD_REPLACE calls are necessary to change the password.
        # If only one call is performed, both the old and new password will work.
        ## could not reproduce it...i just got one working password. Nevertheless didn't change the original script.
        _modattrs = [( ldap.MOD_REPLACE, 'unicodePwd', new_password),( ldap.MOD_REPLACE, 'unicodePwd', new_password)]
        # modify the dn object
        lobject.modify_s(dn, _modattrs)
        # unbind from ad
        lobject.unbind_s()
    except Exception, e:
        __handleError('changePassword', e.args[0]["desc"])
    if debug:
        __writeDebug(debuglog, 'left changePassword function in admodule with adname ' + adname)
    # }}}

def generatePassword(keylength=None): # {{{
    """Generate new Password
    keylength: length of the password
    returns the new password
    """
    if debug:
        __writeDebug(debuglog, 'joined generatePassword function in admodule with keylength ' + str(keylength))
    _specialchars = '^!@#$%&*()-_+=.,?'
    _upperkeys = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _lowerkeys = 'abcdefghijklmnopqrstuvwxyz'
    _digits = '1234567890'
    result=""
    if not ( keylength > 0 ):
        keylength = 10
    for i in range(keylength):
        result += choice(choice(_specialchars) + choice(_upperkeys) + choice(_lowerkeys) + choice(_digits))
    for char in result:
        if _specialchars.find(char) > 0:
            for char in result:
                if _upperkeys.find(char) > 0:
                    for char in result:
                        if _lowerkeys.find(char) > 0:
                            for char in result:
                                if _digits.find(char) > 0:
                                    return result
                                    break
    __writeDebug(debuglog, 'left generatePassword function in admodule with a password')
    return generatePassword(keylength)
# }}}

# EOF
# vim:foldmethod=marker:autoindent:expandtab:tabstop=4
