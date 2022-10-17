import re
from statistics import mean

from . import tokenizer


def joinLine(columns):
    return "\t".join(columns)


def unclump(s):
    """
    Replacess $'s with spaces. The reverse of clumpFractions.
    """
    return re.sub(r"\$", " ", s)


def getFeatures(token, index, tokens):
    """
    Returns a list of features for a given token.
    """
    length = len(tokens)

    return [
        ("I%s" % index),
        ("L%s" % lengthGroup(length)),
        ("Yes" if isCapitalized(token) else "No") + "CAP",
        ("Yes" if insideParenthesis(token, tokens) else "No") + "PAREN",
    ]


def singularize(word):
    """
    A poor replacement for the pattern.en singularize function, but ok for now.
    """

    units = {
        "cups": "cup",
        "tablespoons": "tablespoon",
        "teaspoons": "teaspoon",
        "pounds": "pound",
        "ounces": "ounce",
        "cloves": "clove",
        "sprigs": "sprig",
        "pinches": "pinch",
        "bunches": "bunch",
        "slices": "slice",
        "grams": "gram",
        "heads": "head",
        "quarts": "quart",
        "stalks": "stalk",
        "pints": "pint",
        "pieces": "piece",
        "sticks": "stick",
        "dashes": "dash",
        "fillets": "fillet",
        "cans": "can",
        "ears": "ear",
        "packages": "package",
        "strips": "strip",
        "bulbs": "bulb",
        "bottles": "bottle",
    }

    if word in units.keys():
        return units[word]
    else:
        return word


def isCapitalized(token):
    """
    Returns true if a given token starts with a capital letter.
    """
    return re.match(r"^[A-Z]", token) is not None


def lengthGroup(actualLength):
    """
    Buckets the length of the ingredient into 6 buckets.
    """
    for n in [4, 8, 12, 16, 20]:
        if actualLength < n:
            return str(n)

    return "X"


def insideParenthesis(token, tokens):
    """
    Returns true if the word is inside parenthesis in the phrase.
    """
    if token in ["(", ")"]:
        return True
    else:
        line = " ".join(tokens)
        return (
            re.match(r".*\(.*" + re.escape(token) + r".*\).*", line) is not None  # noqa: W605 - invalid dscape sequence
        )


def displayIngredient(ingredient):
    """
    Format a list of (tag, [tokens]) tuples as an HTML string for display.

        displayIngredient([("qty", ["1"]), ("name", ["cat", "pie"])])
        # => <span class='qty'>1</span> <span class='name'>cat pie</span>
    """

    return "".join(["<span class='{}'>{}</span>".format(tag, " ".join(tokens)) for tag, tokens in ingredient])


# HACK: fix this
def smartJoin(words):
    """
    Joins list of words with spaces, but is smart about not adding spaces
    before commas.
    """

    input = " ".join(words)

    # replace " , " with ", "
    input = input.replace(" , ", ", ")

    # replace " ( " with " ("
    input = input.replace("( ", "(")

    # replace " ) " with ") "
    input = input.replace(" )", ")")

    return input


def import_data(lines):
    """
    This thing takes the output of CRF++ and turns it into an actual
    data structure.
    """
    data = [{}]
    display = [[]]
    prevTag = None

    confidence_all = [{}]

    #
    # iterate lines in the data file, which looks like:
    #
    #   # 0.511035
    #   1/2       I1  L12  NoCAP  X  B-QTY/0.982850
    #   teaspoon  I2  L12  NoCAP  X  B-UNIT/0.982200
    #   fresh     I3  L12  NoCAP  X  B-COMMENT/0.716364
    #   thyme     I4  L12  NoCAP  X  B-NAME/0.816803
    #   leaves    I5  L12  NoCAP  X  I-NAME/0.960524
    #   ,         I6  L12  NoCAP  X  B-COMMENT/0.772231
    #   finely    I7  L12  NoCAP  X  I-COMMENT/0.825956
    #   chopped   I8  L12  NoCAP  X  I-COMMENT/0.893379
    #
    #   # 0.505999
    #   Black   I1  L8  YesCAP  X  B-NAME/0.765461
    #   pepper  I2  L8  NoCAP   X  I-NAME/0.756614
    #   ,       I3  L8  NoCAP   X  OTHER/0.798040
    #   to      I4  L8  NoCAP   X  B-COMMENT/0.683089
    #   taste   I5  L8  NoCAP   X  I-COMMENT/0.848617
    #
    # i.e. the output of crf_test -v 1
    #
    for line in lines:
        # blank line starts a new ingredient
        if line in ("", "\n"):
            data.append({})
            display.append([])
            prevTag = None

            confidence_all.append({})

        # ignore comments
        elif line[0] == "#":
            pass

        # otherwise it's a token
        # e.g.: potato \t I2 \t L5 \t NoCAP \t B-NAME/0.978253
        else:

            columns = re.split("\t", line.strip())
            token = columns[0].strip()

            # unclump fractions
            token = unclump(token)

            # turn B-NAME/123 back into "name"
            tag, confidence = re.split(r"/", columns[-1], 1)
            tag = re.sub(r"^[BI]\-", "", tag).lower()  # noqa: W605 - invalid dscape sequence

            # ====================
            # Confidence Getter
            if prevTag != tag:
                if confidence_all[-1].get(tag):
                    confidence_all[-1][tag].append(confidence)
                else:
                    confidence_all[-1][tag] = [confidence]
            else:
                if confidence_all[-1].get(tag):
                    confidence_all[-1][tag].append(confidence)
                else:
                    confidence_all[-1][tag] = [confidence]
            # ---- DISPLAY ----
            # build a structure which groups each token by its tag, so we can
            # rebuild the original display name later.

            if prevTag != tag:
                display[-1].append((tag, [token]))
                prevTag = tag

            else:
                display[-1][-1][1].append(token)
                #               ^- token
                #            ^---- tag
                #        ^-------- ingredient

            # ---- DATA ----
            # build a dict grouping tokens by their tag

            # initialize this attribute if this is the first token of its kind
            if tag not in data[-1]:
                data[-1][tag] = []

            # HACK: If this token is a unit, singularize it so Scoop accepts it.
            if tag == "unit":
                token = singularize(token)

            data[-1][tag].append(token)

    # reassemble the output into a list of dicts.
    output = [{k: smartJoin(tokens) for k, tokens in ingredient.items()} for ingredient in data if len(ingredient)]

    # Preclean Confidence
    for i, c in enumerate(confidence_all):
        avg_of_all = []
        for k, v in c.items():
            v = [float(x) for x in v]
            avg = round(mean(v), 2)
            avg_of_all.append(avg)
            confidence_all[i][k] = avg

        if avg_of_all:
            confidence_all[i]["average"] = round(mean(avg_of_all), 2)

    # Add the raw ingredient phrase
    for i, _ in enumerate(output):
        output[i]["input"] = smartJoin([" ".join(tokens) for _, tokens in display[i]])
        output[i]["confidence"] = confidence_all[i]

    return output


def export_data(lines):
    """Parse "raw" ingredient lines into CRF-ready output"""
    output = []
    for line in lines:
        line_clean = re.sub("<[^<]+?>", "", line)
        tokens = tokenizer.tokenize(line_clean)

        for i, token in enumerate(tokens):
            features = getFeatures(token, i + 1, tokens)
            output.append(joinLine([token] + features))
        output.append("")
    return "\n".join(output)
