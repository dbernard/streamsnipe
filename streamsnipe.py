from __future__ import print_function

import json
import requests

CLIENT = 'rf2wbmqoul3ucilhakgswp9oki2jip'


def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
             "amzn1.ask.skill.705b55f4-b5ba-4e23-9fde-9271227e34fa"):
         raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    if intent_name == 'GetTopStreamersIntent':
        return get_top_streamers_response(intent)
    elif intent_name == 'GetFeaturedStreamersIntent':
        return get_featured_streamers_response(intent)
    elif intent_name == 'GetStreamersByGameIntent':
        return get_streamers_by_game_response(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        return get_unknown_intent_response()


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])


# --- RESPONSE BUILDERS


def handle_session_end_request():
    card_title = 'StreamSnipe Session Ended'
    speech_output = 'Enjoy!'
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def get_unknown_intent_response():
    session_attributes = {}
    card_title = "StreamSnipe"
    speech_output = "I'm sorry, I'm not sure what you're asking for."
    reprompt_text = "I'm sorry, I'm not sure what you're asking for. Try again."

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_welcome_response():
    session_attributes = {}
    card_title = "StreamSnipe"
    speech_output = "Ask me if your favorite streamer is online or for the " \
                    "top streamers playing your favorite game."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Ask me if your favorite streamer is online or for the " \
                    "top streamers playing your favorite game."

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_streamers_by_game_response(intent):
    card_title = 'Top Streamers by Game'
    session_attributes = {}
    reprompt_text = None
    should_end_session = True

    if 'Game' in intent['slots']:
        game = intent['slots']['Game']['value']
        streamers = get_streamers_by_game(game)

        if streamers:
            s = ', '.join(streamers)
            speech_output = 'The top {} streamers are {}.'.format(game, s)
        else:
            speech_output = 'I couldn\'t find anyone streaming {} right now.'.format(game)

        reprompt_text = 'Ask me who is streaming your favorite game.'
    else:
        speech_output = 'Sorry, I\'m not sure what you\'re looking for. Please '\
                        'ask again.'
        reprompt_text = speech_output

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_featured_streamers_response(intent):
    card_title = 'Featured Streamers'
    session_attributes = {}
    reprompt_text = 'Ask me who the featured streamers are right now.'
    should_end_session = True

    streamers = get_featured_streamers()
    if streamers:
        s = ', '.join(streamers)
        speech_output = 'The featured streamers right now are {}'.format(s)
    else:
        speech_output = 'It doesn\'t look like there are any featured '\
                        'streamers at the moment.'

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_top_streamers_response(intent):
    card_title = 'Top Streamers'
    session_attributes = {}
    reprompt_text = 'Ask me who the top streamers are right now.'
    should_end_session = True

    streamers = get_top_streamers()
    if streamers:
        s = ', '.join(streamers)
        speech_output = 'The top streamers right now are {}'.format(s)
    else:
        speech_output = 'It doesn\'t look like there are any top '\
                        'streamers at the moment.'

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --- TWITCH API CALLS

def get_streamers_by_game(game):
    headers = {'Accept': 'application/vnd.twitchtv.v3+json',
               'Client-ID': CLIENT}

    url = 'https://api.twitch.tv/kraken/search/streams?query={}'.format(game)
    r = requests.get(url, headers=headers)

    r.raise_for_status()
    resp = json.loads(r.text)

    top = []
    if resp['streams']:
        try:
            streams = sorted(resp['streams'], key=lambda k: k['viewers'], reverse=True)

            top = [k['channel']['display_name'] for k in streams[:5]]
        except AttributeError:
            # Stream JSON has been proven unreliable. Ignore nameless/gameless
            # results.
            pass

    return top


def get_featured_streamers():
    headers = {'Accept': 'application/vnd.twitchtv.v3+json',
               'Client-ID': CLIENT}

    url = 'https://api.twitch.tv/kraken/streams/featured'
    r = requests.get(url, headers=headers)

    r.raise_for_status()
    resp = json.loads(r.text)

    feat = []
    for stream in resp['featured']:
        try:
            name = stream['stream']['channel']['display_name'].encode('utf-8')
            game = stream['stream']['channel']['game'].encode('utf-8')
            feat.append('{} playing {}'.format(name, game))
        except AttributeError:
            # Stream JSON has been proven unreliable. Ignore nameless/gameless
            # results.
            pass

    return feat


def get_top_streamers():
    headers = {'Accept': 'application/vnd.twitchtv.v3+json',
               'Client-ID': CLIENT}

    url = 'https://api.twitch.tv/kraken/streams'
    r = requests.get(url, headers=headers)

    r.raise_for_status()
    resp = json.loads(r.text)

    top = []
    if resp['streams']:
        try:
            streams = sorted(resp['streams'], key=lambda k: k['viewers'], reverse=True)

            top = ['{} playing {}'.format(k['channel']['display_name'].encode('utf-8'),
                                      k['channel']['game'].encode('utf-8')) for k in streams[:5]]
        except AttributeError:
            # Stream JSON has been proven unreliable. Ignore nameless/gameless
            # results.
            pass

    return top


def _get_stream_name(stream):
    if stream:
        return stream['channel']['display_name'].lower()

    return None


def _get_stream_viewers(stream):
    if stream:
        return stream['viewers']

    return None


def _get_stream_game(stream):
    if stream:
        return stream['game']

    return None


if __name__ == '__main__':
    #print(get_streamers_by_game('overwatch'))

    #print(get_top_streamers())

    print(get_featured_streamers())
