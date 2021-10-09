# Improving the Ingredient Parser

Mealie uses Conditional Random Fields (CRFs) for parsing and processing ingredients. The model used for ingredients is based off a data set of over 100,000 ingredients from a dataset compiled by the New York Times. I believe that the model used is sufficient enough to handle most of the ingredients, therefore, more data to train the model won't necessarily help improve the model. 

## Improving The CRF Parser

To improve results with the model, you'll likely need to focus on improving the tokenization and parsing of the original string to aid the model in determine what the ingredient is. Datascience is not my forte, but I have done some tokenization to improve the model. You can find that code under `/mealie/services/parser_services/crfpp` along with some other utility functions to aid in the tokenization and processing of ingredient strings. 

The best way to test on improving the parser is to register additional test cases in  `/mealie/tests/unit_tests/test_crfpp_parser.py` and run the test after making changes to the tokenizer. Note that the test cases DO NOT run in the CI environment, therefore you will need to have CRF++ installed on your machine. If you're using a Mac the easiest way to do this is through brew.

When submitting a PR to improve the parser it is important to provide your test cases, the problem you were trying to solve, and the results of the changes you made. As the tests don't run in CI, not providing these details may delay your PR from being merged. 

## Alternative Parsers
Alternatively, you can register a new parser by fulfilling the `ABCIngredientParser` interface. Satisfying this single method interface allows us to register additional parsing strategies at runtime and gives the user several options when trying to parse a recipe. 


## Links
- [Pretrained Model](https://github.com/hay-kot/mealie-nlp-model)
- [CRF++ (Forked)](https://github.com/hay-kot/crfpp)

