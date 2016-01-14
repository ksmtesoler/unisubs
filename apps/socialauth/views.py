from django.shortcuts import render_to_response, redirect
from django.contrib import messages
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout

from auth.backends import OpenIdBackend
from socialauth.models import AuthMeta
from socialauth.forms import EditProfileForm
from thirdpartyaccounts.models import TwitterAccount

"""
from socialauth.models import YahooContact, TwitterContact, FacebookContact,\
                            SocialProfile, GmailContact
"""

from openid_consumer.views import begin
from socialauth.lib import oauthtwitter2 as oauthtwitter
from socialauth.lib.facebook import get_facebook_signature

from oauth import oauth
from datetime import datetime
from django.utils.http import urlquote
from utils.translation import get_user_languages_from_cookie
from auth.models import UserLanguage

TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', '')
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', '')

def get_url_host(request):
# FIXME: Duplication
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    host = request.get_host()
    return '%s://%s' % (protocol, host)

def login_page(request):
    payload = {'fb_api_key':settings.FACEBOOK_API_KEY,}
    return render_to_response('socialauth/login_page.html', payload, RequestContext(request))

def twitter_login(request, next=None):
    callback_url = None
    if next is not None:
        callback_url = '%s%s?next=%s' % \
            (get_url_host(request),
             reverse("socialauth_twitter_login_done"),
             urlquote(next))
    twitter = oauthtwitter.TwitterOAuthClient(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    request_token = twitter.fetch_request_token(callback_url)
    request.session['request_token'] = request_token.to_string()
    signin_url = twitter.authorize_token_url(request_token)
    return HttpResponseRedirect(signin_url)

def twitter_login_done(request):
    request_token = request.session.get('request_token', None)
    oauth_verifier = request.GET.get("oauth_verifier", None)

    # If there is no request_token for session,
    # Means we didn't redirect user to twitter
    if not request_token:
        # Redirect the user to the login page,
        # So the user can click on the sign-in with twitter button
        return HttpResponse("We didn't redirect you to twitter...")

    token = oauth.OAuthToken.from_string(request_token)

    # If the token from session and token from twitter does not match
    #   means something bad happened to tokens
    if token.key != request.GET.get('oauth_token', 'no-token'):
        del request.session['request_token']

        if request.GET.get('denied', None) is not None:
            messages.info(request, "Twitter authorization cancelled.")
            return redirect('profiles:account')

        messages.error(request, "Something wrong! Tokens do not match...")
        # Redirect the user to the login page
        return redirect('auth:login')

    twitter = oauthtwitter.TwitterOAuthClient(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    access_token = twitter.fetch_access_token(token, oauth_verifier)

    request.session['access_token'] = access_token.to_string()

    if request.session.get('no-login', False):
        # The user is trying to link a Twitter account to their Amara account.
        if not request.user.is_authenticated():
            messages.error(request, 'You must be logged in.')
            return redirect('auth:login')

        try:
            from socialauth.lib.oauthtwitter import OAuthApi
            twitter = OAuthApi(TWITTER_CONSUMER_KEY,
                                TWITTER_CONSUMER_SECRET, access_token)
            userinfo = twitter.GetUserInfo()
        except Exception, e:
            # TODO: Raise something more useful here
            raise e

        username = userinfo.screen_name

        try:
            account = TwitterAccount.objects.get(username=username)
            if request.user.pk != account.user.pk:
                messages.error(request, 'Account already linked')
                return redirect('profiles:account')

        except TwitterAccount.DoesNotExist:
            TwitterAccount.objects.create(user=request.user,
                    username=username, access_token=access_token.to_string())

        del request.session['no-login']
        messages.info(request, 'Successfully linked a Twitter account')
        return redirect('profiles:account')

    request.session['access_token'] = access_token.to_string()
    user = authenticate(access_token=access_token)

    # if user is authenticated then login user
    if user:
        if not user.userlanguage_set.exists():
            langs = get_user_languages_from_cookie(request)
            for l in langs:
                UserLanguage.objects.get_or_create(user=user, language=l)
        login(request, user)
    else:
        # We were not able to authenticate user
        # Redirect to login page
        del request.session['access_token']
        del request.session['request_token']
        return HttpResponseRedirect(reverse('socialauth_login_page'))

    # authentication was successful, use is now logged in
    return HttpResponseRedirect(request.GET.get('next', settings.LOGIN_REDIRECT_URL))

def openid_login(request):
    if 'openid_identifier' in request.GET:
        user_url = request.GET.get('openid_identifier')
        request.session['openid_provider'] = user_url
        return begin(request, user_url = user_url)
    else:
        if 'google.com' in request.POST.get('openid_url', ''):
            request.session['openid_provider'] = 'Google'
            return begin(request, user_url='https://www.google.com/accounts/o8/id')
        elif 'yahoo.com' in request.POST.get('openid_url', ''):
            request.session['openid_provider'] = 'Yahoo'
        else:
            request.session['openid_provider'] = 'Openid'
        return begin(request)

def gmail_login(request):
    request.session['openid_provider'] = 'Google'
    return begin(request, user_url='https://www.google.com/accounts/o8/id')

def udacity_login(request, confirmed=True):
    request.session['openid_provider'] = 'Udacity'
    return begin(request, user_url='https://www.udacity.com/openid/server', confirmed=confirmed)

def gmail_login_complete(request):
    pass

def yahoo_login(request):
    request.session['openid_provider'] = 'Yahoo'
    return begin(request, user_url='http://yahoo.com/')

def openid_done(request, provider=None, confirmed=True):
    """
    When the request reaches here, the user has completed the Openid
    authentication flow. He has authorised us to login via Openid, so
    request.openid is populated.
    After coming here, we want to check if we are seeing this openid first time.
    If we are, we will create a new Django user for this Openid, else login the
    existing openid.
    """
    if not provider:
        provider = request.session.get('openid_provider', '')
    if  request.openid:
        #check for already existing associations
        openid_key = str(request.openid)
        #authenticate and login
        if not confirmed and not OpenIdBackend.pre_authenticate(openid_key=openid_key, request=request, provider=provider) and provider == 'Udacity':
            return redirect('auth:confirm_create_user', 'udacity')
        user = authenticate(openid_key=openid_key, request=request, provider=provider)
        if user:
            if not user.userlanguage_set.exists():
                langs = get_user_languages_from_cookie(request)
                for l in langs:
                    UserLanguage.objects.get_or_create(user=user, language=l)

            login(request, user)
            next = None
            if 'openid_next' in request.session:
                next = request.session.get('openid_next')
            if 'next' in request.GET:
                next = request.GET['next']
            if next is not None and len(next.strip()) >  0 :
                return HttpResponseRedirect(next)
            redirect_url = reverse('profiles:profile', args=(user,))
            return HttpResponseRedirect(redirect_url)
        else:
            return HttpResponseRedirect(settings.LOGIN_URL)
    else:
        return HttpResponseRedirect(settings.LOGIN_URL)

def facebook_login_done(request):
    API_KEY = settings.FACEBOOK_API_KEY
    API_SECRET = settings.FACEBOOK_SECRET_KEY
    REST_SERVER = 'http://api.facebook.com/restserver.php'
    # FB Connect will set a cookie with a key == FB App API Key if the user has been authenticated
    if API_KEY in request.COOKIES:
        signature_hash = get_facebook_signature(API_KEY, API_SECRET, request.COOKIES, True)
        # The hash of the values in the cookie to make sure they're not forged
        # AND If session hasn't expired
        if(signature_hash == request.COOKIES[API_KEY]) and (datetime.fromtimestamp(float(request.COOKIES[API_KEY+'_expires'])) > datetime.now()):
            #Log the user in now.
            user = authenticate(cookies=request.COOKIES)
            if user:
                # if user is authenticated then login user
                login(request, user)
                return HttpResponseRedirect(reverse('socialauth_signin_complete'))
            else:
                #Delete cookies and redirect to main Login page.
                del request.COOKIES[API_KEY + '_session_key']
                del request.COOKIES[API_KEY + '_user']
                return HttpResponseRedirect(reverse('socialauth_login_page'))
    return HttpResponseRedirect(reverse('socialauth_login_page'))

def openid_login_page(request):
    return render_to_response('openid/index.html', {}, RequestContext(request))

def signin_complete(request):
    payload = {}
    return render_to_response('socialauth/signin_complete.html', payload, RequestContext(request))

@login_required
def editprofile(request):
    if request.method == 'POST':
        edit_form = EditProfileForm(user=request.user, data=request.POST)
        if edit_form.is_valid():
            user = edit_form.save()
            try:
                user.authmeta.is_profile_modified = True
                user.authmeta.save()
            except AuthMeta.DoesNotExist:
                pass
            if user.openidprofile_set.all().count():
                openid_profile = user.openidprofile_set.all()[0]
                openid_profile.is_valid_username = True
                openid_profile.save()
            try:
                #If there is a profile. notify that we have set the username
                profile = user.get_profile()
                profile.is_valid_username = True
                profile.save()
            except:
                pass
            request.user.message_set.create(message='Your profile has been updated.')
            return HttpResponseRedirect('.')
    if request.method == 'GET':
        edit_form = EditProfileForm(user = request.user)

    payload = {'edit_form':edit_form}
    return render_to_response('socialauth/editprofile.html', payload, RequestContext(request))

def social_logout(request):
    # Todo
    # still need to handle FB cookies, session etc.

    # let the openid_consumer app handle openid-related cleanup
    from openid_consumer.views import signout as oid_signout
    oid_signout(request)

    # normal logout
    logout_response = logout(request)

    if getattr(settings, 'LOGOUT_REDIRECT_URL', None):
        return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
    else:
        return logout_response
