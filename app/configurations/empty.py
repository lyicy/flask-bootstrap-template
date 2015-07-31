# generate your own secret key with:
#   os.random(40).encode('hex')
SECRET_KEY = '1234567890'

# The website title
TITLE = 'Flask Blog'

# A description tag for this website
META_DESCRIPTION = (
    'This is the personal blog of Martin Drohmann'
    )

# generate your own activation salt for hashing with:
#   os.random(15)
ACTIVATION_SALT = '\xe5\xdbhJ\xfaB\xd0\xd9\xf6\x02'

# Google might ask you to prove that you own your website, if you want to user
# their analysis tools.  Put the address of the website they want to access
# here:
GOOGLE_SITE_VERIFICATION = 'google123456789012.html'

# If you want to use the Google Tag Manager, put the GTM id here
GTM = None

# your contact email
CONTACT_EMAIL = ('email@address.com')

# information for social buttons
SOCIAL = {
    'facebook': {'url': '#'},
    'twitter': {'handle': 'example'},
    }

COPYRIGHT = '&copy; A.U. Thors 2015'

EMAIL_SIGNATURE = """
A.U. Thors

Read my stuff
"""


# vim:set ft=python sw=4 et spell spelllang=en:
