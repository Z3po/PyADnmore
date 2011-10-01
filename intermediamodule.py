# -*- coding: UTF-8 -*-
'''
Copyright (C) 2010 Sebastian Cabrera
<scabrera@astaro.com>
'''

import urllib, urllib2
import ldap
from sys import exit as __exit
import config
import re
import MultipartPostHandler
from datetime import datetime
from random import choice

configdict = config.configobject
debug = config.debug
debuglog = config.debuglog

# Write Debug to logfile
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
        __writeDebug(debuglog, 'joined __handleError function in intermediamodule with function ' + function + ' and Error ' + str(Error))
    if str(Error) == 'Invalid credentials':
        print 'ERROR in ' + function + ': ' + str(Error) 
        print 'BIND user or password is wrong'
    else:
        print 'ERROR in ' + function + ': ' + str(Error)
    __exit(2)
# }}}

# loging in to intermedia
def __login_multipart(accountname): # {{{
    try:
        # Set intermedia Login
        intermedia_login_data = urllib.urlencode({"userName" : configdict[accountname]["MANAGERLOGIN"], "password" : configdict[accountname]["MANAGERPASSWD"]})

        # Setup Connection
        intermedia_connector = urllib2.build_opener(urllib2.HTTPCookieProcessor(), MultipartPostHandler.MultipartPostHandler)

        # Set headers (to identify in logfile)
        intermedia_connector.addheaders = [("User-Agent", "PyADnmore v0.0.1")]

        # Sent Authentication information (login)
        intermedia_connect = intermedia_connector.open("https://%s/asp/User/Management.asp" % (configdict[accountname]["MANAGERURL"]), intermedia_login_data)
        if re.findall(r"HostPilot for Account ",intermedia_connect.read()):
            pass
        else:
            __handleError('_login', 'Could not login to Intermedia')

    except Exception, e:
        __handleError('_login', e)
    else:
        return intermedia_connector
# }}}

def __ldap_connect(domain): # {{{
    if debug:
            __writeDebug(debuglog, 'joined __ldap_connect function with domain ' + domain)

    try:
        # try to open ldap connection
        lobject = ldap.initialize(configdict[domain]["LDAPHOST"])

        #lobject.set_option(LDAPOPTIONS)
        # bind to AD
        lobject.simple_bind_s(configdict[domain]["BINDUSER"],configdict[domain]["BINDPASSWD"])
    except (ldap.SERVER_DOWN, ldap.INVALID_CREDENTIALS), e:
        __handleError('__ldap_connect', e.args[0]["desc"])

    else:
        if debug:
            __writeDebug(debuglog, 'seems we successfully connected to ' + domain)
        return lobject

# }}}

def getEntryByAttribute(domain, lookupstring): # {{{
    """get Entries from Intermedia by its attributes
    domain: we need the name of the DOMAIN to use
    lookupstring: ldap Filter String
    return: unsorted list of all matching objects
    """


    domain = 'IM_' + domain
    result = []

    if debug:
        __writeDebug(debuglog, 'joined getEntryByAttribute function in intermediamodule with domain ' + domain + ' and lookupstring ' + str(lookupstring))

    lobject = __ldap_connect(domain)

    try:
        # get all matching Objects
        result = lobject.search_s(configdict[domain]["BASE"],ldap.SCOPE_SUBTREE, lookupstring)
        # unbind from ldap
        lobject.unbind_s()
    # unless exception is raised
    except ldap.NO_SUCH_OBJECT, e:
        return result
    except Exception, e:
        __handleError('getEntryByAttribute', e.args[0]["desc"])
    # if no exception is raised, return results after popping "waste"
    else:
        while result[(len(result)-1)][0] == None:
            result.pop()
            if len(result) == 0:
                break
    if debug:
        __writeDebug(debuglog, 'left getEntryByAttribute function in intermediamodule with domain ' + domain + ' and resultset with a length of ' + str(len(result)))
    return result
# }}}

def getUsers(domain, username): # {{{
    """get Userss from Intermedia
    domain: we need the name of the DOMAIN to use
    username: we need the name of the user to search for or * for all
    return: list of matching User Objects sorted by sAMAccountName
    NOTE: username can be any of: sAMAccountName, name, givenName, sn, distinguishedName, mail, displayName, userPrincipalName
    """

    domain = 'IM_' + domain

    _itemdict = {}
    _counter = 0
    _tempresult = []
    if debug:
        __writeDebug(debuglog, 'joined getUsers function in intermediamodule with domain ' + domain + ' and username ' + username)

    lobject = __ldap_connect(domain)

    try:
        # get all matching Mailboxes
        result = lobject.search_s(configdict[domain]["BASE"],ldap.SCOPE_SUBTREE,'(|(&(sAMAccountName=%s)(objectCategory=person)(objectClass=user))(&(name=%s)(objectCategory=person)(objectClass=user))(&(givenName=%s)(objectCategory=person)(objectClass=user))(&(sn=%s)(objectCategory=person)(objectClass=user))(&(distinguishedName=%s)(objectCategory=person)(objectClass=user))(&(mail=%s)(objectCategory=person)(objectClass=user))(&(displayName=%s)(objectCategory=person)(objectClass=user))(&(userPrincipalName=%s)(objectCategory=person)(objectClass=user)))' % (username, username, username, username, username, username, username, username))
        # unbind from ldap
        lobject.unbind_s()
    # unless exception is raised
    except ldap.NO_SUCH_OBJECT, e:
        return _tempresult
    except Exception, e:
        __handleError('getUsers', e.args[0]["desc"])
    # if no exception is raised, return results after popping "waste" (noone needs "None")
    else:
        while result[(len(result)-1)][0] == None:
            result.pop()
            if len(result) == 0:
                break

        for _entry in result:
            _itemdict.update({ _entry[1]["sAMAccountName"][0] : _counter })
            _counter += 1
        _sorted = sorted((key.lower(), value) for (key, value) in _itemdict.iteritems())
        for key, value in _sorted:
            _tempresult.append( result[value] )
        result = _tempresult
    if debug:
        __writeDebug(debuglog, 'left getUsers function in intermediamodule with domain ' + domain + ' and resultset with a length of ' + str(len(result)))
    return result
# }}}

def getGroups(domain, group): # {{{
    """get Mailinglists from Intermedia
    domain: we need the name of the DOMAIN to use
    groupname: name of the goup to search for or * for all
    return: list of matching Group Objects sorted by sAMAccountName
    NOTE: group can be any of: sAMAccountName, name, distinguishedName, mail
    """

    domain = 'IM_' + domain
    result = []

    _itemdict = {}
    _counter = 0
    _tempresult = []
    if debug:
        __writeDebug(debuglog, 'joined getMailinglists function in intermediamodule with domain ' + domain + ' and group ' + group)

    lobject = __ldap_connect(domain)

    try:
        # get all matching gruops
        result = lobject.search_s(configdict[domain]["BASE"],ldap.SCOPE_SUBTREE,'(|(&(objectCategory=group)(sAMAccountName=%s))(&(objectCategory=group)(name=%s))(&(objectCategory=group)(distinguishedName=%s))(&(objectCategory=group)(mail=%s)))' % (group, group, group, group))
        # unbind from AD
        lobject.unbind_s()
    # unless exception is raised
    except ldap.NO_SUCH_OBJECT, e:
        return result
    except Exception, e:
        __handleError('getMailinglists', e.args[0]["desc"])
    # if no exception is raised, return results after popping "waste" (again nobody needs "None")
    else:
        while result[(len(result)-1)][0] == None:
            result.pop()
            if len(result) == 0:
                break

        for _entry in result:
            _itemdict.update({ _entry[1]["sAMAccountName"][0] : _counter })
            _counter += 1
        _sorted = sorted((key.lower(), value) for (key, value) in _itemdict.iteritems())
        for key, value in _sorted:
            _tempresult.append( result[value] )
        result = _tempresult
    if debug:
        __writeDebug(debuglog, 'left getMailinglists function in intermediamodule with domain ' + domain + ' and a resultset with a length of ' + str(len(result)))
    return result
# }}}

