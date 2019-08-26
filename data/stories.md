## greet
* greet
  - utter_greet

## say goodbye
* goodbye
  - utter_goodbye

## New Story

* greet
    - utter_greet
* inform_name{"person":"Ayas"}
    - utter_greet_name
    - utter_ask_mood
* mood_great
    - utter_happy
* goodbye
    - utter_goodbye

## New Story 1

* greet
    - utter_greet
* inform_name{"person":"Rifqi"}
    - utter_greet_name
    - utter_ask_mood
    - action_set_intents
* mood_unhappy
    - utter_cheer_up
    - utter_did_that_help
    - action_set_intents
* affirm
    - utter_happy
    - action_set_intents
* goodbye
    - utter_goodbye

## inform name
* ask_my_name
  - action_greet_name

## Experiment 1
* greet
    - utter_greet
* start_experiment
    - utter_start
* experiment
    - action_get_name
    - utter_experiment

## Experiment 2
* start_experiment
    - utter_start
* experiment
    - action_get_name
    - utter_experiment

## Calculator 1
* calculate{"listed":"1"}
    - action_calculate
    - action_set_intents
    - utter_result

## Calculator 2
* greet
    - utter_greet
* calculate{"listed":"1"}
    - action_calculate
    - action_set_intents
    - utter_result

## Get Intent Name
* curious_intent
    - action_get_intents

## Query to Wolfram Alpha
* query{"role":"Prime Minister","location":"jamaica"}
    - query_form
    - action_set_intents

## Query to Wolfram Alpha Pronoun
* query{"pronoun":"his","role":"wife"}
    - query_form
    - slot{"topic":"[Ayas Faikar]"}
* query{"pronoun":"her","role":"husband"}
    - query_form
    - slot{"topic":"[Melania Trump]"}

## Stop Query
* stop_query
    - utter_ok
    - reset_form

## New Story

    - slot{"role":"prime minister"}
    - slot{"location":"uk"}
    - slot{"requested_slot":null}
* query{"location":"Malaysia"}
    - query_form
    - slot{"role":"prime minister"}
    - slot{"location":"uk"}
    - slot{"location":"Malaysia"}
    - slot{"requested_slot":null}

## Story from conversation with me on July 25th 2019
* ask_weather{"weather_location":"Surabaya"}
    - weather_form
    - slot{"weather_location":"Surabaya"}
    - slot{"requested_slot":null}
* ask_weather{"weather_location":"Surabaya"}
    - weather_form
    - slot{"weather_location":"Surabaya"}
    - slot{"requested_slot":null}
* ask_weather{"weather_location":"Jakarta"}
    - weather_form
    - slot{"weather_location":"Jakarta"}
    - slot{"requested_slot":null}
* ask_weather{"weather_location":"Squidward"}
    - weather_form
    - slot{"weather_location":null}
    - slot{"requested_slot":"weather_location"}
* ask_weather{"weather_location":"Lombok"}
    - weather_form
    - slot{"weather_location":"Lombok"}
    - slot{"requested_slot":null}

## New Story
* ask_weather
    - weather_form
    - slot{"requested_slot":"weather_location"}
* ask_weather{"weather_location":"Surabaya"}
    - weather_form
    - slot{"weather_location":"Surabaya"}
    - slot{"requested_slot":null}
* ask_weather{"weather_location":"Jakarta"}
    - weather_form
    - slot{"weather_location":"Jakarta"}
    - slot{"requested_slot":null}
* ask_weather
    - utter_confirm_weather_location
* affirm
    - weather_form
    - slot{"weather_location":"Jakarta"}
    - slot{"requested_slot":null}
* ask_weather{"weather_location":"Squidward"}
    - weather_form
    - slot{"weather_location":null}
    - slot{"requested_slot":"weather_location"}
* ask_weather{"weather_location":"Lombok"}
    - weather_form
    - slot{"weather_location":"Lombok"}
    - slot{"requested_slot":null}

## New Story 2

* ask_weather
    - weather_form
    - slot{"requested_slot":"weather_location"}
* ask_weather{"weather_location":"Surabaya"}
    - weather_form
    - slot{"weather_location":"Surabaya"}
    - slot{"requested_slot":null}
* ask_weather
    - utter_confirm_weather_location
* affirm
    - weather_form
    - slot{"weather_location":"Surabaya"}
    - slot{"requested_slot":null}

## New Story 3

* ask_weather
    - weather_form
    - slot{"requested_slot":"weather_location"}
* ask_weather{"weather_location":"Jakarta"}
    - weather_form
    - slot{"weather_location":"Jakarta"}
    - slot{"requested_slot":null}
* ask_weather{"weather_location":"Squidward"}
    - weather_form
    - slot{"weather_location":"Jakarta"}
    - slot{"weather_location":null}
    - slot{"requested_slot":"weather_location"}
* ask_weather{"weather_location":"Malang"}
    - weather_form
    - slot{"weather_location":"Malang"}
    - slot{"requested_slot":null}
* ask_weather
    - utter_confirm_weather_location
* deny
    - utter_ask_weather_location
* ask_weather{"weather_location":"Kediri"}
    - slot{"requested_slot":"weather_location"}
    - weather_form
    - slot{"weather_location":"Kediri"}
    - slot{"requested_slot":null}