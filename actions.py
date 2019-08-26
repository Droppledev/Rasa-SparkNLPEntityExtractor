# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Union

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction, AllSlotsReset
from rasa_sdk.forms import FormAction
from typing import Dict, Text, Any, List, Union, Optional
import requests, pprint
import json
import re

intents = []


class ActionGreetName(Action):
    def name(self) -> Text:
        return "action_greet_name"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        person = tracker.get_slot("person")
        if person:
            string = "Your name is " + str(person)
            dispatcher.utter_message(string)
        else:
            dispatcher.utter_template("utter_ask_name", tracker)

        return []


class ActionGetName(Action):
    def name(self) -> Text:
        return "action_get_name"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        a_list = []
        ent = tracker.latest_message["entities"]
        for z in ent:
            a_list.append(z["value"])
            dispatcher.utter_message(z["value"])
        # tracker.slots['number'] = a_list
        return [SlotSet("listed", a_list)]


class ActionCalculate(Action):
    def name(self) -> Text:
        return "action_calculate"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        if not tracker.slots["listed"]:
            res = 0
        else:
            res = tracker.slots["listed"]

        count = 0
        ent = tracker.latest_message["entities"]
        for z in ent:
            if count == 0 and z["entity"] == "number":
                res = z["value"]
                res = int(res)
            elif z["entity"] == "operator":
                if z["value"] == "plus":
                    added = ent[count + 1]["value"]
                    res += int(added)
                elif z["value"] == "minus":
                    minused = ent[count + 1]["value"]
                    res -= int(minused)
            count += 1
            # dispatcher.utter_message(z['value'])
            # dispatcher.utter_message(z['entity'])

        return [SlotSet("listed", res)]


class ActionSetIntents(Action):
    def name(self) -> Text:
        return "action_set_intents"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        intent = tracker.latest_message["intent"].get("name")
        intents.append(intent)
        return []


class ActionGetIntents(Action):
    def name(self) -> Text:
        return "action_get_intents"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        for z in intents:
            dispatcher.utter_message(z)

        return []


class FormActionParent(FormAction):
    def name(self) -> Text:
        pass

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        pass

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        pass

    def get_wolfram_data(self, query: Text) -> Dict:
        url = "http://api.wolframalpha.com/v2/query?input="
        api_key = "your_api_key"
        po_titles = ["Result", "Image"]
        output = "json"

        final_url = url + query.strip() + "&appid=" + api_key + "&output=" + output

        for item in po_titles:
            final_url = final_url + "&podtitle=" + item

        r = requests.get(final_url).text
        qr = json.loads(r)
        return qr

    def extract_values(self, obj, key) -> List:
        """Pull all values of specified key from nested JSON."""
        arr = []

        def extract(obj, arr, key) -> List:
            """Recursively search for values of key in JSON tree."""
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        extract(v, arr, key)
                    elif k == key:
                        arr.append(v)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item, arr, key)
            return arr

        results = extract(obj, arr, key)
        return results

    def get_gender(self, name: Text) -> Text:
        first = name.split(" ")[0]
        print(first)
        url = "https://gender-api.com/get?name=" + first.strip()
        api_key = "your_api_key"
        final_url = url + "&key=" + api_key
        r = requests.get(final_url).text
        gender = json.loads(r)["gender"]
        return gender