def getContacts(domain, contact): # {{{
    """get Contacts from Intermedia
    domain: we need the name of the DOMAIN to use
    contact: we need the name of the user to search for or * for all
    return: list of matching contact objects sorted by name
    NOTE: contact can be any of: name, displayName, distinguishedName, email
    """

    domain = 'IM_' + domain

    _itemdict = {}
    _counter = 0
    _tempresult = []
    if debug:
        __writeDebug(debuglog, 'joined getContacts function in intermediamodule with domain ' + domain + ' and contact ' + contact)

    lobject = __ldap_connect(domain)

    try:
        # get all matching Contacts
        result = lobject.search_s(configdict[domain]["BASE"],ldap.SCOPE_SUBTREE,'(|(&(name=%s)(objectCategory=person)(objectClass=contact))(&(displayName=%s)(objectCategory=person)(objectClass=contact))(&(distinguishedName=%s)(objectCategory=person)(objectClass=contact))(&(targetAddress=SMTP:%s)(objectCategory=person)(objectClass=contact)))' % (contact, contact, contact, contact))
        # unbind from ldap
        lobject.unbind_s()
    # unless exception is raised
    except ldap.NO_SUCH_OBJECT, e:
        return _tempresult
    except (ldap.SERVER_DOWN, ldap.INVALID_CREDENTIALS), e:
        __handleError('geContacts', e.args[0]["desc"])
    # if no exception is raised, return results after popping "waste" (removing "None")
    else:
        while result[(len(result)-1)][0] == None:
            result.pop()
            if len(result) == 0:
                break

        for _entry in result:
            _itemdict.update({ _entry[1]["name"][0] : _counter })
            _counter += 1
        _sorted = sorted((key.lower(), value) for (key, value) in _itemdict.iteritems())
        for key, value in _sorted:
            _tempresult.append( result[value] )
        result = _tempresult
    if debug:
        __writeDebug(debuglog, 'left getContacts function in intermediamodule with domain ' + domain + ' and a resultset with a length of ' + str(len(result)))
    return result
# }}}

def createContact(accountname, userdict): # {{{
    """creates Contacts at Intermedia
    userdict: dictionary of the user to create
    Needed values:
                  -> displayName: Display Name of the new Contact
                  -> emailName: The Contacts Email Address
    """

    accountname = 'IM_' + accountname

    # Prepare dictionary to post
    _userdict = { }
    if debug:
        __writeDebug(debuglog, 'joined createContact function in intermediamodule with accountname ' + accountname + ' and userdict ' + str(userdict))
    if 'displayName' in userdict:
            _userdict.update({ 'displayName' : userdict["displayName"] })
            _userdict.update({ 'dispName' : userdict["displayName"]  })
    else:
            __handleError('createContact', 'ATTRIBUTE ERROR MISSING: displayName')

    if 'emailName' in userdict:
        _userdict.update({ 'emailName' : userdict["emailName"] })
    else:
        __handleError('createContact', 'ATTRIBUTE ERROR MISSING: emailName')

    intermedia_connector = __login_multipart(accountname)

    try:
        intermedia_connect = intermedia_connector.open("https://%s/asp/User/MSExchange/CreateContacts.asp?action=createItems&chargeOptions=" % (configdict[accountname]["MANAGERURL"]), _userdict)
        if re.findall(r"were successfully created",intermedia_connect.read()):
            pass
        else:
            __handleError('createContact', 'Could not Create Contact')

    except Exception, e:
        __handleError('createContact', e)
    if debug:
        __writeDebug(debuglog, 'left createContact function in intermediamodule with accountname ' + accountname)
# }}}

def createUser(accountname, userdict): # {{{
    """creates Users at Intermedia
    userdict: dictionary of the user to create
    Needed values:
                  -> displayName: Display Name of the new User
                  -> sAMAccountName: sAMAccountName the User will have will also be the part before the @ of the Email Address
                  -> notificationEmail: Address where to send the notification about the Mailbox created to
                  -> emailDomain: Domain of the users Email Address
    """
    accountname = 'IM_' + accountname

    # Prepare dictionary to post
    _userdict = { 'emailDomainValue0' : "" }

    if debug:
        __writeDebug(debuglog, 'joined createUser function in intermediamodule with accountname ' + accountname + ' and userdict ' + str(userdict))
    if 'displayName' in userdict:
            _userdict.update({ 'displayName' : userdict["displayName"] })
            _userdict.update({ 'dispName' : userdict["displayName"]  })
    else:
            __handleError('createUser', 'ATTRIBUTE ERROR MISSING: displayName')

    if 'sAMAccountName' in userdict:
        _userdict.update({ 'emailName' : userdict["sAMAccountName"] })
    else:
        __handleError('createUser', 'ATTRIBUTE ERROR MISSING: sAMAccountName')

    if 'notificationEmail' in userdict:
        _userdict.update({ 'notificationEmail' : userdict["notificationEmail"] })
    else:
        __handleError('createUser', 'ATTRIBUTE ERROR MISSING: notificationEmail')

    if 'emailDomain' in userdict:
        _userdict.update({ 'emailDomain' : userdict["emailDomain"] })
    else:
        __handleError('createUser', 'ATTRIBUTE ERROR MISSING: emailDomain')

    # get intermedia connector object
    intermedia_connector = __login_multipart(accountname)

    try:
        intermedia_connect = intermedia_connector.open("https://%s/asp/User/MSExchange/CreateMailboxes.asp?action=createItems&chargeOptions=" % (configdict[accountname]["MANAGERURL"]), _userdict)
        if re.findall(r"were successfully created",intermedia_connect.read()):
            pass
        else:
            __handleError('createUser', 'Could not Create Mailbox')

    except Exception, e:
        __handleError('createUser', e)
    if debug:
        __writeDebug(debuglog, 'left createUser function in intermediamodule with accountname ' + accountname)
