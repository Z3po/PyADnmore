PyADnmore
=========

PyADnmore is a Python Module Collection for Administration use.

I wrote those Modules because of Basic Tasks like changing Active Directory Passwords. While using Linux i was always in the need of logging into the Server directly.
It's just as bad using Intermedia as Exchange Provider. You are always in the need of logging into their Portal to do any changes. Not anymore!
It also helped to automate a lot of processes because you can easily use the Modules to for example bulk-create users.

Example Usage:
--------------

    from PyADnmore import admodule
    
    DN = admodule.getUsers('DOMAIN','Max Mustermann')[0][0]
    
    new_pass = admodule.generatePassword()
    
    admodule.changePassword('DOMAIN',DN,new_pass)
    
    print 'Password of user ' + DN + ' changed to ' + new_pass

___

    from PyADnmore import admodule
    
    for users in admodule.getEntryByAttribute('DOMAIN','(!(extensionAttribute5))')
        print users[0]
        admodule.modifyObject('DOMAIN',users[0],{ 'extensionAttribute5' : users[1]['givenName'][0][0] + users[1]['sn'][0] })
    
___

    from PyADnmore import intermediamodule
    
    for user in intermediamodule.getUsers('DOMAIN','*'):
        if not 'givenName' in user[1]:
            print 'Missing Given Name at user ' + user[1]['sAMAccountName'][0]
