# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 05:38:14 2022

@author: Doug
"""

import datasets
from tqdm import tqdm

_CITATION = """
@inproceedings{balasuriya-etal-2009-named,
    title = "Named Entity Recognition in Wikipedia",
    author = "Balasuriya, Dominic  and
      Ringland, Nicky  and
      Nothman, Joel  and
      Murphy, Tara  and
      Curran, James R.",
    booktitle = "Proceedings of the 2009 Workshop on The People{'}s Web Meets {NLP}: 
    Collaboratively Constructed Semantic Resources (People{'}s Web)",
    month = aug,
    year = "2009",
    address = "Suntec, Singapore",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/W09-3302",
    pages = "10--18",
}
"""

_LICENCE = "CC-BY 4.0"

_DESCRIPTION = """
WikiGold dataset.
"""

#Batch_Name_Variable = 'wikigold_train'

#_TRAINING = (
#    f"H:\My Files\School\Grad School WLU\MRP\Research\Files\Data\Textfiles\80_10_10\{Batch_Name_Variable}.txt"
#)


_TRAINING = (
    "H:\\My Files\\School\\Grad School WLU\\MRP\\Research\\Files\\Data\\Textfiles\\Rule_0.1\\SIS\\100\\v3_Augmented.txt")

_TESTING = (
    "H:\\My Files\\School\\Grad School WLU\\MRP\\Research\\Files\\Data\\Textfiles\\Article\\100\\v3_Testing.txt")

_VALIDATING = (
    "H:\\My Files\\School\\Grad School WLU\\MRP\\Research\\Files\\Data\\Textfiles\\Article\\100\\v3_UnAugmented.txt")

# the label ids
NER_TAGS_DICT = {
    "O": 0,
    "PER": 1,
    "LOC": 2,
    "ORG": 3,
    "MISC": 4,
}

NER_BIO_TAGS_DICT = {
    "O": 0,
    "B-PER": 1,
    "I-PER": 2,
    "B-LOC": 3,
    "I-LOC": 4,
    "B-ORG": 5,
    "I-ORG": 6,
    "B-MISC": 7,
    "I-MISC": 8
}


class WikiGoldConfig(datasets.BuilderConfig):
    """BuilderConfig for WikiGold"""

    def __init__(self, **kwargs):
        """BuilderConfig for WikiGold.
        Args:
          **kwargs: keyword arguments forwarded to super.
        """
        super(WikiGoldConfig, self).__init__(**kwargs)


class WikiGold(datasets.GeneratorBasedBuilder):
    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "id": datasets.Value("string"),
                    "tokens": datasets.features.Sequence(datasets.Value("string")),
                    "ner_tags": datasets.features.Sequence(
                        datasets.features.ClassLabel(
                            names=["O", "PER", "LOC", "ORG", "MISC"]
                        )
                    ),
                    "ner_bio_tags": datasets.features.Sequence(
                        datasets.features.ClassLabel(
                            names=["O", "B-PER", "I-PER", "B-LOC", "I-LOC", 
                            "B-ORG", "I-ORG", "B-MISC", "I-MISC"]
                        )
                    ),
                }
            ),
            supervised_keys=None,
            citation=_CITATION,
            license=_LICENCE,
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        training = dl_manager.download_and_extract(_TRAINING)
        testing = dl_manager.download_and_extract(_TESTING)
        validating = dl_manager.download_and_extract(_VALIDATING)
        return [
            datasets.SplitGenerator(name=datasets.Split.TRAIN,gen_kwargs={"filepath": training},),
            datasets.SplitGenerator(name=datasets.Split.VALIDATION,gen_kwargs={"filepath": validating},),
            datasets.SplitGenerator(name=datasets.Split.TEST,gen_kwargs={"filepath": testing},),
        ]

    def _generate_examples(self, filepath=None):
        num_lines = sum(1 for _ in open(filepath, encoding="utf-8"))
        id = 0

        with open(filepath, "r", encoding="utf-8") as f:
            tokens, ner_tags, ner_bio_tags = [], [], []
            for line in tqdm(f, total=num_lines):
                line = line.strip().split()

                if line:
                    assert len(line) == 2
                    token, ner_tag = line

                    if token == "-DOCSTART-":
                        continue
                    
                    tokens.append(token)
                    ner_bio_tags.append(ner_tag)
                    if ner_tag != "O":
                        ner_tag = ner_tag.split("-")[1]                  
                    ner_tags.append(NER_TAGS_DICT[ner_tag])

                elif tokens:
                    # organize a record to be written into json
                    record = {
                        "tokens": tokens,
                        "id": str(id),
                        "ner_tags": ner_tags,
                        "ner_bio_tags": ner_bio_tags,
                    }
                    tokens, ner_tags = [], []
                    id += 1
                    yield record["id"], record

            # take the last sentence
            if tokens:
                record = {
                    "tokens": tokens,
                    "id": str(id),
                    "ner_tags": ner_tags,
                    "ner_bio_tags": ner_bio_tags,
                }
                yield record["id"], record