# }}}

def createGroup(accountname, groupdict): # {{{
    """creates group objects at Intermedia 
    groupdict: dictionary of the group to create
    Needed values:
                  -> dispName: Display Name of the Group Object
                  -> emailName: part before the @ of the Email Address
                  -> emailDomain: part after the @ of the Email Address
    """
    accountname = 'IM_' + accountname

    _groupdict = {}
    if debug:
        __writeDebug(debuglog, 'joined createGroup function in intermediamodule with accountname ' + accountname + ' and groupdict ' + str(groupdict))
    if 'dispName' in groupdict:
        _groupdict.update({ 'dispName' : groupdict["dispName"] })
    else:
        __handleError('createGroup', 'ATTRIBUTE ERROR MISSING: dispName')

    if 'emailName' in groupdict:
        _groupdict.update({ 'emailName' : groupdict["emailName"] })
    else:
        __handleError('createGroup', 'ATTRIBUTE ERROR MISSING: emailName')

    if 'emailDomain' in groupdict:
        _groupdict.update({ 'emailDomain' : groupdict["emailDomain"] })
    else:
        __handleError('createGroup', 'ATTRIBUTE ERROR MISSING: emailDomain')

    # get intermedia connector
    intermedia_connector = __login_multipart(accountname)

    try:
        intermedia_connect = intermedia_connector.open("https://%s/asp/User/MSExchange/CreateDistributionLists.asp?action=createItems&chargeOptions=" % (configdict[accountname]["MANAGERURL"]), _groupdict)

        if re.findall(r"were successfully created",intermedia_connect.read()):
            pass
        else:
            __handleError('createGroup', 'Could not Create Group')

    except Exception, e:
        __handleError('createGroup', e)
    if debug:
        __writeDebug(debuglog, 'left createGroup function in intermediamodule with accountname ' + accountname)
# }}}

def changeMailboxAdvanced(accountname, changesdict): # {{{
    """address Changes to the "Advanced" tab of the Mailbox in Hostpilot
    accountname: Accountname used for the connection
    changesdict: Dictionary containing the changes
    needed values:
                  -> identity: sAMAccountName of the User Object
    valid values:
                  -> mailboxDisabled:  0 enables and 1 disables the User
                  -> smtprelayEnabled: 1 enables and 0 disables the SMTP Relay for the User
                  -> msExchOmaAdminWirelessEnable2: 1 enables and 0 disables Outlook Mobile Access
                  -> msExchHideFromAddressLists: 1 hides and 0 unhides the user from the GAL
                  -> msExchOmaAdminWirelessEnable1: 1 enables and 0 disables UptoDate notifications
                  -> imap4: 1 enables and 0 disables IMAP for the user
                  -> http: 1 enables 0 disables OWA for the user
                  -> pop3: 1 enables 0 disalbes pop3 for the user
                  -> sAMAccountName: new sAMAccountName of the User object
                  -> submissionContLength: Outgoing Message Size Limit (KB)
                  -> delivContLength: Incoming Message Size Limit (KB)
                  -> msExchRecipLimit: Limit the number of recipients
    """
    accountname = 'IM_' + accountname

    if debug:
        __writeDebug(debuglog, 'joined changeMailboxAdvanced function in intermediamodule with accountname ' + accountname + ' and changesdict ' + str(changesdict))

    # urlencode the dict
    intermedia_changes = urllib.urlencode(changesdict)

    # get intermedia login object
    intermedia_connector = __login_multipart(accountname)

    intermedia_connect = intermedia_connector.open("https://%s/asp/User/MSExchange/EditMailbox/Advanced.asp?action=saveChanges&" % (configdict[accountname]["MANAGERURL"]), intermedia_changes)
    if re.findall(r"were successfully saved",intermedia_connect.read()):
        pass
    else:
        __handleError('changeMailboxAdvanced', 'Could not apply changes')
    if debug:
        __writeDebug(debuglog, 'left changeMailboxAdvanced function in intermediamodule with accountname ' + accountname)
# }}}

