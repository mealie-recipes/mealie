from mealie.http.encoding import jsonable_encoder


def jsonify(data):
    return jsonable_encoder(data)
