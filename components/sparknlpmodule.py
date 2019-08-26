# menjalankan spark nlp
import time

from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel, Pipeline

import sparknlp
from sparknlp.annotator import *
from sparknlp.common import *
from sparknlp.base import *

# membaca dataset dalam format yang terdapat di gambar
from sparknlp.training import CoNLL


class SparkNLPModule:
    def __init__(self):
        self.spark = (
            SparkSession.builder.appName("DL-NER")
            .master("local[*]")
            .config("spark.driver.memory", "8G")
            .config("spark.jars.packages", "JohnSnowLabs:spark-nlp:2.1.0")
            .config("spark.kryoserializer.buffer.max", "500m")
            .getOrCreate()
        )
        self.sc = self.spark.sparkContext
        self.ner_model = None

        self.conll = CoNLL(
            documentCol="document",
            sentenceCol="sentence",
            tokenCol="token",
            posCol="pos",
        )

    def train(self, training_data_path, glove_path):
        training_data = self.conll.readDataset(self.spark, training_data_path)

        glove = (
            WordEmbeddings()
            .setInputCols(["sentence", "token"])
            .setOutputCol("glove")
            .setEmbeddingsSource(glove_path, 300, 2)
        )

        nerTagger = (
            NerDLApproach()
            .setInputCols(["sentence", "token", "glove"])
            .setLabelColumn("label")
            .setOutputCol("ner")
            .setMaxEpochs(1)
            .setRandomSeed(0)
            .setVerbose(0)
        )

        converter = (
            NerConverter()
            .setInputCols(["sentence", "token", "ner"])
            .setOutputCol("ner_span")
        )

        finisher = (
            Finisher()
            .setInputCols(["sentence", "token", "ner", "ner_span"])
            .setIncludeMetadata(True)
        )

        ner_pipeline = Pipeline(stages=[glove, nerTagger, converter, finisher])

        print("Start fitting")
        started = time.time()
        self.ner_model = ner_pipeline.fit(training_data)
        traintime = time.time() - started
        print("Fitting is ended", traintime, " s")
        return self.ner_model
        # print(ner_model)

    def predict(self, model, txt):
        if not self.ner_model:
            self.ner_model = model
        # untuk melakukan prediksi dalam bentuk dataframe (menguji dataset berdasarkan model yang ada)
        prediction_data = self.spark.createDataFrame([[txt]]).toDF("text")

        # testing
        document = DocumentAssembler().setInputCol("text").setOutputCol("document")
        sentence = (
            SentenceDetector().setInputCols(["document"]).setOutputCol("sentence")
        )
        token = Tokenizer().setInputCols(["sentence"]).setOutputCol("token")
        prediction_pipeline = Pipeline(
            stages=[
                document,
                sentence,
                token,
                self.ner_model,  # model NER yang telah di-train sebelumnya
            ]
        )

        prediction_model = prediction_pipeline.fit(prediction_data)
        predicted_res = prediction_model.transform(prediction_data)
        # memperlihatkan hasilnya
        # predicted_res.show()
        # mengambil kolom 'finished_ner' untuk perbandingan dan mengukur akurasi
        finished_ner = predicted_res.select("finished_token", "finished_ner")
        rddl = finished_ner.rdd

        predicted = []
        # memasukkan hasil kolom 'finished_ner' dalam bentuk RDD ke list of list of string
        for x in rddl.collect():
            predicted.append(list(x))

        print(predicted)
        self.convert_to_rasa(predicted[0])

    def load_model(self, model_path):
        if model_path:
            sameModel = PipelineModel.read().load(model_path)
            return sameModel
        else:
            return None

    def convert_to_rasa(self, pred):
        """
        Clinton was the President of United States of America

        hasil masih seperti ini
        
        [['Clinton'], ['Clinton'], [], 
        ['United', 'States', 'of', 'America'], 
        ['United', 'States', 'of', 'America'], 
        ['United', 'States', 'of', 'America'], 
        ['United', 'States', 'of', 'America'], 
        ['United', 'States', 'of', 'America']]
        
        seharusnya

        [['Clinton','person'],
        ['President','role'],
        ['United', 'States', 'of', 'America','location']]

        person, role, location => entity

        yang diinginkan rasa, seperti ini

        [{"value":"Clinton",
                "start": 0,
                "end": 6,
                "entity": "person",
                "confidence": null,
                "extractor": "SparkNLPEntityExtractor"},
        {"value":"President",
                "start": 16,
                "end": 24,
                "entity": "person",
                "confidence": null,
                "extractor": "SparkNLPEntityExtractor"},

                ...dst
        ]
        
        """
        tokens = pred[0]
        entities = pred[1]

        prev_ent = None
        hasil = []
        value = []
        for i in range(len(tokens)):
            if entities[i] != "O":
                if prev_ent == None or prev_ent == entities[i]:
                    value.append(tokens[i])
                elif prev_ent != entities[i]:
                    prev_ent = entities[i]
                    value = []
            else:
                prev_ent = None
                value = []
            if value and value not in hasil:
                hasil.append(value)
        print("DEBUGGGG\n==============")
        print(hasil)