def changeMailboxDeliveryOptions(accountname, changesdict): # {{{
    """address changes to the "Delivery Options" tab of the Mailbox
    accountname: Accountname of the intermedia Account to use
    changesdict: a dict containing the changes
    needed values:
                  -> identity: sAMAccountName of the Mailbox you want to change
    valid values:
                  -> altRecipient: DN of the Object you want to deliver to
                  -> acceptFrom: all for all
                  -> deliverAndRedirect: 0 for only redirect 1 for redirect and local delivery
                  -> rejectFrom: none for none
    """
    accountname = 'IM_' + accountname

    if debug:
        __writeDebug(debuglog, 'joined changeMailboxDeliveryOptions function in intermediamodule with accountname ' + accountname + ' and changesdict ' + str(changesdict))

    # urlencode the changes dict
    intermedia_changes = urllib.urlencode(changesdict)

    # get intermedia connector object
    intermedia_connector = __login_multipart(accountname)

    intermedia_connect = intermedia_connector.open("https://%s/asp/User/MSExchange/EditMailbox/DeliveryOptions.asp?action=saveRestrictions&" % (configdict[accountname]["MANAGERURL"]), intermedia_changes)
    if not re.findall(r"Cannot save delivery restrictions of mailbox",intermedia_connect.read()):
        pass
    else:
        __handleError('changeMailboxDeliveryOptions', 'Could not apply changes')
    if debug:
        __writeDebug(debuglog, 'left changeMailboxDeliveryOptions function in intermediamodule with accountname ' + accountname)
# }}}

def changeMailboxGeneral(accountname, changesdict): # {{{
    """address Changes to the "General" tab of the Mailbox in Hostpilot
    accountname: Accountname of the Intermedia Account to use
    changesdict: a dict containing the changes
    needed values:
                  -> identity: sAMAccountName of the user object
                  -> title: Job Title of the User object
                  -> company: Company the user is working in
                  -> department: Department of the user
                  -> st: State of the User
                  -> co: Country the User is in
                  -> givenName: First Name of the User
                  -> sn: Surname of the User
                  -> physicalDeliveryOfficeName: Location of the Office
                  -> initials: Initials of the User
                  -> displayName: Display Name of the User
                  -> employeeID: Employee ID
                  -> employeeNumber: Employee Number
                  -> ipPhone: IP Phone
                  -> employeeType: Employee Type
                  -> homePhone: Home Phone Number
                  -> telephoneNumber: Business Phone Number
                  -> mobile: Mobile Phone Number
                  -> facsimileTelephoneNumber: Fax Number
                  -> wWWHomePage: Website
                  -> telephoneAssistant: Assistants Phone Number
                  -> streetAddress: Address of the User
                  -> info: Notes
                  -> l: City of the User
                  -> postalCode: Zip Code
    """
    accountname = 'IM_' + accountname

    if debug:
        __writeDebug(debuglog, 'joined changeMailboxGeneral function in intermediamodule with accountname ' + accountname + ' and changesdict ' + str(changesdict))

        # urlencode the changesdict
        intermedia_changes = urllib.urlencode(changesdict)

        # get intermedia connector
        intermedia_connector = __login_multipart(accountname)

    try:
        intermedia_connect = intermedia_connector.open("https://%s/asp/User/MSExchange/EditMailbox/General.asp?action=saveChanges&" % (configdict[accountname]["MANAGERURL"]), intermedia_changes)
        if re.findall(r"were successfully saved",intermedia_connect.read()):
            pass
        else:
            __handleError('changeMailboxGeneral', 'Could not apply changes')
    except Exception, e:
        __handleError('changeMailboxGeneral', e)
    if debug:
        __writeDebug(debuglog, 'left changeMailboxGeneral function in intermediamodule with accountname ' + accountname)
# }}}

def addMailboxEmailAddresses(accountname, changesdict): # {{{
    """add adresses to mailboxes
    accountname: name of the IntermediaAccount to use (configfile)
    changesdict: a dict containing the changes
    needed values:
                  -> identity: sAMAccountName of the user object
                  -> prefix: part before the @
                  -> domain: part after the @
    """
    accountname = 'IM_' + accountname
    if debug:
        __writeDebug(debuglog, 'joined addMailboxEmailAddresses function in intermediamodule with accountname ' + accountname + ' and changesdict ' + str(changesdict))

    if 'identity' not in changesdict:
        __handleError('addMailboxEmailAddresses','Missing needed value identity in changesdict')
    if 'prefix' not in changesdict:
        __handleError('addMailboxEmailAddresses','Missing needed value prefix in changesdict')
    if 'domain' not in changesdict:
        __handleError('addMailboxEmailAddresses','Missing needed value domain in changesdict')

    # urlencode the changesdict
    intermedia_changes = urllib.urlencode(changesdict)

    # get the intermedia connector
    intermedia_connector = __login_multipart(accountname)

    try:
        intermedia_connect = intermedia_connector.open("https://%s/asp/User/MSExchange/EditMailbox/EmailAddresses.asp?action=createAddress&" % (configdict[accountname]["MANAGERURL"]), intermedia_changes)
        if re.findall(r"were successfully added to Mailbox",intermedia_connect.read()):
            pass
        else:
            __handleError('addMailboxEmailAddress', 'Could not add')
    except Exception, e:
        __handleError('addMailboxEmailAddress', e)
    if debug:
        __writeDebug(debuglog, 'left addMailboxEmailAddress function in intermediamodule with accountname ' + accountname)
