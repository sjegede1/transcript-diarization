import azure.cognitiveservices.speech as speechsdk

def speech_diarization(audio_file, subscription_key, region):
    # Set up the speech configuration
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
    
    # Enable diarization
    speech_config.output_format = speechsdk.OutputFormat.Detailed
    speech_config.speech_recognition_language="en-US"
    speech_config.set_property(property_id=speechsdk.PropertyId.SpeechServiceResponse_DiarizeIntermediateResults, value='true')
    speech_config.request_word_level_timestamps()
    
    print("CONFIG Properties -------> START")
    print(speech_config.get_property(speechsdk.PropertyId.SpeechServiceResponse_DiarizeIntermediateResults))
    print("---------------> END")

    # Create the audio configuration
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file)

    # Create a recognizer with the given configurations
    speech_recognizer = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)

    done = False

    def stop_cb(evt):
        """callback that stops continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_transcribing_async()
        nonlocal done
        done = True
    

    def handle_final_result(evt):
        print("Final result: ------------> START")
        result_data = {
            "Text": evt.result.text,
            "Offset": evt.result.offset/10E6,
            "Duration": evt.result.duration/10E6,
            "SpeakerId": evt.result.speaker_id
        }
        print(result_data)
        print("Final result: ------------> END")
        transcripts_collection.insert_one(result_data)
        print("Saved to MongoDB🍃")

    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.transcribing.connect(lambda evt: print(f'Recognizing: {evt.result.text}'))
    speech_recognizer.transcribed.connect(handle_final_result)
    speech_recognizer.session_started.connect(lambda evt: print(f'Session Started: {evt}'))
    speech_recognizer.canceled.connect(lambda evt: print(f'CANCELED: {evt}'))
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_transcribing_async()

    while not done:
        pass

    return
