import logging
import os
import typing
from typing import Any, Dict, List, Optional, Text, Tuple

from rasa.nlu.config import InvalidConfigError, RasaNLUModelConfig
from rasa.nlu.extractors import EntityExtractor
from rasa.nlu.model import Metadata
from rasa.nlu import utils
from rasa.nlu.training_data import Message, TrainingData
from rasa.nlu.components import Component

# from pyspark.ml import PipelineModel, Pipeline

import json

from sparknlpmodule import SparkNLPModule

MODEL_DIR = "sparknlp_ner_extractor"
"""
export PYTHONPATH=/Users/ayas/Documents/KP/Chatbot/CustomComponents/name_bot/components/:$PYTHONPATH
"""


class SparkNLPEntityExtractor(EntityExtractor):
    provides = ["entities"]
    requires = []
    defaults = {}

    def __init__(self, component_config: Text = None, model=None) -> None:
        super(SparkNLPEntityExtractor, self).__init__(component_config)
        self.sparknlp = SparkNLPModule()
        self.ner_model = self.sparknlp.load_model(model)

    def train(self, training_data, cfg, **kwargs):
        """Train this component."""
        # print(training_data.as_json())

        dir_path = os.path.dirname(os.path.realpath(__file__))

        training_data.persist(dir_name=dir_path)
        self.convert_json_conll(
            dir_path + "/training_data.json", dir_path + "/train_data.train"
        )

        self.ner_model = self.sparknlp.train(
            dir_path + "/train_data.train", dir_path + "/wiki.id.vec"
        )

        # print(json.dumps(training_data.training_examples))
        # self.sparknlp = SparkNLPModule("wiki.id.vec")

    def convert_json_conll(self, input_data, output="train_data.train"):
        f = open(output, "w+")
        print("-DOCSTART- -X- -X- O\n", file=f)
        DATA = []
        with open(input_data) as json_file:
            data = json.load(json_file)
            DATA = data["rasa_nlu_data"]["common_examples"]

        for datum in DATA:
            isi_text = []
            idx = []
            text = datum["text"]
            if "entities" not in datum:
                token = "O"
            else:
                for ent in datum["entities"]:
                    if ent["entity"] == "":
                        token = "O"
                    else:
                        token = ent["entity"]
                    idx.append([ent["start"], ent["end"], token])
            entity = {}
            begin = 0
            print("Index : ", idx)
            if not idx:
                isi_text.append([text])
            else:
                for index in idx:
                    start = index[0]
                    end = index[1]
                    label = index[2]

                    if start != begin:
                        starter = [text[begin : start - 1]]
                        isi_text.append(starter)

                    ent = [text[start:end]]
                    entity = {label: ent}
                    isi_text.append(entity)
                    begin = end + 1
                ender = [text[end:]]
                isi_text.append(ender)
            print(isi_text)
            for content in isi_text:
                print("content:", content)
                if isinstance(content, dict):
                    for key, value in content.items():
                        for val in value:
                            for valsplit in val.split(" "):
                                print(valsplit, "O", str(key), str(key), file=f)
                else:
                    splitted = str(content[0])
                    splitted = splitted.split(" ")
                    for spl in splitted:
                        spl = spl.strip()
                        if spl == "":
                            continue
                        print(spl, "O", "O", "O", file=f)
            print("\n")
            print("", file=f)

        f.close()

    def process(self, message, **kwargs):
        """Retrieve the tokens of the new message, pass it to the classifier
            and append prediction results to the message class."""
        if not self.ner_model:
            # component is either not trained or didn't
            # receive enough training data
            # self.ner_model = PipelineModel.read().load(extractor_file)
            entity = None
        else:
            print(
                "DEBUGGGG\n==============\n"
                + str(message.as_dict())
                + "\n==============="
            )
            """{'intent': {'name': None, 'confidence': 0.0}, 'entities': [], 'text': 'hello'}"""
            self.sparknlp.predict(self.ner_model, message.text)

            # entity = self.convert_to_rasa(sentiment, confidence)
            entity = "TESSSS"

        message.set("entities", [entity], add_to_output=True)

    def persist(self, file_name, model_dir):
        """Persist this model into the passed directory."""
        extractor_dir = os.path.join(model_dir, MODEL_DIR)
        self.ner_model.write().overwrite().save(extractor_dir)
        # utils.json_pickle(extractor_dir, self.sparknlp)
        return {"extractor_dir": MODEL_DIR}

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir=None,
        model_metadata=None,
        cached_component=None,
        **kwargs
    ):
        dir_name = meta.get("extractor_dir")
        extractor_dir = os.path.join(model_dir, dir_name)
        return cls(meta, extractor_dir)