# }}}

def delMailboxEmailAddresses(accountname, changesdict): # {{{
    """remove adresses from mailboxes
    accountname: Name of the IntermediaAccount to use (configfile)
    changesdict: the Dict containing the changes
    needed values:
                  -> identity: sAMAccounName of the user object
                  -> otherProxyAddress: addresses to remove
    """
    accountname = 'IM_' + accountname

    if debug:
        __writeDebug(debuglog, 'joined delMailboxEmailAddresses function in intermediamodule with accountname ' + accountname + ' and changesdict ' + str(changesdict))

    # check if needed values are present
    if 'identity' not in changesdict:
        __handleError('delMailboxEmailAddress', 'Missing identity in changesdict')
    if 'otherProxyAddress' not in changesdict:
        __handleError('delMailboxEmailAddress', 'Missing otherProxyAddress in changesdict')

    # urlencode the dict
    intermedia_changes = urllib.urlencode(changesdict)

    # setup the intermedia connector
    intermedia_connector = __login_multipart(accountname)

    try:
        intermedia_connect = intermedia_connector.open("https://%s/asp/User/MSExchange/EditMailbox/EmailAddresses.asp?action=deleteAddresses&" % (configdict[accountname]["MANAGERURL"]), intermedia_changes)
        if re.findall(r"were successfully removed from Mailbox",intermedia_connect.read()):
            pass
        else:
            __handleError('delMailboxEmailAddress', 'Could not delete')
    except Exception, e:
        __handleError('delMailboxEmailAddress', e)
    if debug:
        __writeDebug(debuglog, 'left dellMailboxEmailAddress function in intermediamodule with accountname ' + accountname)
# }}}

def deleteMailbox(accountname, username): # {{{
    """delete Mailboxes from your Account
    accountname: Accountname to establish the connectoin
    username: sAMAccountName of the User you want to delete
    """
    accountname = 'IM_' + accountname

    if debug:
        __writeDebug(debuglog, 'joined deleteMailbox function in intermediamodule with accountname ' + accountname + ' and username ' + username)
    
    # get the intermedia connector
    intermedia_connector = __login_multipart(accountname)

    # set the post value
    _deletemailbox = urllib.urlencode({ "cnsToDelete" : username + '|' })

    try:
        intermedia_connect = intermedia_connector.open("https://%s/asp/User/MSExchange/DeleteMailboxes.asp?action=delete&chargeOptions=" % (configdict[accountname]["MANAGERURL"]), _deletemailbox)

        if re.findall(r"has been deleted successfully",intermedia_connect.read()):
            pass
        else:
            __handleError('deleteMailbox', 'Could not Delete Mailbox')

    except Exception, e:
        __handleError('deleteMailbox', e)
    if debug:
        __writeDebug(debuglog, 'left deleteMailbox function in intermediamodule with accountname ' + accountname)
# }}}

def deleteContact(accountname, contact): # {{{
    """delete Contacts from your Account
    accountname: Accountname to establish the connectoin
    contact: name or cn attribute of the Contact you want to delete
    """
    accountname = 'IM_' + accountname

    if debug:
        __writeDebug(debuglog, 'joined deleteContact function in intermediamodule with accountname ' + accountname + ' and contact ' + contact)

    _deletemailbox = urllib.urlencode({ "items" : contact })

    # get intermedia connector
    intermedia_connector = __login_multipart(accountname)

    try:
        intermedia_connect = intermedia_connector.open("https://%s/asp/User/MSExchange/Contacts.asp?filterName=displayName&filterValue=t&filterType=index&sortName=&sortOrder=&all=1&action=deleteItems" % (configdict[accountname]["MANAGERURL"]), _deletemailbox)

        if re.findall(r"has been deleted successfully",intermedia_connect.read()):
            pass
        else:
            __handleError('deleteContact', 'Could not Delete Contact')

    except Exception, e:
        __handleError('deleteContact', e)
    if debug:
        __writeDebug(debuglog, 'left deleteContact function in intermediamodule with accountname ' + accountname)
