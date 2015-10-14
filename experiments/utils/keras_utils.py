from keras.models import model_from_json

def load_model(model_path, weights_path):
    json = open(model_path, 'r').read()
    model = model_from_json(json)
    model.load_weights(weights_path)
    return model