class QueryForm(FormActionParent):
    def name(self) -> Text:
        return "query_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["role", "location"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:

        return {
            "role": [self.from_entity(entity="role", intent="query")],
            "location": [self.from_entity(entity="location", intent="query")],
            "pronoun": [self.from_entity(entity="pronoun", intent="query")],
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        temp = {"his": [], "her": []}
        refer = ""

        # get slots
        topic = tracker.slots["topic"]
        pronoun = tracker.slots["pronoun"]
        locat = tracker.slots["location"]
        role = tracker.slots["role"]

        # get topic if exists
        if topic:
            temp = topic
        """
        {
            'intent': {
                'name': 'query',
                'confidence': 0.9659770727157593
            },
            'entities': ,
            'intent_ranking': ,
            'text': 'who is the prime minister of Japan'
        }
        """
        print(str(temp))
        if pronoun and temp:
            if (pronoun == "her" and temp["her"]) or (pronoun == "his" and temp["his"]):
                # change name from pronoun in "topic" slot
                # if len(temp[pronoun]) > 1:
                #     dispatcher.utter_message("Did you mean :")
                #     for target in temp[pronoun][-3:]:
                #         dispatcher.utter_message(target)
                #     return [
                #         SlotSet("pronoun", None),
                #         FollowupAction("confirm_name"),
                #         SlotSet("listed", temp[pronoun][-3]),
                #     ]
                # else:
                refer = temp[pronoun][-1]
            else:
                dispatcher.utter_message("I don't know the context of " + pronoun)
                return []

        elif not role and not locat:
            dispatcher.utter_message("I don't know the context of " + pronoun)
            return []

        if refer and pronoun:
            msg = str(refer).strip() + "+" + str(role).strip()
            temp1, temp2 = role, refer
        else:
            msg = str(role).strip() + "+" + str(locat).strip()
            temp1, temp2 = role, locat
        # dispatcher.utter_message(txt)

        # get data from Wolfram Alpha
        qr = self.get_wolfram_data(msg)

        # Extract data
        try:
            result = self.extract_values(qr, "plaintext")[0]
            if result == "(data not available)":
                raise Exception
        except Exception as _:
            dispatcher.utter_message("Sorry, I can't find " + temp1 + " of " + temp2)
            return []

        # Send image
        img = self.extract_values(qr, "src")
        if len(img) > 1:
            dispatcher.utter_image_url(img[-1])

        # Split multiple data separated by | and get the last
        res_list = []
        name_list = []
        if "|" in str(result):
            if str(role) == "child":
                for datum in str(result).split("|"):
                    res_list.append(datum.strip())
                    name_list.append(datum.strip())
            else:
                res = str(result).split("|")[-1].strip()
                res_list.append(res)
                name = re.sub(r"\(.*", "", res).strip()
                name_list.append(name)
        else:
            res_list.append(str(result).strip())
            name = re.sub(r"\(.*", "", result).strip()
            name_list.append(name)

        for name in name_list:
            # get gender so we can overwrite the topic
            gender = self.get_gender(name)

            if not re.match(r"\d", name):
                if gender == "male":
                    pronoun = "his"
                else:
                    pronoun = "her"
                if name not in temp[pronoun]:
                    temp[pronoun].append(name)

                if len(temp[pronoun]) > 3:
                    temp[pronoun].pop(0)

        # print(str(qr))
        for res in res_list:
            dispatcher.utter_message(res)

        return [SlotSet("topic", temp), SlotSet("pronoun", None)]


class ResetForm(Action):
    def name(self) -> Text:
        return "reset_form"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        return [AllSlotsReset()]


class ConfirmName(FormActionParent):
    def name(self) -> Text:
        return "confirm_name"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["choice"]

    def validate_choice(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        """Validate choice value."""

        list_choices = tracker.slots["listed"]
        choice = tracker.slots["choice"]
        if choice in list_choices:
            return [SlotSet("choice", choice)]
        else:
            return [SlotSet("choice", None)]

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Text:

        topic = tracker.slots["topic"]
        temp = {"his": [], "her": []}
        if topic:
            temp = topic

        choice = tracker.slots["choice"]
        role = tracker.slots["role"]
        msg = str(choice) + " " + str(role)

        dispatcher.utter_message("ニャン")
        return []

class WeatherForm(FormAction):
    """Example of a custom form action"""

    # def __init__(self):
    #     self.condition = None
    #     self.degree = None

    def name(self) -> Text:
        """Unique identifier of the form"""
        return "weather_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["weather_location"]

    def validate_weather_location(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        """Validate location value."""

        from apixu.client import ApixuClient

        cur_loc = tracker.get_slot("weather_location")
        dispatcher.utter_message(str(cur_loc))
        api_key = "your_api_key"
        client = ApixuClient(api_key=api_key, lang="en")
        try:
            current = client.current(q=value)
            self.condition = current["current"]["condition"]["text"]
            self.degree = current["current"]["temp_c"]
            dispatcher.utter_message(str(self.condition)+str(self.degree))
            return {"weather_location": value}
        except Exception as e:
            dispatcher.utter_template("utter_no_location", tracker)
            return {"weather_location": None}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        loc = tracker.get_slot("weather_location")
        dispatcher.utter_message(str(loc))

        cur_int = tracker.latest_message.get("intent").get("name")
        cur_ent = tracker.latest_message.get("entities")
        # if (len(tracker.events)>5):
        #     two_last = tracker.events[-5]
        # dispatcher.utter_message(cur_int + " " + str(cur_ent))
        # dispatcher.utter_message(str(two_last))

        if cur_int == "ask_weather" and not cur_ent:
            dispatcher.utter_template("utter_confirm_weather_location", tracker)
            return []
        elif cur_int == "deny":
            dispatcher.utter_template("utter_ask_weather_location", tracker)
            return []

        msg = (
            "Weather in "
            + str(loc)
            + " is "
            + str(self.condition)
            + " with "
            + str(self.degree)
            + " Celcius"
        )

        dispatcher.utter_message(msg)

        return []


class WeatherForm(FormAction):
    """Example of weather form"""
    def name(self) -> Text:
        """Unique identifier of the form"""
        return "weather_form"
    
    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:

        return {
            "weather_location": [self.from_entity(entity="weather_location", intent="ask_weather")],
        }

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["weather_location"]

    def get_weather(self, location: Text) -> Dict:
        from apixu.client import ApixuClient

        api_key = "da0041cd4e0a4ddbaef73702191507"
        client = ApixuClient(api_key=api_key, lang="en")
        try:
            current = client.current(q=location)
            return current
        except Exception as e:
            return None

    def validate_weather_location(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
        """Validate weather_location value."""

        data = self.get_weather(value)

        if data:
            print("Validated and data is there")
            self.condition = data["current"]["condition"]["text"]
            self.degree = data["current"]["temp_c"]
            self.loc = value
            return {"weather_location": value}
        else:
            dispatcher.utter_template("utter_no_weather_location", tracker)
            return {"weather_location": None}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        cur_int = tracker.latest_message.get("intent").get("name")
        cur_ent = tracker.latest_message.get("entities")

        if cur_int == "ask_weather" and not cur_ent:
            dispatcher.utter_template("utter_confirm_weather_location", tracker)
            return []
        elif cur_int == "deny":
            dispatcher.utter_template("utter_ask_weather_location", tracker)
            return []

        msg = (
            "Weather in "
            + str(self.loc)
            + " is "
            + str(self.condition)
            + " with "
            + str(self.degree)
            + " Celcius"
        )

        dispatcher.utter_message(msg)

        return []
