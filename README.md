# Rasa-SparkNLPEntityExtractor Still WIP

## RASA
### Installation
you need Python 3.6 or below and just install RASA with pip
`pip install rasa-x --extra-index-url https://pypi.rasa.com/simple`

## Spark NLP
### Installation
1. Install Java JDK 8
2. Install pyspark and sparknlp with pip
`pip install pyspark
pip install sparknlp`

## How to Use It
1. Clone this repo
2. Export `components` folder so python can find it
`export PYTHONPATH=this_repo_path/components/:$PYTHONPATH`
3. Open `actions.py` and fill the api_key for Wolfram Alpha, Gender API, and Apixu
4. Download [wiki.id.vec](https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/wiki.id.vec) and move it to `components` folder
3. Train it with `rasa train`
4. Test it with `rasa shell` and in another terminal run `rasa run actions` to run the actions in action.py

## Issues
1. Still doesn't work, because `convert_to_rasa` function in `sparknlpmodule.py` has not completed yet
2. Why has not completed yet? I think it's because lack of training dataset in NLU.md so it still give low prediction and just output 'O' or no entity detected


