import boto3
import wave
import os
import sys

def gen_recording(timestamp, trigger_name, trigger_severity):
    CHANNELS = 1 #Polly's output is a mono audio stream
    RATE = 8000 #Polly supports 16000Hz and 8000Hz output for PCM format
    OUTPUT_FILE_IN_WAVE = f"alert-{timestamp}.wav" #WAV format Output file  name
    FRAMES = []
    WAV_SAMPLE_WIDTH_BYTES = 2 # Polly's output is a stream of 16-bits (2 bytes) samples
    
    session = boto3.Session(
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION')
    )
    #Initializing Polly Client
    polly = session.client("polly")
    
    #Input text for conversion
    INPUT_FILE = open(f"/tmp/callalert/soundtext/alert-{timestamp}.txt","r")
    INPUT=INPUT_FILE.read()
    print(INPUT)
    #INPUT = "<speak>Hi! I'm Matthew. Hope you are doing well. This is a sample PCM to WAV conversion for SSML. I am a Neural voice and have a conversational style. </speak>" # Input in SSML
    
    WORD = "<speak>"
    try:
    	if WORD in INPUT: #Checking for SSML input
            #Calling Polly synchronous API with text type as SSML
    		response = polly.synthesize_speech(Text=INPUT, TextType="ssml", OutputFormat="pcm",VoiceId="Matthew", SampleRate="8000") #the input to sampleRate is a string value.
    	else:
    		 #Calling Polly synchronous API with text type as plain text
    		response = polly.synthesize_speech(Text=INPUT, TextType="text", OutputFormat="pcm",VoiceId="Matthew", SampleRate="8000")
    except (BotoCoreError, ClientError) as error:
        sys.exit(-1)
    
    #Processing the response to audio stream
    STREAM = response.get("AudioStream")
    FRAMES.append(STREAM.read())
    
    WAVEFORMAT = wave.open(f'/tmp/callalert/sounds/{OUTPUT_FILE_IN_WAVE}','wb')
    WAVEFORMAT.setnchannels(CHANNELS)
    WAVEFORMAT.setsampwidth(WAV_SAMPLE_WIDTH_BYTES)
    WAVEFORMAT.setframerate(RATE)
    WAVEFORMAT.writeframes(b''.join(FRAMES))
    WAVEFORMAT.close()