# }}}

def deleteMailinglist(accountname, mailinglist): # {{{
    """delete Mailinglists from your Account
    accountname: Accountname for the connection as in the configfile
    mailinglist: sAMAccountName of the Mailinglist to delete
    """
    accountname = 'IM_' + accountname

    if debug:
        __writeDebug(debuglog, 'joined deleteMailinglist function in intermediamodule with accountname ' + accountname + ' and mailinglist ' + mailinglist)

    deletemailinglist = urllib.urlencode({ 'items' : mailinglist })

    # setup intermedia connector
    intermedia_connector = __login_multipart(accountname)

    try:
        intermedia_connect = intermedia_connector.open("https://%s/asp/User/MSExchange/DistributionLists.asp?filterName=displayName&filterValue=t&filterType=index&sortName=&sortOrder=&all=1&action=deleteItems" % (configdict[accountname]["MANAGERURL"]), deletemailinglist)

        if re.findall(r"has been deleted successfully",intermedia_connect.read()):
            pass
        else:
            __handleError('deleteMailinglist', 'Could not Delete Mailinglist')

    except Exception, e:
        __handleError('deleteMailinglist', e)
    if debug:
        __writeDebug(debuglog, 'left deleteMailinglist function in intermediamodule with accountname ' + accountname)
# }}}

def changeMailinglistGeneral(accountname, changesdict): # {{{
    """do the changes in the "General" tab of the Group
    accountname: Accountname we need to use for connection
    changesdict: Dictionary with the Changes for the Mailinglist (group object)
    needed values are:
                      -> identity: sAMAccountName of the group object
    valid values are:
                      -> member: a list of Members of the group object
                                 these must be DNs seperated by \r\n
                      -> displayName: change the displayName of the group object
    """
    accountname = 'IM_' + accountname

    if debug:
        __writeDebug(debuglog, 'joined changeMailinglistGeneral function in intermediamodule with accountname ' + accountname + ' and changesdict ' + str(changesdict))

    # urlencode the changes
    intermedia_changes = urllib.urlencode(changesdict)

    # get intermedia connector
    intermedia_connector = __login_multipart(accountname)

    try:
        intermedia_connect = intermedia_connector.open("https://%s/asp/User/MSExchange/EditDistributionList/General.asp?action=saveChanges&" % (configdict[accountname]["MANAGERURL"]), intermedia_changes)
        if re.findall(r"were successfully saved",intermedia_connect.read()):
            pass
        else:
            __handleError('changeMailinglistGeneral', 'Could not apply changes')
    except Exception, e:
        __handleError('changeMailinglistGeneral', e)
    if debug:
        __writeDebug(debuglog, 'left changeMailinglistGeneral function in intermediamodule with accountname ' + accountname)
# }}}

def addMailinglistEmailAddresses(accountname, changesdict): # {{{
    """add Emailaddresses to a Mailinglist (group object)
    accountname: The Accountname to get the connection
    changesdict: Dictionary with the changes
    needed values:
                  -> identity: sAMAccountName of the group object
                  -> prefix: part BEFORE the @
                  -> domain: part AFTER the @
    """
    accountname = 'IM_' + accountname

    if debug:
        __writeDebug(debuglog, 'joined addMailinglistEmailAdresses function in intermediamodule with accountname ' + accountname + ' and changesdict ' + str(changesdict))

    # check if the needed values are present
    if 'identity' not in changesdict:
        __handleError('addMailinglistEmailAddresses','Missing value identity in changesdict')
    if 'prefix' not in changesdict:
        __handleError('addMailinglistEmailAddresses','Missing value prefix in changesdict')
    if 'domain' not in changesdict:
        __handleError('addMailinglistEmailAddresses','Missing value domain in changesdict')

    # urlencode the changesdict
    intermedia_changes = urllib.urlencode(changesdict)

    # get intermedia connector
    intermedia_connector = __login_multipart(accountname)

    try:
        intermedia_connect = intermedia_connector.open("https://%s/asp/User/MSExchange/EditDistributionList/EmailAddresses.asp?action=createAddress&" % (configdict[accountname]["MANAGERURL"]), intermedia_changes)
        if not re.findall(r"were successfully added to Distribution List",intermedia_connect.read()):
            __handleError('addMailinglistEmailAdresses', 'Could not apply changes')
    except Exception, e:
        __handleError('addMailinglistEmailAdresses', e)
    if debug:
        __writeDebug(debuglog, 'left addMailinglistEmailAdresses function in intermediamodule with accountname ' + accountname)
# }}}

def delMailinglistEmailAddresses(accountname, changesdict): # {{{
    """remove Emailaddresses from a Mailinglist (group object)
    accountname: The Accountname to establish the connection
    changesdict: Dictionary with the changes
    needed values: 
                  -> identity: sAMAccountName of the GroupObject
                  -> otherProxyAddress: Addresses to remove
    """
    accountname = 'IM_' + accountname

    if debug:
        __writeDebug(debuglog, 'joined delMailinglistEmailAddresses function in intermediamodule with accountname ' + accountname + ' and changesdict ' + str(changesdict))

    # check if needed values are present
    if 'identity' not in changesdict:
        __handleError('delMailinglistEmailAddresses','needed value identity not in changesdict')
    if 'otherProxyAddress' not in changesdict:
        __handleError('delMailinglistEmailAddresses','needed value identity not in changesdict')

    # urlencode the data
    intermedia_changes = urllib.urlencode(changesdict)

    # get intermedia connector
    intermedia_connector = __login_multipart(accountname)

    try:
        intermedia_connect = intermedia_connector.open("https://%s/asp/User/MSExchange/EditDistributionList/EmailAddresses.asp?action=deleteAddresses&" % (configdict[accountname]["MANAGERURL"]), intermedia_changes)
        if re.findall(r"were successfully removed from Distribution List",intermedia_connect.read()):
            pass
        else:
            __handleError('delMailinglistEmailAddress', 'Could not delete')
    except Exception, e:
        __handleError('delMailinglistEmailAddress', e)
    if debug:
        __writeDebug(debuglog, 'left dellMailinglistEmailAddress function in intermediamodule with accountname ' + accountname)
# }}}

def createMailboxBackup(accountname, mailboxdict): # {{{
    """create a PST file for a given Mailboxe
    accountname: The Accountname we need to use here
    mailboxdict: Dictionary of Values we need for backing up
    needed values:
                  -> backupname: filename of the backupfile
                  -> sAMAccountName : sAMAccountName of the userobject
                  -> displayName : displayName of the userobject
    """
    accountname = 'IM_' + accountname
    
    if debug:
        __writeDebug(debuglog, 'joined createMailboxBackup function in intermediamodule with accountname ' + accountname + ' and mailboxdict ' + str(mailboxdict))

    # check if the values are present first:
    if 'backupname' not in mailboxdict:
        __handleError('createMailboxBackup','Missing backupname in mailboxdict')
    if 'sAMAccountName' not in mailboxdict:
         __handleError('createMailboxBackup','Missing sAMAccountName in mailboxdict')
    if 'displayName' not in mailboxdict:
         __handleError('createMailboxBackup','Missing displayName in mailboxdict')

    # urlencode the dict
    backupform = urllib.urlencode({ 'noRestrictions0' : 'on', 'pstFileName0' : mailboxdict["backupname"], 'mailboxIdentities' : mailboxdict["sAMAccountName"], 'mailboxLegacyDN0' : '/o=ODEX002/ou=First Administrative Group/cn=Recipients/cn=' + mailboxdict["sAMAccountName"], 'mailboxDisplayName0' : mailboxdict["displayName"], 'isRemoved0' : '0', 'pstFileGuids' : '' })

    # get intermedia connector
    intermedia_connector = __login_multipart(accountname)

    try:
        intermedia_connect = intermedia_connector.open("https://%s/asp/User/PstManager/BackupMailboxes.asp?action=backupMailboxes&chargeOptions=" % (configdict[accountname]["MANAGERURL"]), backupform)

        if re.findall(r"The mailbox backup for ",intermedia_connect.read()):
            pass
        else:
            __handleError('createMailboxBackup', 'Could not Backup Mailbox')

    except Exception, e:
        __handleError('createMailboxBackup', e)
    if debug:
        __writeDebug(debuglog, 'left createMailboxBackup function in intermediamodule with accountname ' + accountname)
# }}}

def generatePassword(keylength=None): # {{{
    """Generate new Password
    keylength: length of the password
    returns the new password
    """
    if debug:
        __writeDebug(debuglog, 'joined generatePassword function in intermediamodule with keylength ' + str(keylength))

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
        __writeDebug(debuglog, 'left generatePassword function in intermediamdoule with a password')
    return generatePassword(keylength)
# }}}

# EOF
# vim:foldmethod=marker:autoindent:expandtab:tabstop=4
